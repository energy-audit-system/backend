# Тестовые данные для Energy Audit System

## 📋 Содержание

Файл `002_seed_test_data.sql` содержит полный набор тестовых данных:

- **8 пользователей** (3 инженера, 4 клиента, 1 админ)
- **5 предприятий**
- **6 заказов на аудит** (разные статусы)
- **4 отчёта** (финальные и черновики)
- **6 файлов** отчётов
- **10 записей истории** изменений

---

## 🚀 Быстрый старт

### Вариант 1: Использовать готовый SQL файл

**⚠️ ВНИМАНИЕ:** Хеши паролей в SQL файле упрощенные. Для работающих паролей используйте Вариант 2.

```bash
# Применить тестовые данные
psql -U asattorov -d energy_audit -f database/002_seed_test_data.sql
```

### Вариант 2: Сгенерировать правильные хеши паролей (РЕКОМЕНДУЕТСЯ)

```bash
# 1. Сгенерировать SQL с правильными хешами
cd database
python3 generate_test_users.py > insert_test_users.sql

# 2. Применить к базе данных
psql -U asattorov -d energy_audit -f insert_test_users.sql

# 3. Затем добавить остальные данные (business, orders, reports)
# Отредактируйте 002_seed_test_data.sql - удалите секцию INSERT INTO auth.users
# И выполните:
psql -U asattorov -d energy_audit -f 002_seed_test_data.sql
```

### Вариант 3: Через Docker

```bash
# Если используете docker-compose
docker exec -i energy_audit_db psql -U asattorov -d energy_audit < database/002_seed_test_data.sql
```

---

## 👤 Тестовые пользователи

### Пароль для ВСЕХ: `password123`

| Email | Роль | ФИО | Телефон |
|-------|------|-----|---------|
| engineer1@example.com | engineer | Иванов Иван Петрович | +7 (999) 111-22-33 |
| engineer2@example.com | engineer | Петрова Мария Александровна | +7 (999) 222-33-44 |
| engineer3@example.com | engineer | Сидоров Алексей Викторович | +7 (999) 333-44-55 |
| client1@example.com | client | Смирнов Дмитрий Олегович | +7 (999) 444-55-66 |
| client2@example.com | client | Кузнецова Елена Сергеевна | +7 (999) 555-66-77 |
| client3@example.com | client | Попов Андрей Николаевич | +7 (999) 666-77-88 |
| client4@example.com | client | Васильева Ольга Ивановна | +7 (999) 777-88-99 |
| admin@example.com | admin | Администратов Админ Админович | +7 (999) 000-00-00 |

---

## 🏢 Предприятия

1. **ООО "ЭнергоПром"** - Москва (владелец: client1)
2. **АО "ТеплоЭнерго"** - Санкт-Петербург (владелец: client2)
3. **ИП Попов А.Н.** - Екатеринбург (владелец: client3)
4. **ООО "СветТорг"** - Новосибирск (владелец: client4)
5. **ООО "ПромСтрой"** - Казань (владелец: client1)

---

## 📦 Заказы на аудит

| ID | Предприятие | Статус | Тип здания | Площадь |
|----|-------------|--------|------------|---------|
| 1 | ООО "ЭнергоПром" | paid | Производственное (Завод) | 5000 м² |
| 2 | АО "ТеплоЭнерго" | ready | Офисное (Бизнес-центр) | 3500 м² |
| 3 | ИП Попов А.Н. | in_progress | Торговое (Магазин) | 800 м² |
| 4 | ООО "СветТорг" | in_progress | Складское | 10000 м² |
| 5 | ООО "ПромСтрой" | pending | Производственное (Цех) | 2000 м² |
| 6 | ООО "ЭнергоПром" | pending | Административное | 1200 м² |

---

## 📊 Отчёты

### Отчёт 1 (Order 1) - ФИНАЛЬНЫЙ ✅
- **Инженер:** Иванов Иван Петрович
- **Статус:** final
- **Энергопотребление:** 850,000 кВт·ч/год
- **Рекомендации:** 3 (LED освещение, ЧП, утепление)
- **Экономия:** 1,151,000 руб/год (20.5%)
- **Инвестиции:** 3,800,000 руб
- **Файлы:** PDF, XLSX, архив с фото

### Отчёт 2 (Order 2) - ФИНАЛЬНЫЙ ✅
- **Инженер:** Петрова Мария Александровна
- **Статус:** final
- **Энергопотребление:** 520,000 кВт·ч/год
- **Рекомендации:** 2 (вентиляция, автоматизация)
- **Экономия:** 388,000 руб/год (12.1%)
- **Файлы:** PDF, XLSX

