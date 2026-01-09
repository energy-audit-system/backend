# Path for engineers to post their report values
from flask import Blueprint, request, jsonify
from app.db import db
from app.models import Report
from app.utils.logging import ReportLogger
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
    db.session.flush()  # Flush to get report.id before logging

    # Log report creation
    # TODO: Extract user_id from JWT token when auth middleware is implemented
    ReportLogger.log_creation(
        report_id=report.id,
        user_id=None,  # Will be populated from JWT token later
        description=f"Создан отчёт версии {report.version} для заказа {report.audit_order_id}"
    )

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

    # Store old data for logging
    old_data = report.data

    # Update report data
    report.data = data["data"]
    report.updated_at = func.now()

    try:
        # Log the update
        # TODO: Extract user_id from JWT token when auth middleware is implemented
        ReportLogger.log_update(
            report_id=report.id,
            old_data=old_data,
            new_data=data["data"],
            user_id=None,  # Will be populated from JWT token later
            description=f"Обновлены данные отчёта {report.id}"
        )

        db.session.commit()
        return jsonify({"id": report.id}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Update failed"}), 400

