"""
Notifier base class
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional

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
