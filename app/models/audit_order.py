from app.db import db
from sqlalchemy.sql import func

class AuditOrder(db.Model):
    __tablename__ = "audit_orders"
    __table_args__ = {"schema": "core"}

    id = db.Column(db.BigInteger, primary_key=True)

    business_id = db.Column(
        db.BigInteger,
        db.ForeignKey("core.business.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status = db.Column(db.Text, nullable=False)  # pending/in_progress/ready/paid/archived
    access_until = db.Column(db.Date)

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<AuditOrder id={self.id} business_id={self.business_id} status={self.status}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "business_id": self.business_id,
            "status": self.status,
            "access_until": self.access_until.isoformat() if self.access_until else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
