"""Utility: promote a user to admin.

The "first admin" problem: /admin/* endpoints are admin-only, but how do you
create the very first one? Through direct DB access — with this script.

Run:
    python make_admin.py alice
"""
import sys

from database import SessionLocal
from repositories.user_repository import UserRepository


def make_admin(username: str) -> None:
    db = SessionLocal()
    try:
        users = UserRepository(db)
        user = users.get_by_username(username)
        if user is None:
            print(f"User '{username}' not found.")
            return
        users.set_role(user, "admin")
        print(f"Done: '{username}' is now an admin.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <username>")
        sys.exit(1)
    make_admin(sys.argv[1])
