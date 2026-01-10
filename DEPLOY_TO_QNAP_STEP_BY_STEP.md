# Пошаговое развертывание на QNAP NAS TS-433

**IP вашего NAS**: `192.168.0.214`
**Пользователь**: `admin` (или `asattorov`)

---

## ✅ ШАГ 1: Подключение к NAS

**На вашем компьютере (PowerShell):**

```powershell
ssh admin@192.168.0.214
# Введите пароль админа
```

---

## ✅ ШАГ 2: Создание структуры директорий на БОЛЬШОМ диске

**В SSH терминале на NAS выполните:**

```bash
# Создайте папки на диске с 14TB свободного места
mkdir -p /share/CACHEDEV1_DATA/energy-audit/database
mkdir -p /share/CACHEDEV1_DATA/energy-audit/backend
mkdir -p /share/CACHEDEV1_DATA/energy-audit/logs

# Проверьте что создалось
ls -la /share/CACHEDEV1_DATA/energy-audit/
```

**Ожидаемый результат:**
```
drwxr-xr-x ... database
drwxr-xr-x ... backend
drwxr-xr-x ... logs
```

---

## ✅ ШАГ 3: Копирование проекта на NAS

### Вариант A: Через SCP (с вашего компьютера)

**Откройте НОВОЕ окно PowerShell (не закрывая SSH):**

```powershell
# Перейдите в папку проекта
cd D:\energo_audit_project_backend

# Скопируйте все файлы на NAS
scp -r * admin@192.168.0.214:/share/CACHEDEV1_DATA/energy-audit/backend/

# Также скопируйте скрытые файлы
scp .env.example admin@192.168.0.214:/share/CACHEDEV1_DATA/energy-audit/backend/
scp .dockerignore admin@192.168.0.214:/share/CACHEDEV1_DATA/energy-audit/backend/
```

### Вариант B: Через WinSCP (проще)

1. Скачайте WinSCP: https://winscp.net/eng/download.php
2. Подключитесь:
   - Protocol: SFTP
   - Host: `192.168.0.214`
   - User: `admin`
   - Password: (ваш пароль)
3. Слева: `D:\energo_audit_project_backend`
4. Справа: `/share/CACHEDEV1_DATA/energy-audit/backend/`
5. Перетащите все файлы из левой панели в правую

### Вариант C: Через Git (если есть доступ к GitHub с NAS)

**В SSH терминале:**

```bash
cd /share/CACHEDEV1_DATA/energy-audit
git clone https://github.com/energy-audit-system/backend.git backend
cd backend
git checkout claude/learn-repo-4j7Nj
```

---

## ✅ ШАГ 4: Проверка что файлы скопировались

**В SSH терминале:**

```bash
cd /share/CACHEDEV1_DATA/energy-audit/backend
ls -la

# Должны увидеть:
# - docker-compose.qnap.yml
# - Dockerfile
# - requirements.txt
# - run.py
# - app/
# - database/
# и другие файлы
```

---

## ✅ ШАГ 5: Создание .env файла

```bash
cd /share/CACHEDEV1_DATA/energy-audit/backend

# Создайте .env из примера
cat > .env << 'EOF'
POSTGRES_DB=energy_audit
POSTGRES_USER=asattorov
POSTGRES_PASSWORD=neda2020luba
POSTGRES_PORT=5432

BACKEND_PORT=5000
FLASK_ENV=production

SECRET_KEY=neda2331_CHANGE_THIS
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24
EOF

# Проверьте что создался
cat .env
```

---

## ✅ ШАГ 6: Запуск контейнеров

```bash
cd /share/CACHEDEV1_DATA/energy-audit/backend

# Запустите с использованием QNAP-специфичного файла
docker compose -f docker-compose.qnap.yml up -d

# Эта команда:
# 1. Скачает образы postgres:14-alpine и python:3.11-slim (1-3 минуты)
# 2. Установит зависимости Python
# 3. Запустит оба контейнера
```

**Следите за процессом:**

