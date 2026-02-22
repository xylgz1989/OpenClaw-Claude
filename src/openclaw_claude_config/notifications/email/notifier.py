"""
Email notification channel
"""

from typing import Dict
from datetime import datetime

from ..notifier import NotificationChannel
from ...config.base import BaseConfigManager
from ...utils.logger import get_logger


class EmailNotifier(NotificationChannel):
    """Email notification channel"""

    def __init__(self, config_manager: BaseConfigManager):
        self.config = config_manager
        self.logger = get_logger(self.__class__.__name__)
        self.smtp_host = None
        self.smtp_port = None
        self.username = None
        self.password = None
        self.to_email = None
        self.enabled = False
        self._load_email_config()

    def _load_email_config(self):
        """Load email configuration"""
        try:
            notifications_config = self.config.get_notifications_config()
            email_config = notifications_config.get("channels", {}).get("email", {})

            self.enabled = email_config.get("enabled", False)
            self.smtp_host = self._expand_env_var(email_config.get("smtp_host"))
            self.smtp_port = self._expand_env_var(email_config.get("smtp_port", "587"))
            self.username = self._expand_env_var(email_config.get("username"))
            self.password = self._expand_env_var(email_config.get("password"))
            self.to_email = self._expand_env_var(email_config.get("to"))
        except Exception as e:
            self.logger.warning(f"Failed to load email config: {e}")
            self.enabled = False

    def _expand_env_var(self, value):
        """Expand environment variable"""
        if not value:
            return None
        if value.startswith('${') and value.endswith('}'):
            import os
            var_name = value[1:-1]
            return os.environ.get(var_name)
        return value

    def send(self, alert) -> Dict:
        """Send email notification"""
        try:
            if not self.enabled:
                return {'success': False, 'error': 'Email notifications not enabled'}

            if not self.smtp_host or not self.username or not self.password or not self.to_email:
                return {'success': False, 'error': 'Email configuration incomplete'}

            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['Subject'] = alert.title
            msg['To'] = self.to_email

            # Body
            body = f"""
{alert.message}

Provider: {alert.provider_id}
Level: {alert.level}
Time: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Quota Used: {alert.quota_used_percentage:.1f}% ({alert.quota_remaining} remaining)
"""

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Send
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            self.logger.info(f"Email sent for alert {alert.id}")
            return {'success': True, 'error': None}

        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return {'success': False, 'error': str(e)}

    def send_test(self, message: str) -> Dict:
        """Send test email"""
        test_alert = {
            'id': 'test',
            'provider_id': 'test',
            'level': 'info',
            'title': 'Test Notification',
            'message': message,
            'created_at': datetime.utcnow(),
            'quota_used_percentage': 0,
            'quota_remaining': 0
        }
        return self.send(test_alert)
