import json
import os


# Исправление 1: пароль берём из переменной окружения.
PASSWORD = os.getenv("APP_PASSWORD")


def find_user(connection, user_id):
    cursor = connection.cursor()

    # Исправление 2: параметризованный SQL-запрос.
    cursor.execute(
        "SELECT id, username FROM users WHERE id = ?",
        (user_id,)
    )

    return cursor.fetchone()


def parse_value(data):
    # Исправление 3: безопасная обработка JSON.
    return json.loads(data)
