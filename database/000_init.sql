-- Energy Audit DB
-- Initial schema
-- Version: 0.1
-- Author: asattorov
-- Date: 2025-12-13
-- IMPORTANT: Do not edit after migrations start

CREATE TABLE auth.users (
    id              BIGSERIAL PRIMARY KEY,
    full_name       TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    phone           TEXT,
    password_hash   TEXT NOT NULL,

    role            TEXT NOT NULL CHECK (
        role IN ('engineer', 'client', 'admin')
    ),

    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    updated_at      TIMESTAMP NOT NULL DEFAULT now()
);

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

    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    updated_at      TIMESTAMP NOT NULL DEFAULT now()
);
CREATE TABLE reports.reports (
    id              BIGSERIAL PRIMARY KEY,

    audit_order_id  BIGINT NOT NULL
        REFERENCES core.audit_orders(id)
        ON DELETE CASCADE,

    version         INTEGER NOT NULL DEFAULT 1,

    status          TEXT NOT NULL CHECK (
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
CREATE TABLE logs.report_history (
    id              BIGSERIAL PRIMARY KEY,

    report_id       BIGINT NOT NULL
        REFERENCES reports.reports(id)
        ON DELETE CASCADE,

    user_id         BIGINT NOT NULL
        REFERENCES auth.users(id)
        ON DELETE SET NULL,

    action          TEXT NOT NULL,

    diff            JSONB,

    created_at      TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX idx_users_role ON auth.users(role);

CREATE INDEX idx_business_owner ON core.business(owner_id);

CREATE INDEX idx_audit_orders_business
    ON core.audit_orders(business_id);

CREATE INDEX idx_reports_audit_order
    ON reports.reports(audit_order_id);

CREATE INDEX idx_reports_data_gin
    ON reports.reports USING GIN (data);

CREATE INDEX idx_report_files_report
    ON reports.files(report_id);

CREATE INDEX idx_report_history_report
    ON logs.report_history(report_id);
