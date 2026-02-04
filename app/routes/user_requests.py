import os
import hmac
import hashlib
import logging
from flask import Blueprint, request, jsonify

from app.db import db
from app.models.user_request import UserRequest
from app.services.telegram import telegram_notifier

logger = logging.getLogger(__name__)

user_requests_bp = Blueprint('user_requests', __name__, url_prefix='/api/requests')


@user_requests_bp.route('', methods=['POST'])
def create_request():
    """
    Create a new user request from the website form.
    Saves to DB and sends notification to Telegram.
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate required fields
    required_fields = ['name', 'phone', 'email']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({
            'error': 'Missing required fields',
            'missing': missing
        }), 400

    # Create new request
    user_request = UserRequest(
        name=data['name'].strip(),
        phone=data['phone'].strip(),
        email=data['email'].strip(),
        comment=data.get('comment', '').strip() or None
    )

    db.session.add(user_request)
    db.session.commit()

    # Send Telegram notification
    message_id = telegram_notifier.send_new_request_notification(
        request_id=user_request.id,
        name=user_request.name,
        phone=user_request.phone,
        email=user_request.email,
        comment=user_request.comment
    )

    # Save telegram message_id for later update
    if message_id:
        user_request.telegram_message_id = message_id
        db.session.commit()

    return jsonify({
        'success': True,
        'request_id': user_request.id
    }), 201


@user_requests_bp.route('/<int:request_id>/process', methods=['PATCH'])
def mark_processed(request_id):
    """Mark request as processed (called from admin panel or directly)."""
    user_request = UserRequest.query.get_or_404(request_id)

    if user_request.processed:
        return jsonify({'error': 'Already processed'}), 400

    user_request.processed = True
    db.session.commit()

    return jsonify({
        'success': True,
        'request': user_request.to_dict()
    })


@user_requests_bp.route('/telegram/webhook', methods=['POST'])
def telegram_webhook():
    """
    Handle Telegram bot webhook callbacks.
    Processes the "PROCESSED" button click.
    """
    data = request.get_json()

    if not data:
        return jsonify({'ok': True})

    # Handle callback query (button press)
    callback_query = data.get('callback_query')
    if not callback_query:
        return jsonify({'ok': True})

    callback_data = callback_query.get('data', '')
    user = callback_query.get('from', {})
    operator_name = user.get('first_name', 'Operator')
    if user.get('last_name'):
        operator_name += f" {user['last_name']}"

    # Parse callback data
    if callback_data.startswith('process_request:'):
        try:
            request_id = int(callback_data.split(':')[1])
        except (IndexError, ValueError):
            logger.warning(f"Invalid callback data: {callback_data}")
            return jsonify({'ok': True})

        # Find and update request
        user_request = UserRequest.query.get(request_id)
        if user_request and not user_request.processed:
            user_request.processed = True
            db.session.commit()

            # Update Telegram message
            if user_request.telegram_message_id:
                telegram_notifier.update_message_as_processed(
                    message_id=user_request.telegram_message_id,
                    request_id=request_id,
                    operator_name=operator_name
                )

            logger.info(
                f"Request {request_id} marked as processed by {operator_name}"
            )

        # Answer callback to remove loading state on button
        _answer_callback_query(callback_query.get('id'))

    return jsonify({'ok': True})


def _answer_callback_query(callback_query_id: str):
    """Answer callback query to remove loading indicator."""
    if not callback_query_id:
        return

    import requests as req
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        return

    try:
        req.post(
            f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery",
            json={
                "callback_query_id": callback_query_id,
                "text": "Заявка обработана!"
            },
            timeout=5
        )
    except Exception as e:
        logger.warning(f"Failed to answer callback query: {e}")


@user_requests_bp.route('', methods=['GET'])
def list_requests():
    """List all requests with optional filtering."""
    processed = request.args.get('processed')

    query = UserRequest.query.order_by(UserRequest.created_at.desc())

    if processed is not None:
        processed_bool = processed.lower() in ('true', '1', 'yes')
        query = query.filter(UserRequest.processed == processed_bool)

    requests_list = query.all()

    return jsonify({
        'requests': [r.to_dict() for r in requests_list],
        'total': len(requests_list)
    })
