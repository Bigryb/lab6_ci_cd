PASSWORD = "lab_demo_password_123"


def find_user(connection, user_id):
    cursor = connection.cursor()

    # Уязвимость SQL Injection.
    cursor.execute(
        f"SELECT id, username FROM users WHERE id = {user_id}"
    )

    return cursor.fetchone()
