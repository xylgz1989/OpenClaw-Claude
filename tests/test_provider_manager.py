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
    config_data = {}
    config_data["hasCompletedOnboarding"] = True
    config_data["version"] = 2.0
    config_data["security"] = {}
    config_data["security"]["auth"] = {}
    config_data["security"]["auth"]["selectedType"] = "test"
    config_data["security"]["auth"]["apiKey"] = "test_key"
    config_data["security"]["auth"]["baseUrl"] = "https://test.com/api"
    config_data["model"] = "test-model"
    config_data["providers"] = {}
    config_data["fallback"] = {}
    config_data["fallback"]["enabled"] = False
    config_data["fallback"]["strategy"] = "balance"
    config_data["quota_monitoring"] = {}
    config_data["quota_monitoring"]["enabled"] = False
    config_data["notifications"] = {}
    config_data["notifications"]["enabled"] = False
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
    
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    
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
