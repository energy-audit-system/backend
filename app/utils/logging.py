"""
Logging utilities for tracking changes to reports.
Provides functions to log all actions in logs.report_history table.
"""

from typing import Optional, Dict, Any
from app.db import db
from app.models import ReportHistory


class ReportLogger:
    """
    Utility class for logging report changes to the audit trail.

    Action types:
    - created: Report was created
    - updated: Report data was updated
    - status_changed: Report status changed (draft → final)
    - archived: Report was archived
    - restored: Report was restored from archive
    - deleted: Report was deleted
    """

    @staticmethod
    def log_creation(
        report_id: int,
        user_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> ReportHistory:
        """
        Log report creation.

        Args:
            report_id: ID of the created report
            user_id: ID of the user who created the report (optional)
            description: Additional description (optional)

        Returns:
            ReportHistory: Created log entry
        """
        log_entry = ReportHistory(
            report_id=report_id,
            user_id=user_id,
            action_type="created",
            description=description or "Отчёт создан",
            changes=None  # No changes on creation
        )
        db.session.add(log_entry)
        db.session.flush()
        return log_entry

    @staticmethod
    def log_update(
        report_id: int,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        user_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> ReportHistory:
        """
        Log report data update.

        Args:
            report_id: ID of the updated report
            old_data: Previous data (JSONB)
            new_data: New data (JSONB)
            user_id: ID of the user who updated the report (optional)
            description: Additional description (optional)

        Returns:
            ReportHistory: Created log entry
        """
        changes = {
            "old_value": old_data,
            "new_value": new_data
        }

        log_entry = ReportHistory(
            report_id=report_id,
            user_id=user_id,
            action_type="updated",
            description=description or "Данные отчёта обновлены",
            changes=changes
        )
        db.session.add(log_entry)
        db.session.flush()
        return log_entry

    @staticmethod
    def log_status_change(
        report_id: int,
        old_status: str,
        new_status: str,
        user_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> ReportHistory:
        """
        Log report status change.

        Args:
            report_id: ID of the report
            old_status: Previous status
            new_status: New status
            user_id: ID of the user who changed status (optional)
            description: Additional description (optional)

        Returns:
            ReportHistory: Created log entry
        """
        changes = {
            "field": "status",
            "old_value": old_status,
            "new_value": new_status
        }

        log_entry = ReportHistory(
            report_id=report_id,
            user_id=user_id,
            action_type="status_changed",
            description=description or f"Статус изменён: {old_status} → {new_status}",
            changes=changes
        )
        db.session.add(log_entry)
        db.session.flush()
        return log_entry

    @staticmethod
    def log_archive(
        report_id: int,
        user_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> ReportHistory:
        """
        Log report archiving.

        Args:
            report_id: ID of the archived report
            user_id: ID of the user who archived the report (optional)
            description: Additional description (optional)

        Returns:
            ReportHistory: Created log entry
        """
        log_entry = ReportHistory(
            report_id=report_id,
            user_id=user_id,
            action_type="archived",
            description=description or "Отчёт перемещён в архив",
            changes=None
        )
        db.session.add(log_entry)
        db.session.flush()
        return log_entry

    @staticmethod
    def log_restore(
        report_id: int,
        user_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> ReportHistory:
        """
        Log report restoration from archive.

        Args:
            report_id: ID of the restored report
            user_id: ID of the user who restored the report (optional)
            description: Additional description (optional)

        Returns:
            ReportHistory: Created log entry
        """
        log_entry = ReportHistory(
            report_id=report_id,
            user_id=user_id,
            action_type="restored",
            description=description or "Отчёт восстановлен из архива",
            changes=None
        )
        db.session.add(log_entry)
        db.session.flush()
        return log_entry

    @staticmethod
    def log_deletion(
        report_id: int,
        user_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> ReportHistory:
        """
        Log report deletion.

        Args:
            report_id: ID of the deleted report
            user_id: ID of the user who deleted the report (optional)
            description: Additional description (optional)

        Returns:
            ReportHistory: Created log entry
        """
        log_entry = ReportHistory(
            report_id=report_id,
            user_id=user_id,
            action_type="deleted",
            description=description or "Отчёт удалён",
            changes=None
        )
        db.session.add(log_entry)
        db.session.flush()
        return log_entry

    @staticmethod
    def get_report_history(report_id: int) -> list[ReportHistory]:
        """
        Get all history entries for a specific report.

        Args:
            report_id: ID of the report

        Returns:
            List of ReportHistory entries, ordered by creation time (newest first)
        """
        return (
            ReportHistory.query
            .filter_by(report_id=report_id)
            .order_by(ReportHistory.created_at.desc())
            .all()
        )

    @staticmethod
    def get_user_actions(user_id: int, limit: int = 50) -> list[ReportHistory]:
        """
        Get recent actions by a specific user.

        Args:
            user_id: ID of the user
            limit: Maximum number of entries to return (default: 50)

        Returns:
            List of ReportHistory entries, ordered by creation time (newest first)
        """
        return (
            ReportHistory.query
            .filter_by(user_id=user_id)
            .order_by(ReportHistory.created_at.desc())
            .limit(limit)
            .all()
        )
