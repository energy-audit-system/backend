# Path for engineers to post their report values
from flask import Blueprint, request, jsonify
from app.db import db
from app.models import Report
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError

bp = Blueprint("reports", __name__, url_prefix="/reports")

# creating a new report
@bp.route("/post_report", methods=["POST"])
def post_report():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Missing fields"}), 400
    
    report = Report(
        audit_order_id=data["audit_order_id"],
        data=data["data"]
    )

    db.session.add(report)
    db.session.commit()

    return jsonify({
        "id": report.id,
    }), 201

# updating the report
@bp.route("/<int:report_id>", methods=["PATCH"])
def update_report(report_id):
    data = request.get_json(silent=True)

    if not data or not "data" in data:
        return jsonify({"error": "data is required"}), 400
    
    report = Report.query.get(report_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404

    report.data = data["data"]
    report.updated_at = func.now()

    try:
        db.session.commit()
        return jsonify({"id": report.id}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Update failed"}), 400

