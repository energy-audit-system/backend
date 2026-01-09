# Energy Audit System Backend - Claude Project Guide

**Last Updated**: 2026-01-07
**Repository**: energy-audit-system/backend
**Branch**: claude/learn-repo-4j7Nj

---

## Project Overview

**Purpose**: Backend API for managing energy audits for businesses. Handles the complete audit lifecycle including user management, business registration, audit order processing, and report generation with versioning.

**Technology Stack**:
- Python 3.x + Flask
- PostgreSQL + SQLAlchemy ORM
- JWT Authentication (PyJWT)
- Flask-CORS

---

## Project Structure

```
/home/user/backend/
├── run.py                          # Entry point - Flask app on port 5000
├── requirements.txt                # Python dependencies
├── README.md                        # Project documentation
├── claude.md                        # This file - Claude's project guide
├── .gitignore
│
├── app/                            # Main application package
│   ├── __init__.py                # App factory (create_app)
│   ├── config.py                  # Configuration (DB, JWT, secrets)
│   ├── db.py                      # SQLAlchemy instance
│   │
│   ├── models/                    # ORM Models
│   │   ├── __init__.py
│   │   ├── user.py               # User model (auth.users)
│   │   ├── business.py           # Business model (core.business)
│   │   ├── audit_order.py        # AuditOrder model (core.audit_orders)
│   │   ├── report.py             # Report model (reports.reports)
│   │   ├── report_file.py        # ReportFile model (reports.files)
│   │   └── report_history.py     # ReportHistory model (logs.report_history)
│   │
│   ├── routes/                    # API Blueprints
│   │   ├── __init__.py
│   │   ├── auth.py               # /auth endpoints
│   │   ├── audit_orders.py       # /audit-orders endpoints
│   │   └── reports_reports.py    # /reports endpoints
│   │
│   ├── utils/                     # Utility functions
│   │   └── security.py           # Password hashing, JWT generation
│   │
│   └── scripts/                   # Database scripts
│       └── seed.py               # Seed test data
│
├── database/                       # Database schema
│   └── 000_init.sql              # Schema initialization SQL
│
└── docs/                          # Documentation
    └── db/
        └── Скелет БД (черновой).drawio
```

---

## Database Architecture

**Database**: `energy_audit` on PostgreSQL (localhost:5432)

### Schema Organization

#### 1. `auth` Schema - Authentication & User Management

**users** table:
- `id` (BIGSERIAL PK)
- `full_name` (TEXT)
- `email` (TEXT, UNIQUE)
- `phone` (TEXT)
- `password_hash` (TEXT)
- `role` (TEXT) - CHECK: 'engineer', 'client', 'admin'
- `is_email_verified` (BOOLEAN)
- `email_verification_token` (TEXT)
- `created_at`, `updated_at` (TIMESTAMP)

#### 2. `core` Schema - Business Logic

**business** table:
- `id` (BIGSERIAL PK)
- `business_name` (TEXT, UNIQUE)
- `address` (TEXT)
- `inn` (TEXT) - Tax ID
- `owner_id` (BIGINT FK → auth.users)
- `created_at` (TIMESTAMP)

**audit_orders** table:
- `id` (BIGSERIAL PK)
- `business_id` (BIGINT FK → core.business)
- `status` (TEXT) - CHECK: 'pending', 'in_progress', 'ready', 'paid', 'archived'
- `access_until` (DATE)
- `building_type` (TEXT)
- `building_subtype` (TEXT)
- `order_data` (JSONB) - Flexible order details
- `created_at`, `updated_at` (TIMESTAMP)

#### 3. `reports` Schema - Report Management

**reports** table:
- `id` (BIGSERIAL PK)
- `audit_order_id` (BIGINT FK → core.audit_orders)
- `version` (INTEGER)
- `status` (TEXT) - CHECK: 'draft', 'final'
- `data` (JSONB) - Report content
- `access_until` (DATE)
- `created_at`, `updated_at` (TIMESTAMP)
- UNIQUE constraint on (audit_order_id, version)

