#!/usr/bin/env python3
"""
Test script for report history logging functionality.
Run this after applying migration 001_alter_report_history.sql

Usage:
    python test_logging.py
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.db import db
from app.models import Report, ReportHistory, AuditOrder, Business, User
from app.utils.logging import ReportLogger


def test_logging():
    """Test the report logging functionality"""
    app = create_app()

    with app.app_context():
        print("=" * 60)
        print("Testing Report History Logging System")
        print("=" * 60)

        # Check if report_history table has new structure
        print("\n1. Checking table structure...")
        try:
            # Try to query with new column names
            test_query = db.session.query(ReportHistory).limit(1).first()
            print("✓ Table structure is correct (action_type, description, changes)")
        except Exception as e:
            print(f"✗ Error: Table structure issue - {e}")
            print("  Make sure to run migration 001_alter_report_history.sql first!")
            return False

        # Create test user (if not exists)
        print("\n2. Creating test user...")
        test_user = User.query.filter_by(email="test_logging@example.com").first()
        if not test_user:
            test_user = User(
                full_name="Test Logger",
                email="test_logging@example.com",
                password_hash="dummy_hash",
                role="engineer",
                is_email_verified=True
            )
            db.session.add(test_user)
            db.session.flush()
            print(f"✓ Created test user (ID: {test_user.id})")
        else:
            print(f"✓ Using existing test user (ID: {test_user.id})")

        # Create test business (if not exists)
        print("\n3. Creating test business...")
        test_business = Business.query.filter_by(business_name="Test Logging Business").first()
        if not test_business:
            test_business = Business(
                business_name="Test Logging Business",
                address="Test Address",
                inn="1234567890",
                owner_id=test_user.id
            )
            db.session.add(test_business)
            db.session.flush()
            print(f"✓ Created test business (ID: {test_business.id})")
        else:
            print(f"✓ Using existing test business (ID: {test_business.id})")

        # Create test audit order (if not exists)
        print("\n4. Creating test audit order...")
        test_order = AuditOrder.query.filter_by(business_id=test_business.id).first()
        if not test_order:
            test_order = AuditOrder(
                business_id=test_business.id,
                status="pending",
                order_data={"test": "data"}
            )
            db.session.add(test_order)
            db.session.flush()
            print(f"✓ Created test audit order (ID: {test_order.id})")
        else:
            print(f"✓ Using existing audit order (ID: {test_order.id})")

        # Test 1: Log report creation
        print("\n5. Testing report creation logging...")
        test_report = Report(
            audit_order_id=test_order.id,
            version=1,
            status="draft",
            data={"energy_consumption": {"electricity": 100000}},
            access_until="2027-01-01"
        )
        db.session.add(test_report)
        db.session.flush()

        ReportLogger.log_creation(
            report_id=test_report.id,
            user_id=test_user.id,
            description=f"Test: Created report version {test_report.version}"
        )
        db.session.commit()

        # Verify creation log
        creation_log = ReportHistory.query.filter_by(
            report_id=test_report.id,
            action_type="created"
        ).first()

        if creation_log:
            print(f"✓ Creation logged successfully")
            print(f"  - Log ID: {creation_log.id}")
            print(f"  - Action: {creation_log.action_type}")
            print(f"  - User: {creation_log.user_id}")
            print(f"  - Description: {creation_log.description}")
        else:
            print("✗ Creation log not found!")
            return False

        # Test 2: Log report update
        print("\n6. Testing report update logging...")
        old_data = test_report.data.copy()
        new_data = {"energy_consumption": {"electricity": 150000, "gas": 50000}}

        test_report.data = new_data

        ReportLogger.log_update(
            report_id=test_report.id,
            old_data=old_data,
            new_data=new_data,
            user_id=test_user.id,
            description="Test: Updated energy consumption data"
        )
        db.session.commit()

        # Verify update log
        update_log = ReportHistory.query.filter_by(
            report_id=test_report.id,
            action_type="updated"
        ).first()

        if update_log:
            print(f"✓ Update logged successfully")
            print(f"  - Log ID: {update_log.id}")
            print(f"  - Action: {update_log.action_type}")
            print(f"  - User: {update_log.user_id}")
            print(f"  - Description: {update_log.description}")
            print(f"  - Old value: {update_log.changes.get('old_value')}")
            print(f"  - New value: {update_log.changes.get('new_value')}")
        else:
            print("✗ Update log not found!")
            return False

        # Test 3: Log status change
        print("\n7. Testing status change logging...")
        old_status = test_report.status
        new_status = "final"
        test_report.status = new_status

        ReportLogger.log_status_change(
            report_id=test_report.id,
            old_status=old_status,
            new_status=new_status,
            user_id=test_user.id
        )
        db.session.commit()

        # Verify status change log
        status_log = ReportHistory.query.filter_by(
            report_id=test_report.id,
            action_type="status_changed"
        ).first()

        if status_log:
            print(f"✓ Status change logged successfully")
            print(f"  - Log ID: {status_log.id}")
            print(f"  - Action: {status_log.action_type}")
            print(f"  - Changes: {status_log.changes}")
        else:
            print("✗ Status change log not found!")
            return False

        # Test 4: Get report history
        print("\n8. Testing get_report_history()...")
        history = ReportLogger.get_report_history(test_report.id)
        print(f"✓ Found {len(history)} history entries for report {test_report.id}")
        for idx, entry in enumerate(history, 1):
            print(f"  {idx}. {entry.action_type} - {entry.description} ({entry.created_at})")

        # Test 5: Get user actions
        print("\n9. Testing get_user_actions()...")
        user_actions = ReportLogger.get_user_actions(test_user.id, limit=10)
        print(f"✓ Found {len(user_actions)} actions by user {test_user.id}")
        for idx, action in enumerate(user_actions, 1):
            print(f"  {idx}. Report {action.report_id}: {action.action_type}")

        # Cleanup test data
        print("\n10. Cleaning up test data...")
        db.session.delete(test_report)  # This will cascade delete history entries
        db.session.delete(test_order)
        db.session.delete(test_business)
        db.session.delete(test_user)
        db.session.commit()
        print("✓ Test data cleaned up")

        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        return True


if __name__ == "__main__":
    try:
        success = test_logging()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
