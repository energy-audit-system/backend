from app.db import db
from sqlalchemy.sql import func

class Business(db.Model):
    __tablename__ = "business"
    __table_args__ = {"schema": "core"}

    id = db.Column(db.BigInteger, primary_key=True)

    business_name = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text)
    inn = db.Column(db.Text)

    owner_id = db.Column(
        db.BigInteger,
        db.ForeignKey("auth.users.id", ondelete="RESTRICT"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime, server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<Business id={self.id} name={self.business_name}>"
