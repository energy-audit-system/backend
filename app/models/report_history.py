from app.db import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB


class ReportHistory(db.Model):
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

    action = db.Column(db.Text, nullable=False)
    diff = db.Column(JSONB)  # что изменилось

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<ReportHistory id={self.id} report_id={self.report_id} action={self.action}>"
