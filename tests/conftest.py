"""
Test framework for OpenClaw Claude Config
"""

import pytest
import tempfile
import os
import json
from pathlib import Path

# 添加 src 到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from openclaw_claude_config.config.provider_manager import ProviderManager
from openclaw_claude_config.core.fallback_engine import FallbackEngine
from openclaw_claude_config.core.quota_monitor import QuotaMonitor
from openclaw_claude_config.core.alert_engine import AlertEngine, Alert, AlertLevel, AlertStatus


@pytest.fixture(scope="session")
def test_config_dir():
    """Create a temporary configuration directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def provider_manager(test_config_dir):
    """Create provider manager instance with test config"""
    config_path = Path(test_config_dir) / "settings.json"
    return ProviderManager(config_path)


@pytest.fixture
def fallback_engine(provider_manager):
    """Create fallback engine instance"""
    return FallbackEngine(provider_manager)


@pytest.fixture
def quota_monitor(provider_manager):
    """Create quota monitor instance"""
    return QuotaMonitor(provider_manager)


@pytest.fixture
def alert_engine(provider_manager):
    """Create alert engine instance"""
    return AlertEngine(provider_manager)


@pytest.fixture
def sample_providers():
    """Sample provider data"""
    return {
        "deepseek": {
            "id": "deepseek",
            "name": "DeepSeek",
            "api_endpoint": "https://api.deepseek.com/v1",
            "api_key": "test_key",
            "enabled": True,
            "priority": 10,
            "tier": "enterprise",
            "quota_limit": 1000000,
            "quota_type": "tokens",
            "health": 0.95
        },
        "glm": {
            "id": "glm",
            "name": "GLM",
            "api_endpoint": "https://open.bigmodel.cn/api/paas/v4",
            "api_key": "test_key",
            "enabled": True,
            "priority": 5,
            "tier": "professional",
            "quota_limit": 500000,
            "quota_type": "tokens",
            "health": 0.90
        },
        "anthropic": {
            "id": "anthropic",
            "name": "Anthropic",
            "api_endpoint": "https://api.anthropic.com/v1",
            "api_key": "test_key",
            "enabled": False,
            "priority": 3,
            "tier": "free",
            "quota_limit": 100000,
            "quota_type": "tokens",
            "health": 0.85
        }
    }
