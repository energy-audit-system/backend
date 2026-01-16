from flask import Blueprint, request, jsonify
from app.db import db
from app.models import User
from app.utils.security import hash_password, verify_password, generate_jwt
import secrets

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    required_fields = ["full_name", "email", "password", "role"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    if data["role"] not in ("client", "engineer"):
        return jsonify({"error": "Invalid role"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "User already exists"}), 409

    verification_token = secrets.token_urlsafe(32)

    user = User(
        full_name=data["full_name"],
        email=data["email"],
        phone=data.get("phone"),
        password_hash=hash_password(data["password"]),
        role=data["role"],
        email_verification_token=verification_token,
        is_email_verified=False,
    )

    db.session.add(user)
    db.session.commit()

    token = generate_jwt(user.id, user.role)

    return jsonify({
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "token": token,
        "role": user.role,
    }), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Invalid credentials"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not verify_password(data["password"], user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_email_verified:
        return jsonify({"error": "Email not verified"}), 403

    token = generate_jwt(user.id, user.role)

    return jsonify({
        "id": user.id,
        "token": token,
        "role": user.role,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone
    })


@bp.route("/verify-email", methods=['GET'])
def verify_email():
    token = request.args.get("token")

    if not token:
        return jsonify({"error": "Missing token"}), 400
    
    user = User.query.filter_by(email_verification_token=token).first()

    if not user:
        return jsonify({"error": "Invalid token"}), 400
    
    user.is_email_verified = True
    user.email_verification_token = None

    db.session.commit()

    return jsonify({
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "token": token,
        "role": user.role,
        "is_email_verified": user.is_email_verified
    })
