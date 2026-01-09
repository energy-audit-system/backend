-- Migration: Improve logs.report_history table structure
-- Date: 2026-01-07
-- Description: Add action_type constraint, rename diff to changes, add description field

-- Step 1: Add new columns
ALTER TABLE logs.report_history
    ADD COLUMN action_type TEXT,
    ADD COLUMN description TEXT,
    ADD COLUMN changes JSONB;

-- Step 2: Migrate existing data (if any)
-- Copy 'action' to 'action_type' and 'diff' to 'changes'
UPDATE logs.report_history
SET
    action_type = CASE
        WHEN action ILIKE '%created%' THEN 'created'
        WHEN action ILIKE '%updated%' OR action ILIKE '%changed%' THEN 'updated'
        WHEN action ILIKE '%status%' THEN 'status_changed'
        WHEN action ILIKE '%archive%' THEN 'archived'
        WHEN action ILIKE '%restore%' THEN 'restored'
        WHEN action ILIKE '%delete%' THEN 'deleted'
        ELSE 'updated'  -- default fallback
    END,
    description = action,
    changes = diff;

-- Step 3: Make action_type NOT NULL after migration
ALTER TABLE logs.report_history
    ALTER COLUMN action_type SET NOT NULL;

-- Step 4: Add CHECK constraint for action_type
ALTER TABLE logs.report_history
    ADD CONSTRAINT chk_action_type CHECK (
        action_type IN ('created', 'updated', 'status_changed', 'archived', 'restored', 'deleted')
    );

-- Step 5: Drop old columns
ALTER TABLE logs.report_history
    DROP COLUMN action,
    DROP COLUMN diff;

-- Step 6: Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_report_history_action_type
    ON logs.report_history(action_type);

CREATE INDEX IF NOT EXISTS idx_report_history_created_at
    ON logs.report_history(created_at DESC);

-- Step 7: Add comment for documentation
COMMENT ON TABLE logs.report_history IS 'Audit trail for all report changes';
COMMENT ON COLUMN logs.report_history.action_type IS 'Type of action: created, updated, status_changed, archived, restored, deleted';
COMMENT ON COLUMN logs.report_history.description IS 'Human-readable description of the change';
COMMENT ON COLUMN logs.report_history.changes IS 'Structured JSON with old and new values: {"field": "status", "old_value": "draft", "new_value": "final"}';
