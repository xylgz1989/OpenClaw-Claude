"""
测试配置文件
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from openclaw_claude_config.config.claude import ClaudeCodeConfigManager
from openclaw_claude_config.config.openclaw import OpenClawConfigManager
from openclaw_claude_config.core.exceptions import ConfigError, ValidationError


class TestClaudeCodeConfigManager:
    """测试Claude Code配置管理器"""

    def test_create_default_config(self):
        """测试创建默认配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_settings.json"
            with patch.object(
                ClaudeCodeConfigManager,
                "CUSTOM_PRESETS_PATH",
                Path(tmpdir) / "custom_presets.json",
            ):
                manager = ClaudeCodeConfigManager.__new__(ClaudeCodeConfigManager)
                manager.config_path = config_path
                manager.logger = MagicMock()
                manager.config = {}
                manager.custom_presets = {}
                manager.config = manager.create_default_config()

                assert "env" in manager.config
                assert "permissions" in manager.config
                assert "hooks" in manager.config
                assert manager.config["_schema"]["version"] == "2.0"

    def test_apply_preset(self):
        """测试应用预设"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_settings.json"
            with patch.object(
                ClaudeCodeConfigManager,
                "CUSTOM_PRESETS_PATH",
                Path(tmpdir) / "custom_presets.json",
            ):
                manager = ClaudeCodeConfigManager.__new__(ClaudeCodeConfigManager)
                manager.config_path = config_path
                manager.logger = MagicMock()
                manager.config = manager.create_default_config()
                manager.custom_presets = {}

                # 测试应用内置预设
                result = manager.apply_preset(
                    "zhipu", "test_api_key", model="test-model"
                )
                assert result is True
                assert manager.get("env.ANTHROPIC_API_KEY") == "test_api_key"
                assert (
                    manager.get("env.ANTHROPIC_BASE_URL")
                    == "https://open.bigmodel.cn/api/anthropic"
                )
                assert manager.get("env.ANTHROPIC_MODEL") == "test-model"

    def test_apply_invalid_preset(self):
        """测试应用无效预设"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_settings.json"
            with patch.object(
                ClaudeCodeConfigManager,
                "CUSTOM_PRESETS_PATH",
                Path(tmpdir) / "custom_presets.json",
            ):
                manager = ClaudeCodeConfigManager.__new__(ClaudeCodeConfigManager)
                manager.config_path = config_path
                manager.logger = MagicMock()
                manager.config = manager.create_default_config()
                manager.custom_presets = {}

                with pytest.raises(ConfigError):
                    manager.apply_preset("invalid_preset", "test_api_key")

    def test_add_custom_preset(self):
        """测试添加自定义预设"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_settings.json"
            custom_presets_path = Path(tmpdir) / "custom_presets.json"
            with patch.object(
                ClaudeCodeConfigManager, "CUSTOM_PRESETS_PATH", custom_presets_path
            ):
                with patch(
                    "openclaw_claude_config.config.claude.set_secure_permissions",
                    return_value=True,
                ):
                    manager = ClaudeCodeConfigManager.__new__(ClaudeCodeConfigManager)
                    manager.config_path = config_path
                    manager.logger = MagicMock()
                    manager.config = manager.create_default_config()
                    manager.custom_presets = {}

                    models = {
                        "opus": "test-opus",
                        "sonnet": "test-sonnet",
                        "haiku": "test-haiku",
                    }

                    result = manager.add_custom_preset(
                        "test_provider",
                        "Test Provider",
                        "Test description",
                        "https://api.test.com",
                        models,
                    )
                    assert result is True
                    assert "test_provider" in manager.custom_presets

    def test_validate_config(self):
        """测试配置验证"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_settings.json"
            with patch.object(
                ClaudeCodeConfigManager,
                "CUSTOM_PRESETS_PATH",
                Path(tmpdir) / "custom_presets.json",
            ):
                manager = ClaudeCodeConfigManager.__new__(ClaudeCodeConfigManager)
                manager.config_path = config_path
                manager.logger = MagicMock()
                manager.config = manager.create_default_config()
                manager.custom_presets = {}

                # 空配置应该验证失败
                is_valid, errors = manager.validate_config()
                assert is_valid is False
                assert len(errors) > 0

                # 添加必需的环境变量
                manager.set("env.ANTHROPIC_AUTH_TOKEN", "test_token")
                manager.set("env.ANTHROPIC_API_KEY", "test_key")
                manager.set("env.ANTHROPIC_BASE_URL", "https://api.test.com")

                is_valid, errors = manager.validate_config()
                assert is_valid is True
                assert len(errors) == 0


