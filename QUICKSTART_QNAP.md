# Quick Start: Развертывание на QNAP NAS TS-433

Быстрая инструкция для развертывания. Для подробностей см. [QNAP_DEPLOYMENT.md](QNAP_DEPLOYMENT.md)

---

## Предварительные требования

- ✅ QNAP NAS TS-433 настроен и доступен
- ✅ Container Station установлен через App Center
- ✅ SSH доступ включен (Control Panel → Telnet/SSH)
- ✅ У вас есть доступ к админ панели

---

## 5 шагов до запуска

### Шаг 1: Включите SSH и подключитесь

```bash
# Подключитесь к NAS
ssh admin@<IP_вашего_NAS>

# Создайте директорию для проекта
mkdir -p /share/Container/energy-audit-backend
cd /share/Container/energy-audit-backend
```

### Шаг 2: Перенесите проект на NAS

**Вариант A - Через Git (если есть интернет на NAS):**
```bash
cd /share/Container
git clone <URL_вашего_репозитория> energy-audit-backend
cd energy-audit-backend
git checkout claude/learn-repo-4j7Nj
```

**Вариант B - Через SCP (с вашего компьютера):**
```bash
# На вашем компьютере:
cd /path/to/backend
scp -r . admin@<IP_NAS>:/share/Container/energy-audit-backend/
```

### Шаг 3: Настройте переменные окружения

```bash
# На NAS:
cd /share/Container/energy-audit-backend

# Создайте .env файл из примера
cp .env.example .env

# Отредактируйте .env (опционально)
vi .env
# Измените SECRET_KEY на более безопасный
```

### Шаг 4: Запустите Docker Compose

```bash
# Запустите все сервисы (PostgreSQL + Backend)
docker-compose up -d

# Проверьте статус
docker-compose ps

# Должны увидеть:
# energy_audit_db       running   5432/tcp
# energy_audit_backend  running   5000/tcp
```

### Шаг 5: Инициализируйте базу данных

```bash
# Создайте схемы
docker exec -it energy_audit_db psql -U asattorov -d energy_audit << 'EOF'
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS reports;
CREATE SCHEMA IF NOT EXISTS logs;
\q
EOF

# Примените миграции
docker exec -i energy_audit_db psql -U asattorov -d energy_audit < database/000_init.sql
docker exec -i energy_audit_db psql -U asattorov -d energy_audit < database/001_alter_report_history.sql
```

---

## Проверка работы

```bash
# 1. Проверьте логи
docker-compose logs -f backend

# 2. Протестируйте API (с вашего компьютера или NAS)
curl -X POST http://<IP_NAS>:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "role": "engineer"
  }'

# Должны получить JSON ответ с токеном
```

**Успех!** 🎉 Backend доступен на `http://<IP_NAS>:5000`

---

## Полезные команды

```bash
# Просмотр логов
docker-compose logs -f backend
docker-compose logs -f postgres

# Перезапуск
docker-compose restart

# Остановка
docker-compose stop

# Полная остановка и удаление
docker-compose down

# Обновление после изменений кода
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Что дальше?

1. ✅ **Настройте автоматический бэкап** - См. раздел "Backup стратегия" в QNAP_DEPLOYMENT.md
2. ✅ **Настройте firewall** - Ограничьте доступ к порту 5000
3. ✅ **Настройте HTTPS** - Используйте Nginx reverse proxy
4. ✅ **Подключите frontend** - Укажите в frontend URL: `http://<IP_NAS>:5000`

---

## Устранение проблем

### Контейнеры не запускаются
```bash
docker-compose logs
docker-compose down
docker-compose up -d --force-recreate
```

### Не могу подключиться к API
```bash
# Проверьте запущены ли контейнеры
docker-compose ps

# Проверьте порты
netstat -tulpn | grep 5000

# Проверьте firewall
# В веб-интерфейсе QNAP: Control Panel → Security → Firewall
```

### База данных не инициализирована
```bash
# Проверьте логи PostgreSQL
docker-compose logs postgres

# Пересоздайте БД
docker-compose down -v
docker-compose up -d
# Затем повторите Шаг 5
```

---

## Техподдержка

**Полная документация**: [QNAP_DEPLOYMENT.md](QNAP_DEPLOYMENT.md)

**При проблемах**:
1. Проверьте `docker-compose logs`
2. Проверьте разделы Troubleshooting в QNAP_DEPLOYMENT.md
3. Обратитесь к разработчику

---

**Время развертывания**: ~10-15 минут
**Последнее обновление**: 2026-01-09
