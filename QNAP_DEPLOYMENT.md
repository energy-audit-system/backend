# Миграция Backend на QNAP NAS TS-433

**Дата**: 2026-01-09
**Целевое устройство**: QNAP NAS TS-433
**Метод**: Docker через Container Station (рекомендуется)

---

## Содержание

1. [Подготовка QNAP NAS](#1-подготовка-qnap-nas)
2. [Вариант A: Развертывание через Docker (рекомендуется)](#вариант-a-docker-рекомендуется)
3. [Вариант B: Прямая установка через SSH](#вариант-b-прямая-установка)
4. [Миграция базы данных](#миграция-базы-данных)
5. [Настройка автозапуска](#настройка-автозапуска)
6. [Тестирование](#тестирование)
7. [Troubleshooting](#troubleshooting)

---

## 1. Подготовка QNAP NAS

### 1.1 Включение SSH

1. Войдите в веб-интерфейс QNAP (обычно `http://<IP_адрес>:8080`)
2. Перейдите в **Control Panel** → **Telnet / SSH**
3. Включите **Allow SSH connection**
4. Установите порт (по умолчанию 22)
5. Нажмите **Apply**

### 1.2 Подключение по SSH

```bash
# Подключитесь к NAS
ssh admin@<IP_адрес_NAS>
# Или ваш созданный пользователь
ssh <ваш_пользователь>@<IP_адрес_NAS>

# Проверьте систему
uname -a
cat /etc/issue
```

### 1.3 Создание рабочей директории

```bash
# Создайте директорию для проекта
# Обычно /share/Container или /share/homes/<user>
mkdir -p /share/Container/energy-audit-backend
cd /share/Container/energy-audit-backend
```

### 1.4 Установка Container Station

1. В веб-интерфейсе QNAP перейдите в **App Center**
2. Найдите **Container Station**
3. Нажмите **Install**
4. Дождитесь установки

**Проверка установки Docker:**
```bash
ssh admin@<IP_адрес_NAS>
docker --version
docker-compose --version
```

---

## Вариант A: Docker (рекомендуется)

### Шаг 1: Создание Dockerfile

Создайте файл `Dockerfile` на вашем локальном компьютере в папке проекта:

```dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование requirements
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Переменные окружения
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Открыть порт
EXPOSE 5000

# Команда запуска
CMD ["python", "run.py"]
```

### Шаг 2: Создание docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:14-alpine
    container_name: energy_audit_db
    restart: always
    environment:
      POSTGRES_DB: energy_audit
      POSTGRES_USER: asattorov
      POSTGRES_PASSWORD: neda2020luba
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - energy_audit_network

  # Backend API
  backend:
    build: .
    container_name: energy_audit_backend
    restart: always
    depends_on:
      - postgres
    environment:
      DATABASE_URI: postgresql://asattorov:neda2020luba@postgres:5432/energy_audit
      FLASK_ENV: production
      SECRET_KEY: ${SECRET_KEY:-neda2331}
    ports:
      - "5000:5000"
    volumes:
      - ./app:/app/app
      - ./logs:/app/logs
    networks:
      - energy_audit_network

volumes:
  postgres_data:
    driver: local

networks:
  energy_audit_network:
    driver: bridge
```

### Шаг 3: Обновление app/config.py для Docker

Измените `app/config.py` чтобы использовать переменные окружения:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        'postgresql://asattorov:neda2020luba@postgres:5432/energy_audit'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'neda2331')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRE_HOURS = 24
```

### Шаг 4: Создание .env файла

```bash
# Создайте .env файл
cat > .env << 'EOF'
DATABASE_URI=postgresql://asattorov:neda2020luba@postgres:5432/energy_audit
SECRET_KEY=замените_на_сильный_секретный_ключ
FLASK_ENV=production
EOF
```

### Шаг 5: Перенос на QNAP

**С вашего компьютера:**

```bash
# Вариант 1: Через SCP
scp -r /path/to/backend admin@<IP_NAS>:/share/Container/energy-audit-backend/

# Вариант 2: Через Git (если есть доступ к интернету на NAS)
ssh admin@<IP_NAS>
cd /share/Container
git clone <ваш_репозиторий_url> energy-audit-backend
cd energy-audit-backend
git checkout claude/learn-repo-4j7Nj
```

### Шаг 6: Запуск через Docker Compose

```bash
# Подключитесь к NAS
ssh admin@<IP_NAS>
cd /share/Container/energy-audit-backend

# Запустите контейнеры
docker-compose up -d

# Проверьте статус
docker-compose ps

# Посмотрите логи
docker-compose logs -f backend
```

### Шаг 7: Инициализация базы данных

```bash
# Подключитесь к контейнеру PostgreSQL
docker exec -it energy_audit_db psql -U asattorov -d energy_audit

# В psql выполните:
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS reports;
CREATE SCHEMA IF NOT EXISTS logs;
\q

# Примените миграции
docker exec -i energy_audit_db psql -U asattorov -d energy_audit < /docker-entrypoint-initdb.d/000_init.sql
docker exec -i energy_audit_db psql -U asattorov -d energy_audit < /docker-entrypoint-initdb.d/001_alter_report_history.sql
```

### Шаг 8: Проверка работы

```bash
# Проверьте API
curl http://<IP_NAS>:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test","email":"test@test.com","password":"pass123","role":"client"}'
```

---

## Вариант B: Прямая установка

Если не хотите использовать Docker:

### Шаг 1: Установка Python

```bash
ssh admin@<IP_NAS>

# Проверьте версию Python
python3 --version

# Если Python 3 не установлен, установите через Entware
# https://github.com/Entware/Entware/wiki/Install-on-QNAP-NAS
```

### Шаг 2: Установка PostgreSQL

**Через Container Station:**
1. Откройте Container Station
2. Create → Search "postgres"
3. Выберите **postgres:14-alpine**
4. Настройте:
   - Port: 5432
   - Environment variables:
     - POSTGRES_DB: energy_audit
     - POSTGRES_USER: asattorov
     - POSTGRES_PASSWORD: neda2020luba
5. Create

### Шаг 3: Установка приложения

```bash
ssh admin@<IP_NAS>

# Перейдите в рабочую директорию
cd /share/Container/energy-audit-backend

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Настройте config.py с правильным IP PostgreSQL
# Узнайте IP контейнера PostgreSQL:
docker inspect <postgres_container_id> | grep IPAddress

# Примените миграции
psql -h <postgres_ip> -U asattorov -d energy_audit -f database/000_init.sql
psql -h <postgres_ip> -U asattorov -d energy_audit -f database/001_alter_report_history.sql

# Запустите приложение
python run.py
```

---

## Миграция базы данных

### Если у вас уже есть данные в локальной БД

**На вашем компьютере:**

```bash
# 1. Создайте дамп базы данных
pg_dump -U asattorov -d energy_audit -F c -f energy_audit_backup.dump

# 2. Перенесите на NAS
scp energy_audit_backup.dump admin@<IP_NAS>:/share/Container/energy-audit-backend/
```

**На QNAP NAS:**

```bash
# Для Docker:
docker exec -i energy_audit_db pg_restore \
  -U asattorov -d energy_audit -v \
  < /share/Container/energy-audit-backend/energy_audit_backup.dump

# Или напрямую:
pg_restore -h localhost -U asattorov -d energy_audit -v energy_audit_backup.dump
```

---

## Настройка автозапуска

### Для Docker Compose

```bash
# Docker Compose автоматически перезапустит контейнеры
# благодаря "restart: always" в docker-compose.yml

# Проверка политики перезапуска:
docker inspect energy_audit_backend | grep -A 3 RestartPolicy
```

### Для прямой установки

Создайте скрипт автозапуска:

```bash
# Создайте скрипт
cat > /share/Container/energy-audit-backend/start.sh << 'EOF'
#!/bin/bash
cd /share/Container/energy-audit-backend
source venv/bin/activate
python run.py >> /share/Container/energy-audit-backend/logs/app.log 2>&1 &
EOF

chmod +x /share/Container/energy-audit-backend/start.sh

# Добавьте в автозагрузку QNAP
# Через веб-интерфейс: Control Panel → System → Hardware → Autorun
```

---

## Тестирование

### 1. Проверка подключения к базе данных

```bash
# Для Docker:
docker exec -it energy_audit_db psql -U asattorov -d energy_audit -c "\dt *.*"

# Прямое подключение:
psql -h <IP_NAS> -p 5432 -U asattorov -d energy_audit -c "\dt *.*"
```

### 2. Проверка API

```bash
# Регистрация
curl -X POST http://<IP_NAS>:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Тест Пользователь",
    "email": "test@example.com",
    "password": "password123",
    "role": "engineer"
  }'

# Логин
curl -X POST http://<IP_NAS>:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Запуск тестов

```bash
# Для Docker:
docker exec -it energy_audit_backend python test_logging.py

# Прямо:
ssh admin@<IP_NAS>
cd /share/Container/energy-audit-backend
source venv/bin/activate
python test_logging.py
```

---

## Настройка сети и безопасности

### Открытие портов через QNAP Firewall

1. **Control Panel** → **Security** → **Security Level**
2. Добавьте правило для порта 5000
3. Установите разрешенные IP адреса (если нужно)

### Настройка обратного прокси (опционально)

Для доступа через 80/443 порт настройте NGINX в QNAP:

1. Установите **Nginx** из App Center
2. Настройте reverse proxy:

```nginx
# /etc/nginx/sites-enabled/energy-audit
server {
    listen 80;
    server_name <your_domain_or_ip>;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## Мониторинг и логи

### Просмотр логов Docker

```bash
# Логи backend
docker logs -f energy_audit_backend

# Логи PostgreSQL
docker logs -f energy_audit_db

# Все логи
docker-compose logs -f
```

### Настройка ротации логов

Создайте `logrotate` конфигурацию:

```bash
cat > /etc/logrotate.d/energy-audit << 'EOF'
/share/Container/energy-audit-backend/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

---

## Backup стратегия

### Автоматический бэкап базы данных

```bash
# Создайте скрипт бэкапа
cat > /share/Container/energy-audit-backend/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/share/Container/energy-audit-backend/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап PostgreSQL
docker exec energy_audit_db pg_dump -U asattorov energy_audit | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Удалить бэкапы старше 30 дней
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /share/Container/energy-audit-backend/backup.sh

# Добавьте в cron (через SSH)
crontab -e
# Добавьте строку:
0 2 * * * /share/Container/energy-audit-backend/backup.sh
```

---

## Troubleshooting

### Проблема: Контейнеры не запускаются

```bash
# Проверьте логи
docker-compose logs

# Проверьте права доступа
ls -la /share/Container/energy-audit-backend

# Пересоздайте контейнеры
docker-compose down
docker-compose up -d --force-recreate
```

### Проблема: Не могу подключиться к PostgreSQL

```bash
# Проверьте работает ли контейнер
docker ps | grep postgres

# Проверьте сеть
docker network ls
docker network inspect energy_audit_network

# Проверьте порты
netstat -tulpn | grep 5432

# Проверьте подключение изнутри контейнера backend
docker exec -it energy_audit_backend sh
ping postgres
```

### Проблема: Ошибка "Permission denied"

```bash
# Измените владельца файлов
chown -R admin:administrators /share/Container/energy-audit-backend

# Проверьте права SELinux (если применимо)
ls -Z /share/Container/energy-audit-backend
```

### Проблема: Медленная работа

```bash
# Проверьте ресурсы
docker stats

# Увеличьте ресурсы для Container Station
# В веб-интерфейсе: Container Station → Preferences → Resources
```

---

## Обновление приложения

```bash
# На вашем компьютере: запушьте изменения в git
git push origin claude/learn-repo-4j7Nj

# На QNAP NAS:
ssh admin@<IP_NAS>
cd /share/Container/energy-audit-backend

# Получите изменения
git pull origin claude/learn-repo-4j7Nj

# Пересоберите и перезапустите
docker-compose down
docker-compose build
docker-compose up -d

# Проверьте
docker-compose ps
docker-compose logs -f backend
```

---

## Checklist развертывания

- [ ] Container Station установлен
- [ ] SSH доступ настроен
- [ ] Проект перенесен на NAS
- [ ] Docker Compose файл создан
- [ ] Контейнеры запущены
- [ ] Схемы БД созданы
- [ ] Миграции применены
- [ ] API тесты пройдены
- [ ] Автозапуск настроен
- [ ] Бэкапы настроены
- [ ] Логирование работает
- [ ] Firewall настроен
- [ ] Frontend может подключиться к API

---

## Полезные команды QNAP

```bash
# Узнать IP адрес NAS
ip addr show

# Проверить место на диске
df -h

# Проверить память
free -h

# Проверить запущенные процессы
top

# Проверить версию QTS
cat /etc/config/uLinux.conf | grep version

# Перезагрузить NAS
reboot
```

---

## Контакты и поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs -f`
2. Проверьте документацию QNAP: https://www.qnap.com/en/support/
3. Container Station guide: https://www.qnap.com/en/how-to/tutorial/article/container-station

---

**Последнее обновление**: 2026-01-09
