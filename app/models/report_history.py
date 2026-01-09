from app.db import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB


class ReportHistory(db.Model):
    """
    Audit trail for all report changes.
    Tracks creation, updates, status changes, archiving, and deletions.
    """
    __tablename__ = "report_history"
    __table_args__ = {"schema": "logs"}

    id = db.Column(db.BigInteger, primary_key=True)

    report_id = db.Column(
        db.BigInteger,
        db.ForeignKey("reports.reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("auth.users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Action type: created, updated, status_changed, archived, restored, deleted
    action_type = db.Column(db.Text, nullable=False, index=True)

    # Human-readable description (optional)
    description = db.Column(db.Text, nullable=True)

    # Structured changes: {"field": "status", "old_value": "draft", "new_value": "final"}
    changes = db.Column(JSONB, nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False,
        index=True
    )

    def __repr__(self) -> str:
        return f"<ReportHistory id={self.id} report_id={self.report_id} action={self.action_type}>"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "report_id": self.report_id,
            "user_id": self.user_id,
            "action_type": self.action_type,
            "description": self.description,
            "changes": self.changes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
