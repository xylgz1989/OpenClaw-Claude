"""
Unit tests for AlertEngine
"""

import pytest
from openclaw_claude_config.core.alert_engine import AlertEngine, Alert, AlertLevel, AlertStatus


class TestAlertEngine:
    """Test AlertEngine functionality"""

    def test_init(self, alert_engine):
        """Test AlertEngine initialization"""
        assert alert_engine is not None
        assert hasattr(alert_engine, 'provider_manager')
        assert hasattr(alert_engine, 'logger')

    def test_create_alert_info(self, alert_engine):
        """Test create_alert with INFO level"""
        alert = alert_engine.create_alert(
            provider_id="test_provider",
            level=AlertLevel.INFO,
            message="Test info alert"
        )
        assert alert is not None
        assert alert.provider_id == "test_provider"
        assert alert.level == AlertLevel.INFO
        assert alert.message == "Test info alert"

    def test_create_alert_warning(self, alert_engine):
        """Test create_alert with WARNING level"""
        alert = alert_engine.create_alert(
            provider_id="test_provider",
            level=AlertLevel.WARNING,
            message="Test warning alert",
            quota_used_percentage=85.0,
            quota_remaining=150000
        )
        assert alert is not None
        assert alert.level == AlertLevel.WARNING
        assert alert.quota_used_percentage == 85.0
        assert alert.quota_remaining == 150000

    def test_create_alert_critical(self, alert_engine):
        """Test create_alert with CRITICAL level"""
        alert = alert_engine.create_alert(
            provider_id="test_provider",
            level=AlertLevel.CRITICAL,
            message="Test critical alert",
            quota_used_percentage=95.0,
            quota_remaining=50000
        )
        assert alert is not None
        assert alert.level == AlertLevel.CRITICAL
        assert alert.quota_used_percentage == 95.0
        assert alert.quota_remaining == 50000

    def test_alert_to_dict(self, alert_engine):
        """Test Alert.to_dict()"""
        alert = alert_engine.create_alert(
            provider_id="test_provider",
            level=AlertLevel.INFO,
            message="Test alert"
        )
        assert alert is not None

        alert_dict = alert.to_dict()
        assert isinstance(alert_dict, dict)
        assert "id" in alert_dict
        assert "provider_id" in alert_dict
        assert "level" in alert_dict
        assert "message" in alert_dict
        assert "created_at" in alert_dict

    def test_get_alerts(self, alert_engine):
        """Test get_alerts"""
        alerts = alert_engine.get_alerts()
        assert isinstance(alerts, list)

    def test_get_alerts_with_filter(self, alert_engine):
        """Test get_alerts with filters"""
        alerts = alert_engine.get_alerts(provider_id="test_provider")
        assert isinstance(alerts, list)

        alerts = alert_engine.get_alerts(level=AlertLevel.WARNING)
        assert isinstance(alerts, list)

    def test_get_alert_stats(self, alert_engine):
        """Test get_alert_stats"""
        stats = alert_engine.get_alert_stats()
        assert isinstance(stats, dict)
        assert "total" in stats
        assert "by_status" in stats
        assert "by_level" in stats

    def test_should_send_alert(self, alert_engine):
        """Test should_send_alert"""
        should_send = alert_engine.should_send_alert(
            provider_id="test_provider",
            level=AlertLevel.WARNING
        )
        assert isinstance(should_send, bool)

    def test_mark_as_sent(self, alert_engine):
        """Test mark_as_sent"""
        alert = alert_engine.create_alert(
            provider_id="test_provider",
            level=AlertLevel.INFO,
            message="Test alert"
        )
        assert alert is not None

        result = alert_engine.mark_as_sent(alert.id)
        assert result is True

    def test_mark_as_failed(self, alert_engine):
        """Test mark_as_failed"""
        alert = alert_engine.create_alert(
            provider_id="test_provider",
            level=AlertLevel.INFO,
            message="Test alert"
        )
        assert alert is not None

        result = alert_engine.mark_as_failed(alert.id, "Test error")
        assert result is False

    def test_cleanup_old_alerts(self, alert_engine):
        """Test cleanup_old_alerts"""
        count = alert_engine.cleanup_old_alerts(days_to_keep=30)
        assert isinstance(count, int)
        assert count >= 0

    def test_alert_levels(self):
        """Test AlertLevel enum"""
        assert AlertLevel.INFO == "info"
        assert AlertLevel.WARNING == "warning"
        assert AlertLevel.CRITICAL == "critical"

    def test_alert_status(self):
        """Test AlertStatus enum"""
        assert AlertStatus.PENDING == "pending"
        assert AlertStatus.SENT == "sent"
        assert AlertStatus.FAILED == "failed"
        assert AlertStatus.ACKNOWLEDGED == "acknowledged"