class TestOpenClawConfigManager:
    """测试OpenClaw配置管理器"""

    def test_create_default_config(self):
        """测试创建默认配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_openclaw.json"
            with patch.object(
                OpenClawConfigManager,
                "CUSTOM_MODELS_PATH",
                Path(tmpdir) / "custom_models.json",
            ):
                manager = OpenClawConfigManager.__new__(OpenClawConfigManager)
                manager.config_path = config_path
                manager.logger = MagicMock()
                manager.config = {}
                manager.custom_models = {}
                manager.config = manager.create_default_config()

                assert "agent" in manager.config
                assert "gateway" in manager.config
                assert "models" in manager.config
                assert "agents" in manager.config
                assert manager.config["_schema"]["version"] == "2.1"

    def test_set_model(self):
        """测试设置模型"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_openclaw.json"
            with patch.object(
                OpenClawConfigManager,
                "CUSTOM_MODELS_PATH",
                Path(tmpdir) / "custom_models.json",
            ):
                manager = OpenClawConfigManager.__new__(OpenClawConfigManager)
                manager.config_path = config_path
                manager.logger = MagicMock()
                manager.config = manager.create_default_config()
                manager.custom_models = {}

                result = manager.set_model(
                    "test_provider/test_model", "test_api_key", "https://api.test.com"
                )
                assert result is True
                assert manager.get("agent.model") == "test_provider/test_model"
                assert manager.get("models.test_provider.apiKey") == "test_api_key"
                assert (
                    manager.get("models.test_provider.baseUrl")
                    == "https://api.test.com"
                )

    def test_set_invalid_model_id(self):
        """测试设置无效模型ID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_openclaw.json"
            with patch.object(
                OpenClawConfigManager,
                "CUSTOM_MODELS_PATH",
                Path(tmpdir) / "custom_models.json",
            ):
                manager = OpenClawConfigManager.__new__(OpenClawConfigManager)
                manager.config_path = config_path
                manager.logger = MagicMock()
                manager.config = manager.create_default_config()
                manager.custom_models = {}

                with pytest.raises(ConfigError):
                    manager.set_model("invalid_model_id", "test_api_key")

    def test_validate_config(self):
        """测试配置验证"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_openclaw.json"
            with patch.object(
                OpenClawConfigManager,
                "CUSTOM_MODELS_PATH",
                Path(tmpdir) / "custom_models.json",
            ):
                manager = OpenClawConfigManager.__new__(OpenClawConfigManager)
                manager.config_path = config_path
                manager.logger = MagicMock()
                manager.config = manager.create_default_config()
                manager.custom_models = {}

                # 默认配置应该验证通过
                is_valid, errors = manager.validate_config()
                assert is_valid is True

                # 设置无效端口
                manager.set("gateway.port", "invalid_port")
                is_valid, errors = manager.validate_config()
                assert is_valid is False
                assert any("端口" in error for error in errors)

    def test_add_custom_model(self):
        """测试添加自定义模型"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_openclaw.json"
            custom_models_path = Path(tmpdir) / "custom_models.json"
            with patch.object(
                OpenClawConfigManager, "CUSTOM_MODELS_PATH", custom_models_path
            ):
                with patch(
                    "openclaw_claude_config.config.openclaw.set_secure_permissions",
                    return_value=True,
                ):
                    manager = OpenClawConfigManager.__new__(OpenClawConfigManager)
                    manager.config_path = config_path
                    manager.logger = MagicMock()
                    manager.config = manager.create_default_config()
                    manager.custom_models = {}

                    result = manager.add_custom_model(
                        "test_provider/test_model",
                        "Test Model",
                        "test_provider",
                        "https://api.test.com",
                        "Test description",
                    )
                    assert result is True
                    assert "test_provider/test_model" in manager.custom_models


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
