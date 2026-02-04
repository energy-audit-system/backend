from datetime import datetime
from app.db import db


class UserRequest(db.Model):
    """Model for storing user contact requests from the website form."""

    __tablename__ = 'user_requests'
    __table_args__ = {'schema': 'core'}

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text, nullable=True)

    processed = db.Column(db.Boolean, nullable=False, default=False)
    telegram_message_id = db.Column(db.BigInteger, nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'comment': self.comment,
            'processed': self.processed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
