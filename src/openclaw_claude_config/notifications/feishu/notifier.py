"""
Feishu notification channel
"""

from typing import Dict
from datetime import datetime

from ..notifier import NotificationChannel
from ...config.base import BaseConfigManager
from ...utils.logger import get_logger


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