### Отчёт 3 (Order 3) - ЧЕРНОВИК 📝
- **Инженер:** Сидоров Алексей Викторович
- **Статус:** draft
- **Рекомендации:** 1 (холодильное оборудование)
- **Файлы:** PDF (черновик)

### Отчёт 4 (Order 4) - ЧЕРНОВИК 📝
- **Инженер:** Иванов Иван Петрович
- **Статус:** draft
- **Данные:** Начальная версия

---

## 🔍 Полезные запросы для проверки

### Проверить пользователей
```sql
SELECT id, email, role, is_email_verified FROM auth.users;
```

### Проверить заказы с предприятиями
```sql
SELECT
    ao.id,
    b.business_name,
    ao.status,
    ao.building_type,
    ao.created_at
FROM core.audit_orders ao
JOIN core.business b ON ao.business_id = b.id
ORDER BY ao.created_at DESC;
```

### Проверить отчёты с инженерами
```sql
SELECT
    r.id,
    r.version,
    r.status,
    r.data->>'engineer_name' as engineer,
    r.data->>'energy_efficiency_class' as class,
    r.created_at
FROM reports.reports r
ORDER BY r.created_at DESC;
```

### Проверить историю изменений
```sql
SELECT
    rh.id,
    rh.report_id,
    u.full_name as user_name,
    rh.action,
    rh.created_at
FROM logs.report_history rh
LEFT JOIN auth.users u ON rh.user_id = u.id
ORDER BY rh.created_at DESC
LIMIT 10;
```

### Статистика по заказам
```sql
SELECT
    status,
    COUNT(*) as count
FROM core.audit_orders
GROUP BY status
ORDER BY count DESC;
```

---

## 🧹 Очистка тестовых данных

### Удалить ВСЕ данные (ОСТОРОЖНО!)

```sql
-- Удаление в правильном порядке (из-за внешних ключей)
TRUNCATE TABLE logs.report_history CASCADE;
TRUNCATE TABLE reports.files CASCADE;
TRUNCATE TABLE reports.reports CASCADE;
TRUNCATE TABLE core.audit_orders CASCADE;
TRUNCATE TABLE core.business CASCADE;
TRUNCATE TABLE auth.users CASCADE;

-- Сбросить счетчики ID
ALTER SEQUENCE auth.users_id_seq RESTART WITH 1;
ALTER SEQUENCE core.business_id_seq RESTART WITH 1;
ALTER SEQUENCE core.audit_orders_id_seq RESTART WITH 1;
ALTER SEQUENCE reports.reports_id_seq RESTART WITH 1;
ALTER SEQUENCE reports.files_id_seq RESTART WITH 1;
ALTER SEQUENCE logs.report_history_id_seq RESTART WITH 1;
```

### Удалить только тестовых пользователей

```sql
DELETE FROM auth.users WHERE email LIKE '%@example.com';
```

---

## 📝 Структура данных в JSON

### Пример order_data
```json
{
  "area": 5000,
  "floors": 3,
  "year_built": 1995,
  "heating_type": "Централизованное",
  "employees": 150,
  "working_hours": "24/7"
}
```

### Пример report.data (финальный отчёт)
```json
{
  "executive_summary": "Краткое резюме",
  "energy_consumption": {
    "electricity_kwh_year": 850000,
    "electricity_cost_rub": 4250000,
    "gas_m3_year": 120000,
    "gas_cost_rub": 840000
  },
  "energy_efficiency_class": "D",
  "recommendations": [
    {
      "id": 1,
      "title": "Название рекомендации",
      "description": "Описание",
      "investment_rub": 500000,
      "savings_kwh_year": 85000,
      "savings_rub_year": 425000,
      "payback_period_years": 1.2,
      "priority": "high"
    }
  ],
  "total_investment_rub": 3800000,
  "total_savings_rub_year": 1151000,
  "engineer_name": "Иванов Иван Петрович"
}
```

---

## 🎯 Тестовые сценарии

### Сценарий 1: Вход как инженер
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"engineer1@example.com","password":"password123"}'
```

### Сценарий 2: Получить список заказов
```bash
curl -X GET http://localhost:5000/audit-orders \
  -H "Authorization: Bearer <token>"
```

### Сценарий 3: Создать новый отчёт
```bash
curl -X POST http://localhost:5000/reports/post_report \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "audit_order_id": 5,
    "data": {
      "energy_consumption": {
        "electricity_kwh_year": 100000
      }
    }
  }'
```

---

## 💡 Советы

1. **Для разработки frontend** - используйте готовые ID из таблиц
2. **Для тестирования API** - все пользователи с паролем `password123`
3. **Для демонстрации** - отчёты 1 и 2 содержат полные реальные данные
4. **Для разработки** - отчёты 3 и 4 можно модифицировать

---

**Последнее обновление:** 2026-01-13
