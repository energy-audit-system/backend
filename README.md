# Energy Audit System - Backend

Бэкенд система для управления энергоаудитами предприятий.

## Технологии

- Python 3.x
- Flask
- PostgreSQL
- SQLAlchemy
- JWT Authentication

---

## Установка и запуск проекта

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd backend
```

### 2. Создание виртуального окружения

**На macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**На Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Установка и настройка PostgreSQL

#### Установка PostgreSQL

**На macOS (через Homebrew):**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**На Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**На Windows:**
Скачайте установщик с https://www.postgresql.org/download/windows/

#### Создание базы данных

```bash
# Войти в PostgreSQL
psql -U postgres

# В консоли PostgreSQL:
CREATE DATABASE energy_audit;
CREATE USER asattorov WITH PASSWORD 'neda2020luba';
GRANT ALL PRIVILEGES ON DATABASE energy_audit TO asattorov;
\q
```

**Важно:** Или измените настройки подключения в `app/config.py` под свои учётные данные.

### 5. Создание схем и таблиц

#### Вариант 1: Автоматическое создание через скрипт

```bash
# Сначала создайте схемы вручную
psql -U asattorov -d energy_audit -c "CREATE SCHEMA IF NOT EXISTS auth;"
psql -U asattorov -d energy_audit -c "CREATE SCHEMA IF NOT EXISTS core;"
psql -U asattorov -d energy_audit -c "CREATE SCHEMA IF NOT EXISTS reports;"
psql -U asattorov -d energy_audit -c "CREATE SCHEMA IF NOT EXISTS logs;"

# Затем примените начальную миграцию
psql -U asattorov -d energy_audit -f database/000_init.sql

# Примените миграцию для системы логирования
psql -U asattorov -d energy_audit -f database/001_alter_report_history.sql
```

#### Вариант 2: Через интерактивную консоль

```bash
psql -U asattorov -d energy_audit

# В консоли PostgreSQL выполните:
\i database/000_init.sql
\i database/001_alter_report_history.sql
\q
```

#### Проверка таблиц

```bash
psql -U asattorov -d energy_audit -c "\dt auth.*"
psql -U asattorov -d energy_audit -c "\dt core.*"
psql -U asattorov -d energy_audit -c "\dt reports.*"
psql -U asattorov -d energy_audit -c "\dt logs.*"
```

Вы должны увидеть:
- `auth.users`
- `core.business`
- `core.audit_orders`
- `reports.reports`
- `reports.files`
- `logs.report_history`

### 6. (Опционально) Заполнение тестовыми данными

```bash
python app/scripts/seed.py
```

### 7. Запуск сервера

```bash
python run.py
```

Сервер запустится на **http://localhost:5000**

Вы должны увидеть:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

---

## Тестирование API

### 1. Регистрация пользователя

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Тестовый Пользователь",
    "email": "test@example.com",
    "password": "password123",
    "role": "engineer"
  }'
```

**Ожидаемый ответ:**
```json
{
  "message": "Пользователь успешно зарегистрирован",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "full_name": "Тестовый Пользователь",
    "email": "test@example.com",
    "role": "engineer"
  }
}
```

### 2. Вход в систему

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Создание отчёта

```bash
# Сохраните токен из предыдущего ответа
TOKEN="your_jwt_token_here"

curl -X POST http://localhost:5000/reports/post_report \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "audit_order_id": 1,
    "data": {
      "energy_consumption": {
        "electricity": 120000,
        "gas": 60000
      }
    }
  }'
```

### 4. Обновление отчёта

```bash
# Замените <report_id> на ID из предыдущего шага
curl -X PATCH http://localhost:5000/reports/<report_id> \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "data": {
      "energy_consumption": {
        "electricity": 125000,
        "gas": 65000
      }
    }
  }'
```

### 5. Проверка истории изменений

```bash
psql -U asattorov -d energy_audit -c "SELECT * FROM logs.report_history ORDER BY created_at DESC LIMIT 5;"
```

Вы должны увидеть записи о создании и обновлении отчёта.

---

## Автоматическое тестирование системы логирования

После запуска сервера протестируйте систему логирования:

```bash
python test_logging.py
```

