-- Energy Audit DB
-- Initial schema
-- Version: 0.2
-- Author: asattorov
-- Date: 2026-01-09
-- Updated: Синхронизировано с текущими моделями

-- ============================================
-- SCHEMA: auth - Аутентификация и пользователи
-- ============================================

-- === SCHEMAS ===
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS reports;
CREATE SCHEMA IF NOT EXISTS logs;

CREATE TABLE auth.users (
    id              BIGSERIAL PRIMARY KEY,
    full_name       TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    phone           TEXT,
    password_hash   TEXT NOT NULL,

    role            TEXT NOT NULL CHECK (
        role IN ('engineer', 'client', 'admin')
    ),

    -- Email verification
    is_email_verified           BOOLEAN NOT NULL DEFAULT FALSE,
    email_verification_token    TEXT,

    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    updated_at      TIMESTAMP NOT NULL DEFAULT now()
);

-- ============================================
-- SCHEMA: core - Бизнес логика
-- ============================================

CREATE TABLE core.business (
    id              BIGSERIAL PRIMARY KEY,
    business_name   TEXT NOT NULL,
    address         TEXT,
    inn             TEXT,

    owner_id        BIGINT NOT NULL
        REFERENCES auth.users(id)
        ON DELETE RESTRICT,

    created_at      TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT uq_business_name UNIQUE (business_name)
);

CREATE TABLE core.audit_orders (
    id              BIGSERIAL PRIMARY KEY,

    business_id     BIGINT NOT NULL
        REFERENCES core.business(id)
        ON DELETE CASCADE,

    status          TEXT NOT NULL CHECK (
        status IN ('pending', 'in_progress', 'ready', 'paid', 'archived')
    ),

    access_until    DATE,

    -- Информация о здании
    building_type       TEXT NOT NULL,
    building_subtype    TEXT NOT NULL,

    -- Дополнительные данные заказа (JSONB для гибкости)
    order_data      JSONB,

    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    updated_at      TIMESTAMP NOT NULL DEFAULT now()
);

-- ============================================
-- SCHEMA: reports - Отчёты и файлы
-- ============================================

CREATE TABLE reports.reports (
    id              BIGSERIAL PRIMARY KEY,

    audit_order_id  BIGINT NOT NULL
        REFERENCES core.audit_orders(id)
        ON DELETE CASCADE,

    version         INTEGER NOT NULL DEFAULT 1,

    status          TEXT NOT NULL DEFAULT 'draft' CHECK (
        status IN ('draft', 'final')
    ),

    data            JSONB NOT NULL,

    access_until    DATE,

    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    updated_at      TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT uq_report_version UNIQUE (audit_order_id, version)
);

CREATE TABLE reports.files (
    id              BIGSERIAL PRIMARY KEY,

    report_id       BIGINT NOT NULL
        REFERENCES reports.reports(id)
        ON DELETE CASCADE,

    file_type       TEXT NOT NULL CHECK (
        file_type IN ('pdf', 'xlsx', 'archive')
    ),

    cloud_path      TEXT NOT NULL,

    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

-- ============================================
-- SCHEMA: logs - Аудит и логирование
-- ============================================

-- Таблица истории изменений отчётов
-- ВАЖНО: Эта структура будет изменена миграцией 001_alter_report_history.sql
-- Здесь создаётся начальная версия
CREATE TABLE logs.report_history (
    id              BIGSERIAL PRIMARY KEY,

    report_id       BIGINT NOT NULL
        REFERENCES reports.reports(id)
        ON DELETE CASCADE,

    user_id         BIGINT
        REFERENCES auth.users(id)
        ON DELETE SET NULL,

    action          TEXT NOT NULL,

    diff            JSONB,

    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

-- ============================================
-- INDEXES - Индексы для производительности
-- ============================================

-- auth.users indexes
CREATE INDEX idx_users_role ON auth.users(role);
CREATE INDEX idx_users_email ON auth.users(email);

-- core.business indexes
CREATE INDEX idx_business_owner ON core.business(owner_id);

-- core.audit_orders indexes
CREATE INDEX idx_audit_orders_business ON core.audit_orders(business_id);
CREATE INDEX idx_audit_orders_status ON core.audit_orders(status);

-- reports.reports indexes
CREATE INDEX idx_reports_audit_order ON reports.reports(audit_order_id);
CREATE INDEX idx_reports_data_gin ON reports.reports USING GIN (data);
CREATE INDEX idx_reports_status ON reports.reports(status);

-- reports.files indexes
CREATE INDEX idx_report_files_report ON reports.files(report_id);

-- logs.report_history indexes
CREATE INDEX idx_report_history_report ON logs.report_history(report_id);
CREATE INDEX idx_report_history_user ON logs.report_history(user_id);

-- ============================================
-- TRIGGERS - Автоматическое обновление updated_at
-- ============================================

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для auth.users
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Триггер для core.audit_orders
CREATE TRIGGER update_audit_orders_updated_at
    BEFORE UPDATE ON core.audit_orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Триггер для reports.reports
CREATE TRIGGER update_reports_updated_at
    BEFORE UPDATE ON reports.reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- COMMENTS - Документация таблиц
-- ============================================

COMMENT ON TABLE auth.users IS 'Пользователи системы (клиенты, инженеры, администраторы)';
COMMENT ON TABLE core.business IS 'Предприятия клиентов';
COMMENT ON TABLE core.audit_orders IS 'Заказы на энергоаудит';
COMMENT ON TABLE reports.reports IS 'Отчёты по энергоаудиту';
COMMENT ON TABLE reports.files IS 'Файлы отчётов (PDF, XLSX, архивы)';
COMMENT ON TABLE logs.report_history IS 'История изменений отчётов (аудит трейл)';

COMMENT ON COLUMN auth.users.role IS 'Роль: engineer (инженер), client (клиент), admin (администратор)';
COMMENT ON COLUMN auth.users.is_email_verified IS 'Подтверждён ли email пользователя';
COMMENT ON COLUMN core.audit_orders.status IS 'Статус: pending, in_progress, ready, paid, archived';
COMMENT ON COLUMN core.audit_orders.order_data IS 'Дополнительные данные заказа в формате JSONB';
COMMENT ON COLUMN reports.reports.data IS 'Данные отчёта в формате JSONB';
COMMENT ON COLUMN reports.reports.status IS 'Статус отчёта: draft (черновик), final (финальный)';
