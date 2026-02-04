from app.db import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB


class Report(db.Model):
    __tablename__ = "reports"
    __table_args__ = {"schema": "reports"}

    id = db.Column(db.BigInteger, primary_key=True)

    audit_order_id = db.Column(
        db.BigInteger,
        db.ForeignKey("core.audit_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.Text, nullable=False, default='draft')  # draft/final

    data = db.Column(JSONB, nullable=False)

    access_until = db.Column(db.Date)

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Report id={self.id} order_id={self.audit_order_id} v={self.version} status={self.status}>"
