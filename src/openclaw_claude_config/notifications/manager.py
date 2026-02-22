"""
Notification Manager - Send notifications via multiple channels
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from datetime import datetime

from ..config.base import BaseConfigManager
from ..config.provider_manager import ProviderManager
from ..utils.logger import get_logger


class NotificationChannel(ABC):
    """Base class for notification channels"""

    @abstractmethod
    def send(self, alert) -> Dict:
        """Send notification
        Returns: {'success': bool, 'error': Optional[str]}
        """
        pass

    @abstractmethod
    def send_test(self, message: str) -> Dict:
        """Send test notification"""
        pass


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

    def _expand_env_var(self, value: Optional[str]) -> Optional[str]:
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


class WebhookNotifier(NotificationChannel):
    """Webhook notification channel"""

    def __init__(self, config_manager: BaseConfigManager):
        self.config = config_manager
        self.logger = get_logger(self.__class__.__name__)
        self.webhook_url = None
        self.enabled = False
        self._load_webhook_config()

    def _load_webhook_config(self):
        """Load webhook configuration"""
        try:
            notifications_config = self.config.get_notifications_config()
            webhook_config = notifications_config.get("channels", {}).get("webhook", {})

            self.enabled = webhook_config.get("enabled", False)
            self.webhook_url = self._expand_env_var(webhook_config.get("url"))
        except Exception as e:
            self.logger.warning(f"Failed to load webhook config: {e}")
            self.enabled = False

    def _expand_env_var(self, value: Optional[str]) -> Optional[str]:
        """Expand environment variable"""
        if not value:
            return None
        if value.startswith('${') and value.endswith('}'):
            import os
            var_name = value[1:-1]
            return os.environ.get(var_name)
        return value

    def send(self, alert) -> Dict:
        """Send webhook notification"""
        try:
            if not self.enabled:
                return {'success': False, 'error': 'Webhook notifications not enabled'}

            if not self.webhook_url:
                return {'success': False, 'error': 'Webhook URL not configured'}

            import requests

            payload = {
                'id': alert.id,
                'provider_id': alert.provider_id,
                'level': alert.level,
                'title': alert.title,
                'message': alert.message,
                'quota_used_percentage': alert.quota_used_percentage,
                'quota_remaining': alert.quota_remaining,
                'created_at': alert.created_at.isoformat()
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                self.logger.info(f"Webhook sent for alert {alert.id}")
                return {'success': True, 'error': None}
            else:
                self.logger.error(f"Webhook error: {response.status_code}")
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            self.logger.error(f"Error sending webhook: {e}")
            return {'success': False, 'error': str(e)}

    def send_test(self, message: str) -> Dict:
        """Send test webhook"""
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


class FeishuNotifier(NotificationChannel):
    """Feishu notification channel"""

    def __init__(self, config_manager: BaseConfigManager):
        self.config = config_manager
        self.logger = get_logger(self.__class__.__name__)
        self.webhook_url = None
        self.enabled = False
        self._load_feishu_config()

    def _load_feishu_config(self):
        """Load Feishu webhook URL"""
        try:
            notifications_config = self.config.get_notifications_config()
            feishu_config = notifications_config.get("channels", {}).get("feishu", {})
            self.enabled = feishu_config.get("enabled", False)
            self.webhook_url = self._expand_env_var(feishu_config.get("webhook_url"))
        except Exception as e:
            self.logger.warning(f"Failed to load feishu config: {e}")
            self.enabled = False

    def _expand_env_var(self, value: Optional[str]) -> Optional[str]:
        """Expand environment variable"""
        if not value:
            return None
        if value.startswith('${') and value.endswith('}'):
            import os
            var_name = value[1:-1]
            return os.environ.get(var_name)
        return value

    def send(self, alert) -> Dict:
        """Send Feishu notification"""
        try:
            if not self.enabled:
                return {'success': False, 'error': 'Feishu notifications not enabled'}

            if not self.webhook_url:
                return {'success': False, 'error': 'Feishu webhook URL not configured'}

            import requests

            payload = {
                "msg_type": "text",
                "content": {
                    "text": f"{alert.title}\n\n{alert.message}\n\nProvider: {alert.provider_id}\nLevel: {alert.level}\nTime: {alert.created_at.strftime('%Y-%m-%d %H:%M')}\n\nQuota Used: {alert.quota_used_percentage:.1f}% ({alert.quota_remaining} remaining)"
                }
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                self.logger.info(f"Feishu sent for alert {alert.id}")
                return {'success': True, 'error': None}
            else:
                self.logger.error(f"Feishu error: {response.status_code}")
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            self.logger.error(f"Error sending Feishu: {e}")
            return {'success': False, 'error': str(e)}

    def send_test(self, message: str) -> Dict:
        """Send test Feishu message"""
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


class NotificationManager:
    """Manage multiple notification channels"""

    def __init__(self, config_manager: ProviderManager):
        self.config_manager = config_manager
        self.logger = get_logger(self.__class__.__name__)
        self.channels: Dict[str, NotificationChannel] = {}

    def register_channel(self, name: str, channel: NotificationChannel) -> None:
        """Register a notification channel"""
        self.channels[name] = channel
        self.logger.info(f"Registered channel: {name}")

    def send_alert(self, alert, channels: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Send alert via specified channels (or all registered channels)"""
        results = {}

        target_channels = channels if channels else list(self.channels.keys())

        for channel_name in target_channels:
            if channel_name not in self.channels:
                results[channel_name] = {'success': False, 'error': 'Channel not found'}
                continue

            channel = self.channels[channel_name]
            result = channel.send(alert)
            results[channel_name] = result

        return results

    def send_test_message(self, message: str, channels: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Send test message via specified channels"""
        results = {}

        target_channels = channels if channels else list(self.channels.keys())

        for channel_name in target_channels:
            if channel_name not in self.channels:
                results[channel_name] = {'success': False, 'error': 'Channel not found'}
                continue

            channel = self.channels[channel_name]
            result = channel.send_test(message)
            results[channel_name] = result

        return results

    def cleanup_old_alerts(self, days_to_keep: int = 30) -> int:
        """Cleanup old alerts"""
        # TODO: Implement database cleanup
        self.logger.info(f"Cleaning up alerts older than {days_to_keep} days")
        return 0


def get_notification_manager(config_manager: Optional[ProviderManager] = None) -> NotificationManager:
    """Get notification manager instance"""
    if config_manager is None:
        from ..config.provider_manager import ProviderManager
        config_manager = ProviderManager()

    manager = NotificationManager(config_manager)

    # Register notification channels
    email_notifier = EmailNotifier(config_manager)
    if email_notifier.enabled:
        manager.register_channel("email", email_notifier)

    webhook_notifier = WebhookNotifier(config_manager)
    if webhook_notifier.enabled:
        manager.register_channel("webhook", webhook_notifier)

    feishu_notifier = FeishuNotifier(config_manager)
    if feishu_notifier.enabled:
        manager.register_channel("feishu", feishu_notifier)

    return manager
