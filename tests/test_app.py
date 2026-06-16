"""Tests for the Auth API. Run: pytest -v"""
import models


# --- small helpers to avoid duplicating code in every test ---
def register(client, username="alice", password="secret123"):
    return client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )


def login(client, username="alice", password="secret123"):
    r = client.post("/auth/login", data={"username": username, "password": password})
    return r.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# --- registration ---
def test_register_success(client):
    r = register(client)
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "alice"
    assert data["role"] == "user"            # a regular user by default
    assert "hashed_password" not in data     # the password/hash never leaks out


def test_register_duplicate(client):
    register(client)
    r = register(client)                     # same username -> error
    assert r.status_code == 400


# --- login ---
def test_login_success(client):
    register(client)
    token = login(client)
    assert token                             # token is not empty


def test_login_wrong_password(client):
    register(client)
    r = client.post("/auth/login", data={"username": "alice", "password": "WRONG"})
    assert r.status_code == 401


# --- protected /users/me ---
def test_me_requires_token(client):
    r = client.get("/users/me")
    assert r.status_code == 401              # no token, no access


def test_me_with_token(client):
    register(client)
    token = login(client)
    r = client.get("/users/me", headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["username"] == "alice"


# --- role-based access /admin ---
def test_admin_forbidden_for_regular_user(client):
    register(client)
    token = login(client)
    r = client.get("/admin/users", headers=auth_header(token))
    assert r.status_code == 403              # logged in, but not an admin


def test_admin_allowed_for_admin(client, session_factory):
    register(client, username="alice")
    register(client, username="bob")

    # make alice an admin directly in the test DB (like make_admin.py does)
    db = session_factory()
    alice = db.query(models.User).filter(models.User.username == "alice").first()
    alice.role = "admin"
    db.commit()
    db.close()

    token = login(client, username="alice")
    r = client.get("/admin/users", headers=auth_header(token))
    assert r.status_code == 200
    assert len(r.json()) == 2                # alice and bob


# --- background tasks / queue (RabbitMQ) ---
def test_register_publishes_email(client, email_outbox):
    assert email_outbox == []                # nobody registered yet
    register(client, username="alice")
    # after registration exactly one email should land in the "queue"
    assert len(email_outbox) == 1
    assert email_outbox[0] == {"to": "alice@example.com", "username": "alice"}


def test_failed_register_publishes_nothing(client, email_outbox):
    register(client, username="alice")
    email_outbox.clear()
    # duplicate registration with the same username -> 400, no email should be sent
    r = register(client, username="alice")
    assert r.status_code == 400
    assert email_outbox == []


# --- rate limiting (Redis) ---
def test_login_rate_limited(client):
    register(client)
    # limit = 5 per minute. The first 5 pass through (here — wrong password -> 401).
    for _ in range(5):
        r = client.post("/auth/login", data={"username": "alice", "password": "WRONG"})
        assert r.status_code == 401
    # the 6th request is blocked BEFORE the password check -> 429
    r = client.post("/auth/login", data={"username": "alice", "password": "WRONG"})
    assert r.status_code == 429


# --- caching (Redis) ---
def test_stats_cache(client, session_factory):
    register(client, username="alice")
    # make alice an admin so she's allowed into /admin/stats
    db = session_factory()
    db.query(models.User).filter(models.User.username == "alice").first().role = "admin"
    db.commit()
    db.close()

    token = login(client, username="alice")
    headers = auth_header(token)

    r1 = client.get("/admin/stats", headers=headers)
    assert r1.status_code == 200
    assert r1.json()["source"] == "db"       # first time — from the DB
    assert r1.json()["total_users"] == 1

    r2 = client.get("/admin/stats", headers=headers)
    assert r2.json()["source"] == "cache"    # second time — from the cache
