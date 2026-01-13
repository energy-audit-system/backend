#!/usr/bin/env python3
"""
Генератор SQL с правильными хешами паролей для тестовых пользователей
Использование: python generate_test_users.py > insert_users.sql
"""

from werkzeug.security import generate_password_hash

# Пароль для всех тестовых пользователей
TEST_PASSWORD = "password123"

# Список тестовых пользователей
test_users = [
    # Инженеры
    {
        "full_name": "Иванов Иван Петрович",
        "email": "engineer1@example.com",
        "phone": "+7 (999) 111-22-33",
        "role": "engineer"
    },
    {
        "full_name": "Петрова Мария Александровна",
        "email": "engineer2@example.com",
        "phone": "+7 (999) 222-33-44",
        "role": "engineer"
    },
    {
        "full_name": "Сидоров Алексей Викторович",
        "email": "engineer3@example.com",
        "phone": "+7 (999) 333-44-55",
        "role": "engineer"
    },
    # Клиенты
    {
        "full_name": "Смирнов Дмитрий Олегович",
        "email": "client1@example.com",
        "phone": "+7 (999) 444-55-66",
        "role": "client"
    },
    {
        "full_name": "Кузнецова Елена Сергеевна",
        "email": "client2@example.com",
        "phone": "+7 (999) 555-66-77",
        "role": "client"
    },
    {
        "full_name": "Попов Андрей Николаевич",
        "email": "client3@example.com",
        "phone": "+7 (999) 666-77-88",
        "role": "client"
    },
    {
        "full_name": "Васильева Ольга Ивановна",
        "email": "client4@example.com",
        "phone": "+7 (999) 777-88-99",
        "role": "client"
    },
    # Администратор
    {
        "full_name": "Администратов Админ Админович",
        "email": "admin@example.com",
        "phone": "+7 (999) 000-00-00",
        "role": "admin"
    },
]

def generate_insert_statements():
    """Генерирует SQL INSERT с правильными хешами паролей"""

    print("-- Тестовые пользователи с паролем: password123")
    print("-- Сгенерировано автоматически")
    print()
    print("INSERT INTO auth.users (full_name, email, phone, password_hash, role, is_email_verified, email_verification_token) VALUES")

    statements = []
    for user in test_users:
        password_hash = generate_password_hash(TEST_PASSWORD)

        statement = f"('{user['full_name']}', '{user['email']}', '{user['phone']}', '{password_hash}', '{user['role']}', true, NULL)"
        statements.append(statement)

    print(",\n".join(statements) + ";")
    print()
    print(f"-- Всего пользователей: {len(test_users)}")
    print(f"-- Пароль для всех: {TEST_PASSWORD}")

if __name__ == "__main__":
    generate_insert_statements()
