-- User Requests table
-- For storing contact form submissions
-- Version: 0.2
-- Date: 2026-02-04

CREATE TABLE core.user_requests (
    id                  BIGSERIAL PRIMARY KEY,
    name                TEXT NOT NULL,
    phone               TEXT NOT NULL,
    email               TEXT NOT NULL,
    comment             TEXT,

    processed           BOOLEAN NOT NULL DEFAULT FALSE,
    telegram_message_id BIGINT,

    created_at          TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_user_requests_processed
    ON core.user_requests(processed);

CREATE INDEX idx_user_requests_created_at
    ON core.user_requests(created_at DESC);
