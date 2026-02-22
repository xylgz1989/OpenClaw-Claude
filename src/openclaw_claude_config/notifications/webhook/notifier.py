"""
Webhook notification channel
"""

from typing import Dict
from datetime import datetime

from ..notifier import NotificationChannel
from ...config.base import BaseConfigManager
from ...utils.logger import get_logger


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
