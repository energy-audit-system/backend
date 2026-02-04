from flask import Blueprint, jsonify
from app.models import AuditOrder

bp = Blueprint("audit_orders", __name__, url_prefix="/audit-orders")

@bp.route("", methods=["GET"])
def list_audit_orders():
    orders = AuditOrder.query.all()
    return jsonify([o.to_dict() for o in orders])
