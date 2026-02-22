"""
Provider Manager - Integrated with OpenClaw-Claude
"""

from typing import Dict, List, Optional
from pathlib import Path
import os
from datetime import datetime

from .base import BaseConfigManager
from ..models.registry import ModelRegistry
from ..utils.logger import get_logger


class ProviderManager(BaseConfigManager):
    """提供商管理器（集成到 OpenClaw-Claude）"""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path.home() / ".claude" / "settings.json"
        super().__init__(config_path)
        self.model_registry = ModelRegistry()
        self.logger = get_logger(self.__class__.__name__)

    def create_default_config(self) -> Dict[str, str]:
        """创建默认配置"""
        return {
            "env": {},
            "permissions": {"allowed": ["all"], "denied": []},
            "hooks": {},
            "_schema": {"version": self.DEFAULT_SCHEMA_VERSION},
            "providers": {},
            "fallback": {
                "enabled": False,
                "default_strategy": "balance",
                "available_strategies": ["balance", "tier", "cost", "latency", "success_rate"],
                "auto_fallback": False,
                "auto_fallback_triggers": ["quota_exhausted", "rate_limited", "provider_error"],
                "manual_trigger": False
            },
            "quota_monitoring": {
                "enabled": False,
                "check_interval_seconds": 300,
                "alert_thresholds": {
                    "warning": 80,
                    "critical": 90,
                    "exhausted": 95
                },
                "prediction_enabled": False,
                "prediction_days": 7
            },
            "notifications": {
                "enabled": False,
                "channels": {
                    "email": {
                        "enabled": False,
                        "smtp_host": "${SMTP_HOST}",
                        "smtp_port": "${SMTP_PORT:-587}",
                        "username": "${SMTP_USERNAME}",
                        "password": "${SMTP_PASSWORD}",
                        "to": "${ALERT_TO_EMAIL}"
                    },
                    "webhook": {
                        "enabled": False,
                        "url": "${WEBHOOK_URL}"
                    },
                    "feishu": {
                        "enabled": False,
                        "webhook_url": "${FEISHU_WEBHOOK_URL}"
                    }
                },
                "throttle": {
                    "cooldown_seconds": 600,
                    "max_alerts_per_hour": 10
                }
            },
            "cli": {
                "default_provider": "${DEFAULT_PROVIDER:-deepseek}",
                "show_fallback_events": False,
                "show_quota_usage": False,
                "log_level": "${LOG_LEVEL:-INFO}"
            }
        }

    def validate_config(self) -> tuple[bool, List[str]]:
        """验证配置"""
        errors = []

        # 验证 providers 配置
        providers = self.get_providers_config()
        for provider_id, config in providers.items():
            if not isinstance(config, dict):
                errors.append(f"提供商 {provider_id} 配置必须是字典")
                continue

            required_fields = ["name", "api_endpoint", "api_key"]
            for field in required_fields:
                if field not in config or not config[field]:
                    # 允许环境变量
                    if not (isinstance(config[field], str) and config[field].startswith("${") and config[field].endswith("}")):
                        errors.append(f"提供商 {provider_id} 缺少必需字段: {field}")

        # 验证 fallback 配置
        fallback_config = self.get_fallback_config()
        if fallback_config.get("enabled", False):
            default_strategy = fallback_config.get("default_strategy", "")
            if default_strategy and default_strategy not in ["balance", "tier", "cost", "latency", "success_rate"]:
                errors.append(f"无效的默认切换策略: {default_strategy}")

        # 验证 quota_monitoring 配置
        quota_config = self.get_quota_monitoring_config()
        if quota_config.get("enabled", False):
            alert_thresholds = quota_config.get("alert_thresholds", {})
            for level, value in alert_thresholds.items():
                if not isinstance(value, int) or not (0 <= value <= 100):
                    errors.append(f"无效的告警阈值 {level}: {value}")

        return len(errors) == 0, errors

    def add_provider(
        self,
        provider_id: str,
        name: str,
        api_endpoint: str,
        api_key: str,
        model: Optional[str] = None,
        quota_limit: Optional[int] = None,
        quota_type: Optional[str] = None,
        tier: Optional[str] = None,
        cost_per_1k_tokens: Optional[float] = None,
        priority: int = 0,
        enabled: bool = True,
        rate_limit_5h: bool = False
    ) -> bool:
        """添加提供商配置"""
        try:
            provider_config = {
                "name": name,
                "api_endpoint": api_endpoint,
                "api_key": api_key,
                "quota_limit": quota_limit,
                "quota_type": quota_type,
                "tier": tier,
                "cost_per_1k_tokens": cost_per_1k_tokens,
                "priority": priority,
                "enabled": enabled,
                "rate_limit_5h": rate_limit_5h
            }

            if model:
                provider_config["model"] = model

            self.set(f"providers.{provider_id}", provider_config)
            self.save_config()

            self.logger.info(f"已添加提供商: {provider_id}")
            return True

        except Exception as e:
            self.logger.error(f"添加提供商失败: {e}")
            return False

    def remove_provider(self, provider_id: str) -> bool:
        """删除提供商配置"""
        try:
            providers = self.get_providers_config()
            if provider_id not in providers:
                self.logger.warning(f"提供商不存在: {provider_id}")
                return False

            del providers[provider_id]
            self.set("providers", providers)
            self.save_config()

            self.logger.info(f"已删除提供商: {provider_id}")
            return True

        except Exception as e:
            self.logger.error(f"删除提供商失败: {e}")
            return False

    def enable_provider(self, provider_id: str) -> bool:
        """启用提供商"""
        try:
            self.set(f"providers.{provider_id}.enabled", True)
            self.save_config()
            self.logger.info(f"已启用提供商: {provider_id}")
            return True
        except Exception as e:
            self.logger.error(f"启用提供商失败: {e}")
            return False

    def disable_provider(self, provider_id: str) -> bool:
        """禁用提供商"""
        try:
            self.set(f"providers.{provider_id}.enabled", False)
            self.save_config()
            self.logger.info(f"已禁用提供商: {provider_id}")
            return True
        except Exception as e:
            self.logger.error(f"禁用提供商失败: {e}")
            return False

    def get_provider(self, provider_id: str) -> Optional[Dict]:
        """获取提供商配置"""
        providers = self.get_providers_config()
        return providers.get(provider_id)

    def list_providers(self, enabled_only: bool = True) -> Dict[str, Dict]:
        """列出所有提供商"""
        providers = self.get_providers_config()

        if enabled_only:
            return {pid: p for pid, p in providers.items() if p.get("enabled", True)}

        return providers

    def get_available_providers(self) -> List[str]:
        """获取可用提供商列表"""
        providers = self.list_providers(enabled_only=True)
        available = []

        for provider_id, config in providers.items():
            # 检查是否启用
            if not config.get("enabled", False):
                continue

            # 检查是否有 API Key
            api_key = config.get("api_key", "")
            if not api_key:
                continue

            # 检查是否是 5 小时限额中
            rate_limit_5h = config.get("rate_limit_5h", False)
            if rate_limit_5h:
                # TODO: 检查冷却时间
                continue

            available.append(provider_id)

        return available

    def enable_fallback(self, enabled: bool = True, default_strategy: str = "balance") -> bool:
        """启用/禁用智能切换"""
        try:
            self.set("fallback.enabled", enabled)
            if enabled:
                self.set("fallback.default_strategy", default_strategy)
            self.save_config()

            self.logger.info(f"智能切换已{'启用' if enabled else '禁用'}")
            return True

        except Exception as e:
            self.logger.error(f"启用智能切换失败: {e}")
            return False

    def enable_quota_monitoring(self, enabled: bool = True, check_interval: int = 300) -> bool:
        """启用/禁用配额监控"""
        try:
            self.set("quota_monitoring.enabled", enabled)
            if enabled:
                self.set("quota_monitoring.check_interval_seconds", check_interval)
            self.save_config()

            self.logger.info(f"配额监控已{'启用' if enabled else '禁用'}")
            return True

        except Exception as e:
            self.logger.error(f"启用配额监控失败: {e}")
            return False

    def import_from_preset(self, preset_id: str) -> bool:
        """从预设导入提供商"""
        try:
            # 获取预设信息
            all_presets = self.model_registry.get_models("all")

            if preset_id not in all_presets:
                self.logger.error(f"未知预设: {preset_id}")
                return False

            provider_info = all_presets[preset_id]

            # 创建提供商配置
            provider_config = {
                "name": provider_info["name"],
                "api_endpoint": provider_info["api_endpoint"],
                "api_key": f"${preset_id.upper()}_API_KEY}",
                "enabled": True,
                "priority": 0,
                "rate_limit_5h": preset_id in ["zhipu", "aliyun", "kimi", "minimax"]
            }

            self.set(f"providers.{preset_id}", provider_config)
            self.save_config()

            self.logger.info(f"已从预设导入提供商: {preset_id}")
            return True

        except Exception as e:
            self.logger.error(f"从预设导入失败: {e}")
            return False
