import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


def generate_jwt(user_id: int, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(
            hours=current_app.config["JWT_EXPIRE_HOURS"]
        ),
    }

    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )

    return token
