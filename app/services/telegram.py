import os
import json
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Service for sending notifications to Telegram."""

    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def _is_configured(self) -> bool:
        """Check if Telegram credentials are configured."""
        return bool(self.bot_token and self.chat_id)

    def send_new_request_notification(
        self,
        request_id: int,
        name: str,
        phone: str,
        email: str,
        comment: Optional[str] = None
    ) -> Optional[int]:
        """
        Send notification about new user request to Telegram group.
        Returns message_id if successful, None otherwise.
        """
        if not self._is_configured():
            logger.warning("Telegram not configured, skipping notification")
            return None

        # Format message with nice layout
        message = self._format_request_message(
            request_id=request_id,
            name=name,
            phone=phone,
            email=email,
            comment=comment
        )

        # Inline keyboard with "PROCESSED" button
        keyboard = {
            "inline_keyboard": [[
                {
                    "text": "ОБРАБОТАНО",
                    "callback_data": f"process_request:{request_id}"
                }
            ]]
        }

        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "reply_markup": keyboard
                },
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            if result.get("ok"):
                message_id = result["result"]["message_id"]
                logger.info(
                    f"Telegram notification sent for request {request_id}, "
                    f"message_id: {message_id}"
                )
                return message_id
            else:
                logger.error(f"Telegram API error: {result}")
                return None

        except requests.RequestException as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return None

    def _format_request_message(
        self,
        request_id: int,
        name: str,
        phone: str,
        email: str,
        comment: Optional[str] = None
    ) -> str:
        """Format beautiful message for Telegram."""
        comment_text = comment if comment else "—"

        return f"""<b>Новая заявка #{request_id}</b>

<b>Имя:</b> {self._escape_html(name)}
<b>Телефон:</b> {self._escape_html(phone)}
<b>Email:</b> {self._escape_html(email)}

<b>Комментарий:</b>
{self._escape_html(comment_text)}

<i>Нажмите кнопку ниже после обработки заявки</i>"""

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def update_message_as_processed(
        self,
        message_id: int,
        request_id: int,
        operator_name: str
    ) -> bool:
        """Update Telegram message to show request was processed."""
        if not self._is_configured():
            return False

        new_text = f"""<b>Заявка #{request_id}</b>

<b>Статус:</b> Обработана
<b>Оператор:</b> {self._escape_html(operator_name)}"""

        try:
            response = requests.post(
                f"{self.base_url}/editMessageText",
                json={
                    "chat_id": self.chat_id,
                    "message_id": message_id,
                    "text": new_text,
                    "parse_mode": "HTML"
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("ok", False)

        except requests.RequestException as e:
            logger.error(f"Failed to update Telegram message: {e}")
            return False


# Singleton instance
telegram_notifier = TelegramNotifier()
