from app import create_app
from app.db import db
from app.models import (
    User,
    Business,
    AuditOrder,
    Report,
    ReportHistory,
)

app = create_app()

with app.app_context():
    # --- USERS ---
    admin = User(
        full_name="Admin User",
        email="admin@test.com",
        password_hash="hashed_admin",
        role="admin",
    )

    client = User(
        full_name="Client User",
        email="client@test.com",
        password_hash="hashed_client",
        role="client",
    )

    db.session.add_all([admin, client])
    db.session.commit()

    # --- BUSINESS ---
    business = Business(
        business_name="Test Factory LLC",
        address="Tashkent",
        inn="123456789",
        owner_id=client.id,
    )

    db.session.add(business)
    db.session.commit()

    # --- AUDIT ORDER ---
    order = AuditOrder(
        business_id=business.id,
        status="in_progress",
    )

    db.session.add(order)
    db.session.commit()

    # --- REPORT ---
    report = Report(
        audit_order_id=order.id,
        version=1,
        status="draft",
        data={
            "general": {
                "energy_consumption": 12345,
                "employees": 120,
            },
            "notes": "Initial draft",
        },
    )

    db.session.add(report)
    db.session.commit()

    # --- HISTORY ---
    history = ReportHistory(
        report_id=report.id,
        user_id=admin.id,
        action="create_report",
        diff={"created": True},
    )

    db.session.add(history)
    db.session.commit()

    print("✅ Test data inserted successfully")