**Ожидаемый вывод:**
```
============================================================
Testing Report History Logging System
============================================================

1. Checking table structure...
✓ Table structure is correct (action_type, description, changes)

2. Creating test user...
✓ Created test user (ID: 1)

...

✓ All tests passed successfully!
============================================================
```

---

## Структура проекта

```
backend/
├── run.py                    # Точка входа - запуск Flask
├── requirements.txt          # Python зависимости
├── README.md                 # Эта инструкция
├── README_MIGRATION.md       # Инструкция по миграции на сервер
├── test_logging.py           # Тесты системы логирования
│
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Конфигурация
│   ├── db.py                # SQLAlchemy instance
│   │
│   ├── models/              # ORM модели
│   │   ├── user.py
│   │   ├── business.py
│   │   ├── audit_order.py
│   │   ├── report.py
│   │   ├── report_file.py
│   │   └── report_history.py
│   │
│   ├── routes/              # API endpoints
│   │   ├── auth.py
│   │   ├── audit_orders.py
│   │   └── reports_reports.py
│   │
│   ├── utils/               # Утилиты
│   │   ├── security.py      # JWT, password hashing
│   │   └── logging.py       # Система логирования изменений
│   │
│   └── scripts/
│       └── seed.py          # Заполнение тестовыми данными
│
├── database/
│   ├── 000_init.sql         # Начальная схема БД
│   └── 001_alter_report_history.sql  # Миграция системы логирования
│
└── docs/
    ├── API.md               # API документация (русский)
    └── claude.md            # Структура проекта для разработчиков
```

---

## Переменные окружения (опционально)

Создайте файл `.env` в корне проекта:

```env
# Database
DATABASE_URI=postgresql://asattorov:neda2020luba@localhost:5432/energy_audit

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
```

**Важно:** Не коммитьте `.env` файл в git (уже добавлен в `.gitignore`)

---

## Частые проблемы

### Ошибка подключения к PostgreSQL

```
psql: error: connection to server on socket failed
```

**Решение:**
```bash
# Убедитесь, что PostgreSQL запущен
# macOS:
brew services start postgresql@14

# Ubuntu/Debian:
sudo systemctl start postgresql

# Проверьте статус:
brew services list  # macOS
sudo systemctl status postgresql  # Linux
```

### Ошибка "permission denied for schema"

```
ERROR: permission denied for schema auth
```

**Решение:**
```bash
psql -U postgres -d energy_audit -c "GRANT ALL ON SCHEMA auth TO asattorov;"
psql -U postgres -d energy_audit -c "GRANT ALL ON SCHEMA core TO asattorov;"
psql -U postgres -d energy_audit -c "GRANT ALL ON SCHEMA reports TO asattorov;"
psql -U postgres -d energy_audit -c "GRANT ALL ON SCHEMA logs TO asattorov;"
```

### Ошибка "ModuleNotFoundError: No module named 'flask'"

**Решение:**
```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate  # macOS/Linux
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt
```

### Порт 5000 уже занят

**Решение:**
Измените порт в `run.py`:
```python
app.run(host="0.0.0.0", port=5001, debug=True)
```

---

## Полезные команды

### База данных

```bash
# Подключиться к БД
psql -U asattorov -d energy_audit

# Посмотреть все таблицы
\dt *.*

# Посмотреть структуру таблицы
\d logs.report_history

# Посмотреть данные
SELECT * FROM auth.users;
SELECT * FROM logs.report_history ORDER BY created_at DESC LIMIT 10;

# Выйти
\q
```

### Python

```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Деактивировать
deactivate

# Обновить зависимости
pip install -r requirements.txt --upgrade

# Добавить новую зависимость
pip install package_name
pip freeze > requirements.txt
```

### Git

```bash
# Переключиться на ветку разработки
git checkout claude/learn-repo-4j7Nj

# Получить последние изменения
git pull origin claude/learn-repo-4j7Nj

# Посмотреть статус
git status
```

---

## Документация

- **API документация**: См. `API.md` (на русском языке)
- **Структура проекта**: См. `claude.md`
- **Миграция на сервер**: См. `README_MIGRATION.md`

---

## Поддержка

При возникновении проблем обращайтесь к разработчику или создайте issue в репозитории.

---

**Последнее обновление:** 2026-01-09
