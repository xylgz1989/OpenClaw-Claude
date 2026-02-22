"""
Unit tests for ProviderManager
"""

import pytest
from pathlib import Path
import tempfile
import json
import os

from openclaw_claude_config.config.provider_manager import ProviderManager


@pytest.fixture
def temp_config():
    """Create temporary config file"""
    config = {
        "hasCompletedOnboarding": True,
        "version": 2.0,
        "security": {
            "auth": {
                "selectedType": "test",
                "apiKey": "test_key",
                "baseUrl": "https://test.com/api"
            }
        },
        "model": "test-model",
        "providers": {},
        "fallback": {"enabled": False, "strategy": "balance"},
        "quota_monitoring": {"enabled": False},
        "notifications": {"enabled": False}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
    
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    yield config_path
    
    if os.path.exists(config_path):
        os.unlink(config_path)


class TestProviderManager:
    """Test ProviderManager functionality"""

    def test_init(self, temp_config):
        """Test ProviderManager initialization"""
        manager = ProviderManager(Path(temp_config))
        assert manager is not None
        assert hasattr(manager, 'config')
        assert hasattr(manager, 'logger')

    def test_get_fallback_config(self, temp_config):
        """Test get_fallback_config"""
        manager = ProviderManager(Path(temp_config))
        config = manager.get_fallback_config()
        assert config is not None
        assert 'enabled' in config
        assert 'strategy' in config

    def test_get_quota_monitoring_config(self, temp_config):
        """Test get_quota_monitoring_config"""
        manager = ProviderManager(Path(temp_config))
        config = manager.get_quota_monitoring_config()
        assert config is not None
        assert 'enabled' in config
        assert 'check_interval_seconds' in config
        assert 'alert_thresholds' in config

    def test_get_notifications_config(self, temp_config):
        """Test get_notifications_config"""
        manager = ProviderManager(Path(temp_config))
        config = manager.get_notifications_config()
        assert config is not None
        assert 'channels' in config

    def test_list_providers(self, temp_config):
        """Test list_providers"""
        manager = ProviderManager(Path(temp_config))
        providers = manager.list_providers()
        assert isinstance(providers, dict)

    def test_get_provider(self, temp_config):
        """Test get_provider"""
        manager = ProviderManager(Path(temp_config))
        provider = manager.get_provider("deepseek")
        assert provider is None or isinstance(provider, dict)

    def test_add_provider(self, temp_config):
        """Test add_provider"""
        manager = ProviderManager(Path(temp_config))
        provider_data = {
            "id": "test_provider",
            "name": "Test Provider",
            "api_endpoint": "https://test.com/api",
            "api_key": "test_key",
            "enabled": True,
            "priority": 1,
            "tier": "free"
        }
        result = manager.add_provider("test_provider", provider_data)
        assert result is True

        provider = manager.get_provider("test_provider")
        assert provider is not None
        assert provider["name"] == "Test Provider"

        manager.remove_provider("test_provider")

    def test_remove_provider(self, temp_config):
        """Test remove_provider"""
        manager = ProviderManager(Path(temp_config))
        provider_data = {
            "id": "test_provider",
            "name": "Test Provider",
            "api_endpoint": "https://test.com/api",
            "api_key": "test_key",
            "enabled": True,
            "priority": 1,
            "tier": "free"
        }
        manager.add_provider("test_provider", provider_data)
        result = manager.remove_provider("test_provider")
        assert result is True

        provider = manager.get_provider("test_provider")
        assert provider is None

    def test_enable_provider(self, temp_config):
        """Test enable_provider"""
        manager = ProviderManager(Path(temp_config))
        provider_data = {
            "id": "test_provider",
            "name": "Test Provider",
            "api_endpoint": "https://test.com/api",
            "api_key": "test_key",
            "enabled": False,
            "priority": 1,
            "tier": "free"
        }
        manager.add_provider("test_provider", provider_data)
        result = manager.enable_provider("test_provider")
        assert result is True

        provider = manager.get_provider("test_provider")
        assert provider is not None
        assert provider.get("enabled") is True

        manager.remove_provider("test_provider")

    def test_disable_provider(self, temp_config):
        """Test disable_provider"""
        manager = ProviderManager(Path(temp_config))
        provider_data = {
            "id": "test_provider",
            "name": "Test Provider",
            "api_endpoint": "https://test.com/api",
            "api_key": "test_key",
            "enabled": True,
            "priority": 1,
            "tier": "free"
        }
        manager.add_provider("test_provider", provider_data)
        result = manager.disable_provider("test_provider")
        assert result is True

        provider = manager.get_provider("test_provider")
        assert provider is not None
        assert provider.get("enabled") is False

        manager.remove_provider("test_provider")

    def test_get_available_providers(self, temp_config):
        """Test get_available_providers"""
        manager = ProviderManager(Path(temp_config))
        manager.add_provider("enabled1", {
            "id": "enabled1",
            "name": "Enabled 1",
            "enabled": True,
            "api_endpoint": "https://test1.com/api"
        })
        manager.add_provider("disabled1", {
            "id": "disabled1",
            "name": "Disabled 1",
            "enabled": False,
            "api_endpoint": "https://test2.com/api"
        })

        available = manager.get_available_providers()
        assert isinstance(available, list)
        assert "enabled1" in available
        assert "disabled1" not in available

        manager.remove_provider("enabled1")
        manager.remove_provider("disabled1")