```bash
# Смотрите логи в реальном времени
docker compose -f docker-compose.qnap.yml logs -f

# Нажмите Ctrl+C чтобы выйти из просмотра логов (контейнеры продолжат работать)
```

**Ожидаемый вывод:**
```
[+] Running 3/3
 ✔ Network energy_audit_network       Created
 ✔ Container energy_audit_db          Started
 ✔ Container energy_audit_backend     Started
```

---

## ✅ ШАГ 7: Проверка статуса контейнеров

```bash
# Проверьте что оба контейнера запущены
docker compose -f docker-compose.qnap.yml ps

# Должны увидеть:
# energy_audit_db       Up (healthy)   5432/tcp
# energy_audit_backend  Up             5000/tcp
```

Если статус "Up" и "healthy" - отлично! Переходим дальше.

---

## ✅ ШАГ 8: Инициализация базы данных

**Подождите 30 секунд после запуска, затем:**

```bash
# 1. Создайте схемы
docker exec -it energy_audit_db psql -U asattorov -d energy_audit << 'EOF'
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS reports;
CREATE SCHEMA IF NOT EXISTS logs;
\q
EOF

# 2. Примените начальную миграцию
docker exec -i energy_audit_db psql -U asattorov -d energy_audit < /share/CACHEDEV1_DATA/energy-audit/backend/database/000_init.sql

# 3. Примените миграцию для системы логирования
docker exec -i energy_audit_db psql -U asattorov -d energy_audit < /share/CACHEDEV1_DATA/energy-audit/backend/database/001_alter_report_history.sql

# 4. Проверьте что таблицы созданы
docker exec -it energy_audit_db psql -U asattorov -d energy_audit -c "\dt *.*"
```

**Ожидаемый вывод (список таблиц):**
```
           Schema            |      Name        | Type  |   Owner
-----------------------------+------------------+-------+-----------
 auth                        | users            | table | asattorov
 core                        | business         | table | asattorov
 core                        | audit_orders     | table | asattorov
 reports                     | reports          | table | asattorov
 reports                     | files            | table | asattorov
 logs                        | report_history   | table | asattorov
```

---

## ✅ ШАГ 9: Тестирование API

### Тест 1: Проверка что backend отвечает

```bash
# Простой тест
curl http://192.168.0.214:5000/
```

### Тест 2: Регистрация пользователя

```bash
curl -X POST http://192.168.0.214:5000/auth/register \
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

### Тест 3: Логин

```bash
curl -X POST http://192.168.0.214:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Тест 4: Проверка логов

```bash
# Посмотрите логи backend
docker compose -f docker-compose.qnap.yml logs backend --tail 50
```

---

## ✅ ШАГ 10: Тестирование с вашего компьютера

**В PowerShell на вашем ПК:**

```powershell
# Регистрация
Invoke-RestMethod -Uri "http://192.168.0.214:5000/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"full_name":"PC User","email":"pcuser@test.com","password":"pass123","role":"client"}'
```

**Если получили JSON ответ с токеном - ВСЁ РАБОТАЕТ!** 🎉

---

## 📊 Полезные команды для управления

### Просмотр логов

```bash
# Все логи
docker compose -f docker-compose.qnap.yml logs

# Только backend
docker compose -f docker-compose.qnap.yml logs backend -f

# Только PostgreSQL
docker compose -f docker-compose.qnap.yml logs postgres -f

# Последние 50 строк
docker compose -f docker-compose.qnap.yml logs --tail 50
```

### Управление контейнерами

```bash
# Остановить
docker compose -f docker-compose.qnap.yml stop

# Запустить снова
docker compose -f docker-compose.qnap.yml start

# Перезапустить
docker compose -f docker-compose.qnap.yml restart

# Полная остановка и удаление (данные БД сохранятся)
docker compose -f docker-compose.qnap.yml down

# Полный перезапуск
docker compose -f docker-compose.qnap.yml down
docker compose -f docker-compose.qnap.yml up -d
```

### Проверка статуса

