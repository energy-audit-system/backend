from flask import Flask
from .db import db
from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # 🔽 ИМПОРТ ТОЛЬКО ТУТ
    from .routes import audit_orders_bp, auth_bp

    app.register_blueprint(audit_orders_bp)
    app.register_blueprint(auth_bp)

    return app
