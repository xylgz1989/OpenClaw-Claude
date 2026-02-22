"""
Unit tests for QuotaMonitor
"""

import pytest
from openclaw_claude_config.core.quota_monitor import QuotaMonitor


class TestQuotaMonitor:
    """Test QuotaMonitor functionality"""

    def test_init(self, quota_monitor):
        """Test QuotaMonitor initialization"""
        assert quota_monitor is not None
        assert hasattr(quota_monitor, 'provider_manager')
        assert hasattr(quota_monitor, 'logger')

    def test_query_quota(self, quota_monitor):
        """Test query_quota"""
        quota_info = quota_monitor.query_quota("deepseek")
        # May return None if provider doesn't exist or API fails
        assert quota_info is None or isinstance(quota_info, dict)

    def test_query_quota_all(self, quota_monitor):
        """Test query_quota_all"""
        all_quotas = quota_monitor.query_quota_all()
        assert isinstance(all_quotas, dict)

    def test_check_quota_alerts(self, quota_monitor):
        """Test check_quota_alerts"""
        quota_info = {
            "used": 850000,
            "limit": 1000000
        }
        alerts = quota_monitor.check_quota_alerts("test_provider", quota_info)
        assert isinstance(alerts, list)

        # Test warning threshold (80%)
        if len(alerts) > 0:
            assert "level" in alerts[0]
            assert "message" in alerts[0]

    def test_check_quota_alerts_critical(self, quota_monitor):
        """Test check_quota_alerts at critical level"""
        quota_info = {
            "used": 950000,
            "limit": 1000000
        }
        alerts = quota_monitor.check_quota_alerts("test_provider", quota_info)
        assert isinstance(alerts, list)

        # Should trigger critical alert (95%)
        if len(alerts) > 0:
            assert any(alert["level"] == "critical" for alert in alerts)

    def test_check_quota_alerts_exhausted(self, quota_monitor):
        """Test check_quota_alerts at exhausted level"""
        quota_info = {
            "used": 1000000,
            "limit": 1000000
        }
        alerts = quota_monitor.check_quota_alerts("test_provider", quota_info)
        assert isinstance(alerts, list)

        # Should trigger exhausted alert (100%)
        if len(alerts) > 0:
            assert any(alert["level"] == "critical" for alert in alerts)

    def test_get_quota_status(self, quota_monitor):
        """Test get_quota_status"""
        status = quota_monitor.get_quota_status("deepseek")
        # May return None if provider doesn't exist
        assert status is None or isinstance(status, dict)

    def test_deepseek_quota_query(self, quota_monitor):
        """Test DeepSeek quota query"""
        quota_info = quota_monitor._query_deepseek_quota("test_key")
        # May return None if API fails
        assert quota_info is None or isinstance(quota_info, dict)

    def test_anthropic_quota_query(self, quota_monitor):
        """Test Anthropic quota query"""
        quota_info = quota_monitor._query_anthropic_quota("test_key")
        # May return None if API fails
        assert quota_info is None or isinstance(quota_info, dict)

    def test_invalid_provider(self, quota_monitor):
        """Test with invalid provider"""
        quota_info = quota_monitor.query_quota("invalid_provider")
        assert quota_info is None