```bash
# Статус контейнеров
docker compose -f docker-compose.qnap.yml ps

# Использование ресурсов
docker stats

# Проверка сети
docker network ls
docker network inspect energy_audit_network
```

### Работа с базой данных

```bash
# Подключиться к PostgreSQL
docker exec -it energy_audit_db psql -U asattorov -d energy_audit

# Посмотреть таблицы
docker exec -it energy_audit_db psql -U asattorov -d energy_audit -c "\dt *.*"

# Посмотреть пользователей
docker exec -it energy_audit_db psql -U asattorov -d energy_audit -c "SELECT * FROM auth.users;"

# Посмотреть историю изменений
docker exec -it energy_audit_db psql -U asattorov -d energy_audit -c "SELECT * FROM logs.report_history ORDER BY created_at DESC LIMIT 10;"
```

---

## 🔄 Обновление приложения

Когда у вас будут изменения в коде:

```bash
# 1. Получите обновления (если через Git)
cd /share/CACHEDEV1_DATA/energy-audit/backend
git pull origin claude/learn-repo-4j7Nj

# 2. Перезапустите backend
docker compose -f docker-compose.qnap.yml restart backend

# 3. Проверьте логи
docker compose -f docker-compose.qnap.yml logs backend -f
```

---

## 🛑 Устранение проблем

### Контейнер не запускается

```bash
# Посмотрите логи
docker compose -f docker-compose.qnap.yml logs

# Пересоздайте контейнеры
docker compose -f docker-compose.qnap.yml down
docker compose -f docker-compose.qnap.yml up -d --force-recreate
```

### Backend не может подключиться к PostgreSQL

```bash
# Проверьте что PostgreSQL работает
docker compose -f docker-compose.qnap.yml ps postgres

# Проверьте логи PostgreSQL
docker compose -f docker-compose.qnap.yml logs postgres

# Проверьте сеть
docker network inspect energy_audit_network
```

### Ошибка "no space left on device"

```bash
# Проверьте место
df -h

# Очистите старые образы и контейнеры
docker system prune -a -f

# Проверьте размер директории БД
du -sh /share/CACHEDEV1_DATA/energy-audit/database
```

### Порт 5000 уже занят

```bash
# Проверьте что использует порт
netstat -tulpn | grep 5000

# Или измените порт в docker-compose.qnap.yml
# ports:
#   - "5001:5000"  # Изменить на другой порт
```

---

## 📋 Проверочный список (Checklist)

После развертывания убедитесь:

- [x] SSH подключение работает
- [x] Папки созданы на `/share/CACHEDEV1_DATA/energy-audit/`
- [x] Все файлы проекта скопированы
- [x] `.env` файл создан
- [x] Оба контейнера запущены (`docker compose ps`)
- [x] PostgreSQL healthy (`docker compose ps`)
- [x] Схемы БД созданы (`\dt *.*`)
- [x] Миграции применены (6 таблиц видны)
- [x] API отвечает на запросы
- [x] Регистрация работает
- [x] Логин работает
- [x] Логирование изменений работает

---

## 🎯 Доступ к приложению

После успешного развертывания:

- **Backend API**: `http://192.168.0.214:5000`
- **PostgreSQL**: `192.168.0.214:5432` (доступен только из Docker сети)
- **Логи**: `/share/CACHEDEV1_DATA/energy-audit/logs/`
- **База данных**: `/share/CACHEDEV1_DATA/energy-audit/database/`

---

## 📞 Что дальше?

1. ✅ **Настройте автозапуск** - контейнеры запускаются автоматически (`restart: always`)
2. ✅ **Настройте бэкапы** - см. раздел в QNAP_DEPLOYMENT.md
3. ✅ **Настройте firewall** - ограничьте доступ к порту 5000
4. ✅ **Подключите frontend** - укажите URL: `http://192.168.0.214:5000`
5. ✅ **Смените SECRET_KEY** - измените в .env на более безопасный

---

**Время развертывания**: 15-20 минут
**Последнее обновление**: 2026-01-09

---

**Успешного развертывания! 🚀**
