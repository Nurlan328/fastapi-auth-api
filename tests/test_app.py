"""Тесты Auth API. Запуск: pytest -v"""
import models


# --- маленькие помощники, чтобы не дублировать код в каждом тесте ---
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


# --- регистрация ---
def test_register_success(client):
    r = register(client)
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "alice"
    assert data["role"] == "user"            # по умолчанию обычный пользователь
    assert "hashed_password" not in data     # пароль/хеш наружу не утекают


def test_register_duplicate(client):
    register(client)
    r = register(client)                     # тот же username -> ошибка
    assert r.status_code == 400


# --- логин ---
def test_login_success(client):
    register(client)
    token = login(client)
    assert token                             # токен не пустой


def test_login_wrong_password(client):
    register(client)
    r = client.post("/auth/login", data={"username": "alice", "password": "WRONG"})
    assert r.status_code == 401


# --- защищённый /users/me ---
def test_me_requires_token(client):
    r = client.get("/users/me")
    assert r.status_code == 401              # без токена нельзя


def test_me_with_token(client):
    register(client)
    token = login(client)
    r = client.get("/users/me", headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["username"] == "alice"


# --- ролевой доступ /admin ---
def test_admin_forbidden_for_regular_user(client):
    register(client)
    token = login(client)
    r = client.get("/admin/users", headers=auth_header(token))
    assert r.status_code == 403              # залогинен, но не админ


def test_admin_allowed_for_admin(client, session_factory):
    register(client, username="alice")
    register(client, username="bob")

    # делаем alice админом напрямую в тестовой БД (как это делает make_admin.py)
    db = session_factory()
    alice = db.query(models.User).filter(models.User.username == "alice").first()
    alice.role = "admin"
    db.commit()
    db.close()

    token = login(client, username="alice")
    r = client.get("/admin/users", headers=auth_header(token))
    assert r.status_code == 200
    assert len(r.json()) == 2                # alice и bob


# --- rate limiting (Redis) ---
def test_login_rate_limited(client):
    register(client)
    # лимит = 5 запросов в минуту. Первые 5 проходят (тут — неверный пароль -> 401).
    for _ in range(5):
        r = client.post("/auth/login", data={"username": "alice", "password": "WRONG"})
        assert r.status_code == 401
    # 6-й запрос блокируется ещё ДО проверки пароля -> 429
    r = client.post("/auth/login", data={"username": "alice", "password": "WRONG"})
    assert r.status_code == 429


# --- caching (Redis) ---
def test_stats_cache(client, session_factory):
    register(client, username="alice")
    # делаем alice админом, чтобы пустили в /admin/stats
    db = session_factory()
    db.query(models.User).filter(models.User.username == "alice").first().role = "admin"
    db.commit()
    db.close()

    token = login(client, username="alice")
    headers = auth_header(token)

    r1 = client.get("/admin/stats", headers=headers)
    assert r1.status_code == 200
    assert r1.json()["source"] == "db"       # первый раз — из БД
    assert r1.json()["total_users"] == 1

    r2 = client.get("/admin/stats", headers=headers)
    assert r2.json()["source"] == "cache"    # второй раз — из кеша


# --- фоновые задачи / очередь (RabbitMQ) ---
def test_register_publishes_email(client, email_outbox):
    assert email_outbox == []                # пока никто не регистрировался
    register(client, username="alice")
    # после регистрации в «очередь» должно лечь ровно одно письмо
    assert len(email_outbox) == 1
    assert email_outbox[0] == {"to": "alice@example.com", "username": "alice"}


def test_failed_register_publishes_nothing(client, email_outbox):
    register(client, username="alice")
    email_outbox.clear()
    # повторная регистрация с тем же именем -> 400, письмо НЕ должно отправиться
    r = register(client, username="alice")
    assert r.status_code == 400
    assert email_outbox == []