**files** table:
- `id` (BIGSERIAL PK)
- `report_id` (BIGINT FK → reports.reports)
- `file_type` (TEXT) - CHECK: 'pdf', 'xlsx', 'archive'
- `cloud_path` (TEXT)
- `created_at` (TIMESTAMP)

#### 4. `logs` Schema - Audit Trail

**report_history** table:
- `id` (BIGSERIAL PK)
- `report_id` (BIGINT FK → reports.reports)
- `user_id` (BIGINT FK → auth.users, nullable)
- `action_type` (TEXT) - CHECK: 'created', 'updated', 'status_changed', 'archived', 'restored', 'deleted'
- `description` (TEXT) - Human-readable description
- `changes` (JSONB) - Structured changes: `{"field": "status", "old_value": "draft", "new_value": "final"}`
- `created_at` (TIMESTAMP)
- Indexed on: report_id, user_id, action_type, created_at

---

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new user (client/engineer)
  - Body: `{full_name, email, password, role}`
  - Returns: JWT token
- `POST /auth/login` - User login
  - Body: `{email, password}`
  - Returns: JWT token
- `GET /auth/verify-email?token=<token>` - Email verification

### Audit Orders (`/audit-orders`)
- `GET /audit-orders` - List all audit orders

### Reports (`/reports`)
- `POST /reports/post_report` - Create new report
  - Body: `{audit_order_id, version, status, data, access_until}`
- `PATCH /reports/<report_id>` - Update report data
  - Body: `{data}` (JSONB)

---

## Key Components

### Models (SQLAlchemy ORM)

**Location**: `/app/models/`

- **User** (`user.py`) - Maps to `auth.users`
- **Business** (`business.py`) - Maps to `core.business`
- **AuditOrder** (`audit_order.py`) - Maps to `core.audit_orders`
- **Report** (`report.py`) - Maps to `reports.reports`
- **ReportFile** (`report_file.py`) - Maps to `reports.files`
- **ReportHistory** (`report_history.py`) - Maps to `logs.report_history`

### Routes (Flask Blueprints)

**Location**: `/app/routes/`

- **auth.py** - Authentication endpoints
- **audit_orders.py** - Audit order management
- **reports_reports.py** - Report CRUD operations

### Utilities

**Security** (`/app/utils/security.py`):
- `hash_password(password)` - Werkzeug password hashing
- `check_password(password, hash)` - Password verification
- `generate_token(user_id, role)` - JWT token generation
- `verify_token(token)` - JWT token validation

**Logging** (`/app/utils/logging.py`):
- `ReportLogger.log_creation()` - Log report creation
- `ReportLogger.log_update()` - Log report data updates
- `ReportLogger.log_status_change()` - Log status changes (draft → final)
- `ReportLogger.log_archive()` - Log archiving
- `ReportLogger.log_restore()` - Log restoration from archive
- `ReportLogger.log_deletion()` - Log deletion
- `ReportLogger.get_report_history()` - Get audit trail for report
- `ReportLogger.get_user_actions()` - Get user's recent actions

---

## Configuration

**File**: `/app/config.py`

```python
SQLALCHEMY_DATABASE_URI = "postgresql://asattorov:neda2020luba@localhost:5432/energy_audit"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "neda2331"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
```

⚠️ **Security Note**: Credentials are currently hardcoded. Should migrate to environment variables.

---

## Authentication Flow

### Registration
1. User submits registration form
2. Password hashed with Werkzeug
3. Email verification token generated
4. User created in database (`is_email_verified=False`)
5. JWT token returned immediately

### Login
1. User submits credentials
2. Password verified against hash
3. Email verification checked (must be verified)
4. JWT token generated and returned

### JWT Structure
- **Algorithm**: HS256
- **Expiration**: 24 hours
- **Payload**: `{sub: user_id, role: user_role, exp: timestamp}`

---

## Status Workflows

### Audit Order Status
```
pending → in_progress → ready → paid → archived
```

