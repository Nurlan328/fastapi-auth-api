"""Утилита: сделать пользователя админом.

Проблема «первого админа»: эндпоинт /admin/* доступен только админу,
но как создать самого первого? Через прямой доступ к БД — этим скриптом.

Запуск:
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
            print(f"Пользователь '{username}' не найден.")
            return
        users.set_role(user, "admin")
        print(f"Готово: '{username}' теперь admin.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python make_admin.py <username>")
        sys.exit(1)
    make_admin(sys.argv[1])
