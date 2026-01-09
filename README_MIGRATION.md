# Инструкция по миграции на сервер

**Дата**: 2026-01-09
**Версия миграции**: 001

---

## Изменения в этой миграции

### Система логирования изменений отчётов

Реализована полная система аудита всех изменений отчётов в таблице `logs.report_history`.

**Что нового**:
- Автоматическое логирование создания отчётов
- Автоматическое логирование обновлений данных отчётов
- Структурированное хранение изменений (старые и новые значения)
- Типизированные действия: created, updated, status_changed, archived, restored, deleted
- Индексы для быстрого поиска по типу действия и дате

---

## Шаги миграции

### 1. Подготовка

Перед миграцией убедитесь, что:
- [ ] Создан бэкап базы данных
- [ ] База данных `energy_audit` существует
- [ ] Пользователь имеет права на ALTER TABLE

```bash
# Создать бэкап
pg_dump -U asattorov energy_audit > backup_before_migration_001_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Применение миграции

Выполните миграцию из файла `/database/001_alter_report_history.sql`:

```bash
# Вариант 1: Через psql
psql -U asattorov -d energy_audit -f database/001_alter_report_history.sql

# Вариант 2: Интерактивно
psql -U asattorov -d energy_audit
\i database/001_alter_report_history.sql
```

### 3. Проверка миграции

Проверьте структуру таблицы после миграции:

```bash
psql -U asattorov -d energy_audit -c "\d logs.report_history"
```

**Ожидаемая структура**:
```
                                  Table "logs.report_history"
    Column     |            Type             | Collation | Nullable | Default
---------------+-----------------------------+-----------+----------+---------
 id            | bigint                      |           | not null | nextval(...)
 report_id     | bigint                      |           | not null |
 user_id       | bigint                      |           |          |
 action_type   | text                        |           | not null |
 description   | text                        |           |          |
 changes       | jsonb                       |           |          |
 created_at    | timestamp without time zone |           | not null | now()

Indexes:
    "report_history_pkey" PRIMARY KEY, btree (id)
    "idx_report_history_action_type" btree (action_type)
    "idx_report_history_created_at" btree (created_at DESC)
    "idx_report_history_report" btree (report_id)
    "idx_report_history_user" btree (user_id)

Check constraints:
    "chk_action_type" CHECK (action_type = ANY (ARRAY['created', 'updated', 'status_changed', 'archived', 'restored', 'deleted']))

Foreign-key constraints:
    "report_history_report_id_fkey" FOREIGN KEY (report_id) REFERENCES reports.reports(id) ON DELETE CASCADE
    "report_history_user_id_fkey" FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE SET NULL
```

### 4. Тестирование

После успешной миграции запустите сервер и проверьте логирование:

#### Тест 1: Создание отчёта

```bash
curl -X POST http://localhost:5000/reports/post_report \
  -H "Content-Type: application/json" \
  -d '{
    "audit_order_id": 1,
    "data": {
      "test": "initial data"
    }
  }'
```

Проверьте, что создалась запись в `logs.report_history`:

```sql
SELECT * FROM logs.report_history WHERE action_type = 'created' ORDER BY created_at DESC LIMIT 1;
```

**Ожидаемый результат**:
- `action_type` = 'created'
- `description` содержит информацию о создании
- `changes` = NULL (при создании нет изменений)

#### Тест 2: Обновление отчёта

```bash
# Замените <report_id> на ID из предыдущего шага
curl -X PATCH http://localhost:5000/reports/<report_id> \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "test": "updated data"
    }
  }'
```

Проверьте запись об обновлении:

```sql
SELECT
  id,
  report_id,
  action_type,
  description,
  changes->>'old_value' as old_value,
  changes->>'new_value' as new_value,
  created_at
FROM logs.report_history
WHERE action_type = 'updated'
ORDER BY created_at DESC
LIMIT 1;
```

**Ожидаемый результат**:
- `action_type` = 'updated'
- `changes` содержит `old_value` и `new_value`
- `old_value` = `{"test": "initial data"}`
- `new_value` = `{"test": "updated data"}`

### 5. Проверка индексов

Убедитесь, что все индексы созданы:

```bash
psql -U asattorov -d energy_audit -c "
  SELECT indexname, indexdef
  FROM pg_indexes
  WHERE tablename = 'report_history'
  AND schemaname = 'logs';
"
```

---

## Откат миграции (если необходимо)

Если миграция вызвала проблемы, можно откатить изменения:

```sql
-- Откат миграции 001
BEGIN;

-- Добавить старые колонки обратно
ALTER TABLE logs.report_history
    ADD COLUMN action TEXT,
    ADD COLUMN diff JSONB;

-- Скопировать данные обратно
UPDATE logs.report_history
SET
    action = description,
    diff = changes;

-- Удалить CHECK constraint
ALTER TABLE logs.report_history
    DROP CONSTRAINT IF EXISTS chk_action_type;

-- Удалить новые колонки
ALTER TABLE logs.report_history
    DROP COLUMN action_type,
    DROP COLUMN description,
    DROP COLUMN changes;

-- Сделать action NOT NULL
ALTER TABLE logs.report_history
    ALTER COLUMN action SET NOT NULL;

-- Удалить новые индексы
DROP INDEX IF EXISTS logs.idx_report_history_action_type;
DROP INDEX IF EXISTS logs.idx_report_history_created_at;

COMMIT;
```

Или восстановить из бэкапа:

```bash
# Остановить приложение
# Удалить текущую базу
dropdb -U asattorov energy_audit

# Восстановить из бэкапа
createdb -U asattorov energy_audit
psql -U asattorov energy_audit < backup_before_migration_001_YYYYMMDD_HHMMSS.sql
```

---

## Проверка готовности к production

После миграции и тестирования убедитесь:

- [ ] Миграция применена успешно
- [ ] Все индексы созданы
- [ ] CHECK constraint работает корректно
- [ ] Создание отчёта логируется
- [ ] Обновление отчёта логируется с сохранением старых и новых значений
- [ ] Производительность не ухудшилась (проверить EXPLAIN на основных запросах)
- [ ] Бэкап создан и сохранён

---

## Мониторинг после миграции

### Проверить размер таблицы

```sql
SELECT
    pg_size_pretty(pg_total_relation_size('logs.report_history')) as total_size,
    pg_size_pretty(pg_relation_size('logs.report_history')) as table_size,
    pg_size_pretty(pg_indexes_size('logs.report_history')) as indexes_size;
```

### Проверить статистику по типам действий

```sql
SELECT
    action_type,
    COUNT(*) as count,
    MIN(created_at) as first_action,
    MAX(created_at) as last_action
FROM logs.report_history
GROUP BY action_type
ORDER BY count DESC;
```

### Найти отчёты с наибольшим количеством изменений

```sql
SELECT
    report_id,
    COUNT(*) as changes_count,
    MAX(created_at) as last_change
FROM logs.report_history
GROUP BY report_id
ORDER BY changes_count DESC
LIMIT 10;
```

---

## Известные ограничения

1. **user_id пока NULL**: Пока не реализован JWT middleware, user_id будет NULL во всех записях. Это будет исправлено в следующих версиях.

2. **Старые данные**: Если в таблице `logs.report_history` были данные до миграции, миграция попытается их сконвертировать автоматически. Проверьте корректность конвертации.

3. **Размер JSONB**: Поле `changes` хранит полные old_value и new_value. Для больших отчётов это может занимать много места. Рассмотрите настройку автоматической очистки старых записей (retention policy).

---

## Контакты

При возникновении проблем с миграцией обращайтесь к разработчику.

**Последнее обновление**: 2026-01-09
