# API Документация - Energy Audit System

**Версия**: 1.0
**Base URL**: `http://localhost:5000`
**Последнее обновление**: 2026-01-07

---

## Содержание

1. [Общая информация](#общая-информация)
2. [Аутентификация](#аутентификация)
3. [Endpoints](#endpoints)
   - [Аутентификация](#endpoints-аутентификация)
   - [Заказы на аудит](#endpoints-заказы-на-аудит)
   - [Отчёты](#endpoints-отчёты)
4. [Модели данных](#модели-данных)
5. [Коды ошибок](#коды-ошибок)

---

## Общая информация

### Формат данных
- Все запросы и ответы используют формат **JSON**
- Кодировка: **UTF-8**
- Content-Type: `application/json`

### Аутентификация
Большинство endpoints требуют JWT токен в заголовке:
```
Authorization: Bearer <ваш_jwt_токен>
```

### Статусы HTTP
- `200 OK` - Успешный запрос
- `201 Created` - Ресурс успешно создан
- `400 Bad Request` - Некорректные данные запроса
- `401 Unauthorized` - Требуется аутентификация
- `403 Forbidden` - Недостаточно прав
- `404 Not Found` - Ресурс не найден
- `500 Internal Server Error` - Ошибка сервера

---

## Аутентификация

### Роли пользователей
- `client` - Клиент (владелец бизнеса)
- `engineer` - Инженер (проводит аудит)
- `admin` - Администратор

### JWT Токен
**Срок действия**: 24 часа
**Алгоритм**: HS256
**Структура payload**:
```json
{
  "sub": 123,           // ID пользователя
  "role": "client",     // Роль пользователя
  "exp": 1704672000     // Timestamp истечения
}
```

---

## Endpoints

### Аутентификация

#### 1. Регистрация пользователя

**Endpoint**: `POST /auth/register`
**Описание**: Регистрация нового пользователя (клиент или инженер)
**Требует авторизации**: Нет

**Тело запроса**:
```json
{
  "full_name": "Иванов Иван Иванович",
  "email": "ivanov@example.com",
  "password": "SecurePassword123",
  "role": "client"
}
```

**Параметры**:
| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| full_name | string | Да | Полное имя пользователя |
| email | string | Да | Email (должен быть уникальным) |
| password | string | Да | Пароль (минимум 6 символов) |
| role | string | Да | Роль: `client` или `engineer` |

**Успешный ответ** (201 Created):
```json
{
  "message": "Пользователь успешно зарегистрирован",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "full_name": "Иванов Иван Иванович",
    "email": "ivanov@example.com",
    "role": "client",
    "is_email_verified": false
  }
}
```

**Ошибки**:
- `400` - Email уже используется
- `400` - Некорректные данные (отсутствуют обязательные поля)
- `400` - Некорректная роль (должна быть client или engineer)

---

#### 2. Вход в систему

**Endpoint**: `POST /auth/login`
**Описание**: Авторизация пользователя и получение JWT токена
**Требует авторизации**: Нет

**Тело запроса**:
```json
{
  "email": "ivanov@example.com",
  "password": "SecurePassword123"
}
```

**Параметры**:
| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| email | string | Да | Email пользователя |
| password | string | Да | Пароль пользователя |

**Успешный ответ** (200 OK):
```json
{
  "message": "Вход выполнен успешно",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "full_name": "Иванов Иван Иванович",
    "email": "ivanov@example.com",
    "role": "client"
  }
}
```

**Ошибки**:
- `401` - Неверный email или пароль
- `403` - Email не подтверждён (требуется верификация)
- `400` - Отсутствуют обязательные поля

---

#### 3. Подтверждение email

**Endpoint**: `GET /auth/verify-email?token=<токен>`
**Описание**: Подтверждение email адреса пользователя
**Требует авторизации**: Нет

**Query параметры**:
| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| token | string | Да | Токен подтверждения из письма |

**Пример запроса**:
```
GET /auth/verify-email?token=xYz123AbC456DeF789
```

**Успешный ответ** (200 OK):
```json
{
  "message": "Email успешно подтверждён"
}
```

**Ошибки**:
- `400` - Неверный или истёкший токен
- `404` - Пользователь не найден

---

### Заказы на аудит

#### 4. Получить список заказов

**Endpoint**: `GET /audit-orders`
**Описание**: Получение списка всех заказов на энергоаудит
**Требует авторизации**: Да (JWT токен)

**Заголовки**:
```
Authorization: Bearer <jwt_токен>
```

**Успешный ответ** (200 OK):
```json
{
  "audit_orders": [
    {
      "id": 1,
      "business_id": 5,
      "status": "in_progress",
      "access_until": "2026-12-31",
      "building_type": "Производственное здание",
      "building_subtype": "Завод",
      "order_data": {
        "area": 5000,
        "floors": 3,
        "year_built": 1995
      },
      "created_at": "2026-01-01T10:00:00",
      "updated_at": "2026-01-05T14:30:00"
    },
    {
      "id": 2,
      "business_id": 7,
      "status": "pending",
      "access_until": "2026-11-15",
      "building_type": "Офисное здание",
      "building_subtype": "Бизнес-центр",
      "order_data": {
        "area": 1200,
        "floors": 5
      },
      "created_at": "2026-01-03T09:15:00",
      "updated_at": "2026-01-03T09:15:00"
    }
  ],
  "total": 2
}
```

**Структура заказа**:
| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | ID заказа |
| business_id | integer | ID бизнеса |
| status | string | Статус: `pending`, `in_progress`, `ready`, `paid`, `archived` |
| access_until | date | Дата окончания доступа (YYYY-MM-DD) |
| building_type | string | Тип здания |
| building_subtype | string | Подтип здания |
| order_data | object | Дополнительные данные о заказе (гибкая структура) |
| created_at | timestamp | Дата создания |
| updated_at | timestamp | Дата последнего обновления |

**Ошибки**:
- `401` - Отсутствует или неверный токен авторизации

---

### Отчёты

#### 5. Создать отчёт

**Endpoint**: `POST /reports/post_report`
**Описание**: Создание нового отчёта по энергоаудиту
**Требует авторизации**: Да (JWT токен)

**Заголовки**:
```
Authorization: Bearer <jwt_токен>
Content-Type: application/json
```

**Тело запроса**:
```json
{
  "audit_order_id": 1,
  "version": 1,
  "status": "draft",
  "data": {
    "energy_consumption": {
      "electricity": 150000,
      "gas": 80000,
      "water": 5000
    },
    "recommendations": [
      {
        "title": "Замена освещения на LED",
        "savings_percent": 30,
        "cost": 500000
      }
    ],
    "total_savings_potential": 25
  },
  "access_until": "2027-01-01"
}
```

**Параметры**:
| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| audit_order_id | integer | Да | ID заказа на аудит |
| version | integer | Да | Версия отчёта (должна быть уникальной для заказа) |
| status | string | Да | Статус: `draft` или `final` |
| data | object | Да | Данные отчёта (гибкая структура JSON) |
| access_until | date | Да | Дата окончания доступа (YYYY-MM-DD) |

**Успешный ответ** (201 Created):
```json
{
  "message": "Отчёт успешно создан",
  "report": {
    "id": 10,
    "audit_order_id": 1,
    "version": 1,
    "status": "draft",
    "data": {
      "energy_consumption": {
        "electricity": 150000,
        "gas": 80000,
        "water": 5000
      },
      "recommendations": [...],
      "total_savings_potential": 25
    },
    "access_until": "2027-01-01",
    "created_at": "2026-01-07T15:30:00",
    "updated_at": "2026-01-07T15:30:00"
  }
}
```

**Ошибки**:
- `400` - Отчёт с такой версией уже существует для данного заказа
- `400` - Некорректные данные (отсутствуют обязательные поля)
- `401` - Отсутствует или неверный токен авторизации
- `404` - Заказ не найден

---

#### 6. Обновить отчёт

**Endpoint**: `PATCH /reports/<report_id>`
**Описание**: Частичное обновление данных отчёта
**Требует авторизации**: Да (JWT токен)

**Параметры URL**:
| Параметр | Тип | Описание |
|----------|-----|----------|
| report_id | integer | ID отчёта для обновления |

**Заголовки**:
```
Authorization: Bearer <jwt_токен>
Content-Type: application/json
```

**Тело запроса**:
```json
{
  "data": {
    "energy_consumption": {
      "electricity": 155000,
      "gas": 82000,
      "water": 5200
    },
    "recommendations": [
      {
        "title": "Замена освещения на LED",
        "savings_percent": 30,
        "cost": 500000
      },
      {
        "title": "Утепление фасада",
        "savings_percent": 15,
        "cost": 1200000
      }
    ],
    "total_savings_potential": 30
  }
}
```

**Параметры**:
| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| data | object | Да | Обновлённые данные отчёта (полностью заменяет старые данные) |

**Успешный ответ** (200 OK):
```json
{
  "message": "Отчёт успешно обновлён",
  "report": {
    "id": 10,
    "audit_order_id": 1,
    "version": 1,
    "status": "draft",
    "data": {
      "energy_consumption": {
        "electricity": 155000,
        "gas": 82000,
        "water": 5200
      },
      "recommendations": [...],
      "total_savings_potential": 30
    },
    "access_until": "2027-01-01",
    "created_at": "2026-01-07T15:30:00",
    "updated_at": "2026-01-07T16:45:00"
  }
}
```

**Ошибки**:
- `400` - Некорректные данные
- `401` - Отсутствует или неверный токен авторизации
- `404` - Отчёт не найден

---

## Модели данных

### User (Пользователь)
```json
{
  "id": 1,
  "full_name": "Иванов Иван Иванович",
  "email": "ivanov@example.com",
  "phone": "+7 (999) 123-45-67",
  "role": "client",
  "is_email_verified": true,
  "created_at": "2026-01-01T10:00:00",
  "updated_at": "2026-01-01T10:00:00"
}
```

### Business (Бизнес)
```json
{
  "id": 5,
  "business_name": "ООО «Энергопром»",
  "address": "г. Москва, ул. Ленина, д. 10",
  "inn": "7707123456",
  "owner_id": 1,
  "created_at": "2026-01-01T12:00:00"
}
```

### AuditOrder (Заказ на аудит)
```json
{
  "id": 1,
  "business_id": 5,
  "status": "in_progress",
  "access_until": "2026-12-31",
  "building_type": "Производственное здание",
  "building_subtype": "Завод",
  "order_data": {
    "area": 5000,
    "floors": 3,
    "year_built": 1995,
    "heating_type": "Централизованное",
    "additional_info": "Требуется срочный аудит"
  },
  "created_at": "2026-01-01T10:00:00",
  "updated_at": "2026-01-05T14:30:00"
}
```

**Возможные статусы**:
- `pending` - Ожидает обработки
- `in_progress` - В процессе выполнения
- `ready` - Готов (аудит завершён)
- `paid` - Оплачен
- `archived` - Архивирован

### Report (Отчёт)
```json
{
  "id": 10,
  "audit_order_id": 1,
  "version": 1,
  "status": "draft",
  "data": {
    "energy_consumption": {
      "electricity": 150000,
      "gas": 80000,
      "water": 5000
    },
    "recommendations": [
      {
        "title": "Замена освещения",
        "savings_percent": 30,
        "cost": 500000
      }
    ]
  },
  "access_until": "2027-01-01",
  "created_at": "2026-01-07T15:30:00",
  "updated_at": "2026-01-07T16:45:00"
}
```

**Возможные статусы**:
- `draft` - Черновик
- `final` - Финальная версия

### ReportFile (Файл отчёта)
```json
{
  "id": 25,
  "report_id": 10,
  "file_type": "pdf",
  "cloud_path": "/reports/2026/01/report_10_v1.pdf",
  "created_at": "2026-01-07T17:00:00"
}
```

**Типы файлов**:
- `pdf` - PDF документ
- `xlsx` - Excel таблица
- `archive` - Архив (ZIP, RAR и т.д.)

### ReportHistory (История изменений отчёта)
```json
{
  "id": 100,
  "report_id": 10,
  "user_id": 5,
  "action_type": "updated",
  "description": "Обновлены данные отчёта 10",
  "changes": {
    "old_value": {
      "energy_consumption": {
        "electricity": 150000
      }
    },
    "new_value": {
      "energy_consumption": {
        "electricity": 155000
      }
    }
  },
  "created_at": "2026-01-09T10:30:00"
}
```

**Типы действий (action_type)**:
- `created` - Отчёт создан
- `updated` - Данные отчёта обновлены
- `status_changed` - Статус изменён (draft → final)
- `archived` - Отчёт перемещён в архив
- `restored` - Отчёт восстановлен из архива
- `deleted` - Отчёт удалён

**Назначение**:
Таблица `logs.report_history` автоматически записывает все изменения отчётов для аудита. Каждая операция создания, обновления или изменения статуса создаёт запись в истории с информацией о том, что именно изменилось.

---

## Коды ошибок

### Формат ошибки
```json
{
  "error": "Описание ошибки",
  "code": "ERROR_CODE",
  "details": {
    "field": "email",
    "message": "Email уже используется"
  }
}
```

### Типичные ошибки

#### 400 Bad Request
```json
{
  "error": "Некорректные данные запроса",
  "message": "Отсутствует обязательное поле: email"
}
```

#### 401 Unauthorized
```json
{
  "error": "Требуется авторизация",
  "message": "JWT токен отсутствует или невалиден"
}
```

#### 403 Forbidden
```json
{
  "error": "Доступ запрещён",
  "message": "Недостаточно прав для выполнения операции"
}
```

#### 404 Not Found
```json
{
  "error": "Ресурс не найден",
  "message": "Отчёт с ID 999 не существует"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Внутренняя ошибка сервера",
  "message": "Пожалуйста, попробуйте позже"
}
```

---

## Примеры использования

### Пример 1: Полный цикл регистрации и создания отчёта

```javascript
// 1. Регистрация
const registerResponse = await fetch('http://localhost:5000/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    full_name: 'Петров Пётр Петрович',
    email: 'petrov@example.com',
    password: 'SecurePass123',
    role: 'engineer'
  })
});

const { token } = await registerResponse.json();

// 2. Получение списка заказов
const ordersResponse = await fetch('http://localhost:5000/audit-orders', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const { audit_orders } = await ordersResponse.json();

// 3. Создание отчёта
const reportResponse = await fetch('http://localhost:5000/reports/post_report', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    audit_order_id: audit_orders[0].id,
    version: 1,
    status: 'draft',
    data: {
      energy_consumption: {
        electricity: 120000,
        gas: 60000
      }
    },
    access_until: '2027-01-01'
  })
});

const { report } = await reportResponse.json();
console.log('Отчёт создан:', report);
```

### Пример 2: Вход и обновление отчёта

```javascript
// 1. Вход в систему
const loginResponse = await fetch('http://localhost:5000/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'petrov@example.com',
    password: 'SecurePass123'
  })
});

const { token } = await loginResponse.json();

// 2. Обновление отчёта
const updateResponse = await fetch('http://localhost:5000/reports/10', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    data: {
      energy_consumption: {
        electricity: 125000,
        gas: 65000
      },
      status_updated: true
    }
  })
});

const { report } = await updateResponse.json();
console.log('Отчёт обновлён:', report);
```

---

## Дополнительные заметки

### CORS
CORS настроен для разработки и принимает запросы со всех доменов. В production будет ограничен конкретными доменами.

### Разработка в процессе
Следующие endpoints находятся в разработке:
- `POST /audit-orders` - Создание нового заказа
- `GET /audit-orders/:id` - Получение конкретного заказа
- `PATCH /audit-orders/:id` - Обновление заказа
- `GET /reports` - Список всех отчётов
- `GET /reports/:id` - Получение конкретного отчёта
- `DELETE /reports/:id` - Удаление отчёта
- `POST /reports/:id/files` - Загрузка файлов к отчёту

### Версионирование API
Текущая версия API: `v1`
В будущем все endpoints будут иметь префикс `/api/v1/`

### Автоматическое логирование изменений
**ВАЖНО**: Все изменения отчётов автоматически записываются в таблицу `logs.report_history` для аудита:
- При создании отчёта (`POST /reports/post_report`) создаётся запись с `action_type: "created"`
- При обновлении данных (`PATCH /reports/<id>`) создаётся запись с `action_type: "updated"` и сохраняются старые и новые значения
- В будущем будет логироваться изменение статуса, архивирование и удаление

**Для frontend разработчиков**:
- Логирование происходит автоматически на бэкенде
- В будущем будет доступен endpoint для получения истории изменений конкретного отчёта
- user_id пока NULL, но будет заполняться автоматически из JWT токена при реализации middleware

---

**Вопросы и поддержка**: Обращайтесь к бэкенд разработчику

**Последнее обновление**: 2026-01-09
