"""
Unit tests for ProviderManager
"""

import pytest
from openclaw_claude_config.config.provider_manager import ProviderManager


class TestProviderManager:
    """Test ProviderManager functionality"""

    def test_init(self):
        """Test ProviderManager initialization"""
        manager = ProviderManager()
        assert manager is not None
        assert hasattr(manager, 'config')
        assert hasattr(manager, 'logger')

    def test_get_fallback_config(self, provider_manager):
        """Test get_fallback_config"""
        config = provider_manager.get_fallback_config()
        assert config is not None
        assert 'enabled' in config
        assert 'strategy' in config

    def test_get_quota_monitoring_config(self, provider_manager):
        """Test get_quota_monitoring_config"""
        config = provider_manager.get_quota_monitoring_config()
        assert config is not None
        assert 'enabled' in config
        assert 'check_interval_seconds' in config
        assert 'alert_thresholds' in config

    def test_get_notifications_config(self, provider_manager):
        """Test get_notifications_config"""
        config = provider_manager.get_notifications_config()
        assert config is not None
        assert 'channels' in config

    def test_list_providers(self, provider_manager):
        """Test list_providers"""
        providers = provider_manager.list_providers()
        assert isinstance(providers, dict)

    def test_get_provider(self, provider_manager):
        """Test get_provider"""
        provider = provider_manager.get_provider("deepseek")
        # May be None if provider doesn't exist
        assert provider is None or isinstance(provider, dict)

    def test_add_provider(self, provider_manager):
        """Test add_provider"""
        provider_data = {
            "id": "test_provider",
            "name": "Test Provider",
            "api_endpoint": "https://test.com/api",
            "api_key": "test_key",
            "enabled": True,
            "priority": 1,
            "tier": "free"
        }
        result = provider_manager.add_provider("test_provider", provider_data)
        assert result is True

        # Verify provider was added
        provider = provider_manager.get_provider("test_provider")
        assert provider is not None
        assert provider["name"] == "Test Provider"

        # Cleanup
        provider_manager.remove_provider("test_provider")

    def test_remove_provider(self, provider_manager):
        """Test remove_provider"""
        # First add a provider
        provider_data = {
            "id": "test_provider",
            "name": "Test Provider",
            "api_endpoint": "https://test.com/api",
            "api_key": "test_key",
            "enabled": True,
            "priority": 1,
            "tier": "free"
        }
        provider_manager.add_provider("test_provider", provider_data)

        # Now remove it
        result = provider_manager.remove_provider("test_provider")
        assert result is True

        # Verify provider was removed
        provider = provider_manager.get_provider("test_provider")
        assert provider is None

    def test_enable_provider(self, provider_manager):
        """Test enable_provider"""
        # First add a provider
        provider_data = {
            "id": "test_provider",
            "name": "Test Provider",
            "api_endpoint": "https://test.com/api",
            "api_key": "test_key",
            "enabled": False,
            "priority": 1,
            "tier": "free"
        }
        provider_manager.add_provider("test_provider", provider_data)

        # Enable it
        result = provider_manager.enable_provider("test_provider")
        assert result is True

        # Verify it's enabled
        provider = provider_manager.get_provider("test_provider")
        assert provider is not None
        assert provider.get("enabled") is True

        # Cleanup
        provider_manager.remove_provider("test_provider")

    def test_disable_provider(self, provider_manager):
        """Test disable_provider"""
        # First add a provider
        provider_data = {
            "id": "test_provider",
            "name": "Test Provider",
            "api_endpoint": "https://test.com/api",
            "api_key": "test_key",
            "enabled": True,
            "priority": 1,
            "tier": "free"
        }
        provider_manager.add_provider("test_provider", provider_data)

        # Disable it
        result = provider_manager.disable_provider("test_provider")
        assert result is True

        # Verify it's disabled
        provider = provider_manager.get_provider("test_provider")
        assert provider is not None
        assert provider.get("enabled") is False

        # Cleanup
        provider_manager.remove_provider("test_provider")

    def test_get_available_providers(self, provider_manager):
        """Test get_available_providers"""
        # Add some test providers
        provider_manager.add_provider("enabled1", {
            "id": "enabled1",
            "name": "Enabled 1",
            "enabled": True,
            "api_endpoint": "https://test1.com/api"
        })
        provider_manager.add_provider("disabled1", {
            "id": "disabled1",
            "name": "Disabled 1",
            "enabled": False,
            "api_endpoint": "https://test2.com/api"
        })

        # Get available providers
        available = provider_manager.get_available_providers()
        assert isinstance(available, list)
        # Should only include enabled providers
        assert "enabled1" in available
        assert "disabled1" not in available

        # Cleanup
        provider_manager.remove_provider("enabled1")
        provider_manager.remove_provider("disabled1")
