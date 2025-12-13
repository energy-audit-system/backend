from flask import Flask
from .db import db
from .config import Config
from .routes import audit_orders_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(audit_orders_bp)

    return app
