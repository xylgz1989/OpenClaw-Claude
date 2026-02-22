"""
Notifications module for OpenClaw Claude Config
"""

from .manager import NotificationManager, get_notification_manager
from .email.notifier import EmailNotifier
from .webhook.notifier import WebhookNotifier
from .feishu.notifier import FeishuNotifier

__all__ = [
    'NotificationManager',
    'get_notification_manager',
    'EmailNotifier',
    'notifier',  # webhook.notifier
    'webhook.notifier',  # feishu.notifier
]
