from app.db import db
from sqlalchemy.sql import func

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id = db.Column(db.BigInteger, primary_key=True)

    full_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    phone = db.Column(db.Text)

    password_hash = db.Column(db.Text, nullable=False)

    role = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime, server_default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"