### Report Status
```
draft → final
```

---

## Known Issues & TODOs

### Security
- [ ] Move database credentials to environment variables
- [ ] Move JWT secret to environment variables
- [ ] Restrict CORS to specific origins
- [ ] Add input validation and sanitization
- [ ] Add rate limiting

### API Completeness
- [ ] Add authentication middleware/decorators
- [ ] Implement pagination for list endpoints
- [ ] Add filtering and search capabilities
- [ ] Complete CRUD operations for all resources
- [ ] Standardize error responses
- [ ] Add request validation

### Infrastructure
- [ ] Add logging system
- [ ] Implement database migrations (Alembic)
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Create test suite
- [ ] Add health check endpoint

---

## Development Conventions

### File Naming
- Models: Singular, PascalCase (e.g., `user.py`, `audit_order.py`)
- Routes: Lowercase with underscores (e.g., `auth.py`, `reports_reports.py`)
- Database tables: Lowercase with underscores, plural where appropriate

### Code Style
- Follow PEP 8 Python style guide
- Use type hints where appropriate
- SQLAlchemy models define `__tablename__` and `__table_args__`
- Blueprint names match their module names

### Database
- Use JSONB for flexible/dynamic data (order_data, report data, diffs)
- Timestamps: `created_at`, `updated_at` (auto-updated via trigger)
- Foreign keys use ON DELETE CASCADE where appropriate
- CHECK constraints for enumerated values

---

## Changelog

### 2026-01-09
- **Report History & Audit Trail System**: Implemented comprehensive logging for all report changes
  - Created SQL migration `001_alter_report_history.sql` to improve table structure
  - Updated `ReportHistory` model with new fields: `action_type`, `description`, `changes`
  - Replaced `action` and `diff` columns with structured approach
  - Added CHECK constraint for action_type: created, updated, status_changed, archived, restored, deleted
  - Created `ReportLogger` utility class (`/app/utils/logging.py`) with methods for all action types
  - Implemented automatic logging in POST `/reports/post_report` endpoint (creation)
  - Implemented automatic logging in PATCH `/reports/<id>` endpoint (updates)
  - Added indexes on action_type and created_at for query performance
  - Logging tracks old and new values in structured JSONB format
  - Ready for server migration with full audit trail

### 2026-01-07
- **Initial Documentation**: Created claude.md for project structure reference
- **Repository Analysis**: Documented current state of the project
  - 6 models (User, Business, AuditOrder, Report, ReportFile, ReportHistory)
  - 3 route blueprints (auth, audit_orders, reports)
  - 6 API endpoints implemented
  - PostgreSQL with 4 schemas (auth, core, reports, logs)
- **API Documentation**: Created API.md - comprehensive API documentation in Russian
  - Full endpoint documentation with request/response examples
  - Data models and error codes reference
  - Code examples in JavaScript for frontend integration
  - Russian language for frontend team collaboration

### Previous Changes (from git history)
- **2609a68**: Add PATCH endpoint for reports and update timestamps
- **48a3964**: Auth: регистрация и логин
- **a2ac01d**: Изначальный бекенд: создана БД, написан первый эндпоинт

---

## Quick Reference

### Start Server
```bash
python run.py
# Server runs on http://0.0.0.0:5000
```

### Database Connection
```python
from app.db import db
# Access via db.session
```

### Create New Model
1. Create file in `/app/models/`
2. Define SQLAlchemy model with `__tablename__` and schema
3. Import in `/app/models/__init__.py`

### Create New Route
1. Create blueprint in `/app/routes/`
2. Define routes with `@blueprint.route()`
3. Import and register in `/app/routes/__init__.py`

---

## Notes for Claude

- Always check this file before making significant changes
- Update the Changelog section when implementing features
- Maintain consistency with existing patterns
- Security is critical - avoid hardcoded secrets
- Keep database schema documentation in sync with actual schema
- Test authentication flows when modifying auth logic
- Consider backward compatibility when changing API contracts

---

**End of Claude Project Guide**
