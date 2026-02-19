"""
OpenClaw配置管理器
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from .base import BaseConfigManager
from ..core.exceptions import ConfigError
from ..utils.logger import get_logger
from ..utils.security import set_secure_permissions, mask_sensitive_data


class OpenClawConfigManager(BaseConfigManager):
    """OpenClaw配置管理器"""

    CUSTOM_MODELS_PATH = Path.home() / ".openclaw" / "custom_models.json"

    # Fallback模型配置
    FALLBACK_MODELS = {
        "anthropic": ["anthropic/claude-haiku-4-20250514"],
        "zhipu": ["zhipu/glm-4.7"],
        "qwen": ["qwen/qwen3.5-plus"],
        "deepseek": ["deepseek/deepseek-chat"],
        "kimi": ["moonshot/kimi-k2.5"],
        "minimax": ["minimax/m2.5"],
    }

    def __init__(self):
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        super().__init__(config_path)
        self.custom_models = {}
        self.load_custom_models()

    def create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        return {
            "agent": {"model": "anthropic/claude-sonnet-4-20250514"},
            "gateway": {
                "port": 18789,
                "mode": "local",
                "bind": "loopback",
                "auth": {"mode": "token", "token": "${GATEWAY_TOKEN}"},
            },
            "models": {"anthropic": {"apiKey": "${ANTHROPIC_API_KEY}"}},
            "agents": {
                "defaults": {
                    "model": {
                        "primary": "anthropic/claude-sonnet-4-20250514",
                        "fallbacks": ["anthropic/claude-haiku-4-20250514"],
                    },
                    "workspace": "~/.openclaw/workspace",
                    "sandbox": {"mode": "non-main"},
                },
                "list": [],
            },
            "channels": {},
            "tools": {},
            "messages": {},
            "_schema": {"version": "2.1"},
        }

    def validate_config(self) -> Tuple[bool, List[str]]:
        """验证配置"""
        errors = []
        warnings = []

        # 检查必需字段
        required_fields = [
            "agent.model",
            "gateway.port",
            "agents.defaults.model.primary",
        ]

        for field in required_fields:
            if not self.get(field):
                errors.append(f"缺少必需配置项: {field}")

        # 检查端口范围
        port = self.get("gateway.port")
        if port:
            try:
                port_num = int(port)
                if not (1024 <= port_num <= 65535):
                    errors.append(f"Gateway端口 {port} 超出有效范围 (1024-65535)")
            except ValueError:
                errors.append(f"Gateway端口 '{port}' 不是有效的数字")

        # 检查模型配置
        primary_model = self.get("agents.defaults.model.primary")
        if primary_model:
            provider = primary_model.split("/")[0]
            if provider not in self.get("models", {}):
                warnings.append(
                    f"主模型 '{primary_model}' 的provider '{provider}' 未配置API密钥"
                )

        return len(errors) == 0, errors + warnings

    def load_custom_models(self) -> Dict[str, Any]:
        """加载自定义模型"""
        if self.CUSTOM_MODELS_PATH.exists():
            try:
                with open(self.CUSTOM_MODELS_PATH, "r", encoding="utf-8") as f:
                    self.custom_models = json.load(f)
                self.logger.info("已加载自定义模型")
            except Exception as e:
                self.logger.error(f"加载自定义模型失败: {e}")
                self.custom_models = {}
        else:
            self.custom_models = {}

        return self.custom_models

    def save_custom_models(self) -> bool:
        """保存自定义模型"""
        try:
            self.CUSTOM_MODELS_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(self.CUSTOM_MODELS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.custom_models, f, indent=2, ensure_ascii=False)

            # 设置安全权限
            set_secure_permissions(self.CUSTOM_MODELS_PATH)

            self.logger.info("自定义模型已保存")
            return True
        except Exception as e:
            self.logger.error(f"保存自定义模型失败: {e}")
            return False

    def set_model(
        self,
        model_id: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        test_connection: bool = True,
    ) -> bool:
        """设置模型（支持分层策略）"""
        # 解析模型ID
        parts = model_id.split("/")
        if len(parts) != 2:
            raise ConfigError(f"模型ID格式错误: {model_id} (应为 provider/model)")

        provider, model_name = parts

        # 更新agent配置
        self.set("agent.model", model_id)

        # 更新agents.defaults.model（分层策略）
        self.set("agents.defaults.model.primary", model_id)

        # 设置fallbacks
        fallbacks = self.FALLBACK_MODELS.get(provider, [])
        self.set("agents.defaults.model.fallbacks", fallbacks)

        # 更新models配置
        if provider not in self.get("models", {}):
            self.set(f"models.{provider}", {})

        if api_key:
            self.set(f"models.{provider}.apiKey", api_key)
        if base_url:
            self.set(f"models.{provider}.baseUrl", base_url)

        # 保存配置
        self.save_config()

        # 打印成功信息
        self.logger.info(f"已设置模型: {model_id}")
        self.logger.info(f"Fallbacks: {', '.join(fallbacks)}")
        if api_key:
            masked_key = mask_sensitive_data(api_key)
            self.logger.info(f"API Key: {masked_key}")

        return True

    def get_fallbacks(self, provider: str, model_name: str) -> List[str]:
        """获取fallback模型列表"""
        return self.FALLBACK_MODELS.get(provider, [])

    def add_custom_model(
        self,
        model_id: str,
        name: str,
        provider: str,
        api_endpoint: str,
        description: str = "",
    ) -> bool:
        """添加自定义模型"""
        self.custom_models[model_id] = {
            "name": name,
            "provider": provider,
            "api_endpoint": api_endpoint,
            "description": description,
        }

        return self.save_custom_models()

    def add_channel(self, channel_id: str, config: Dict) -> bool:
        """添加通道配置"""
        self.set(f"channels.{channel_id}", config)
        return self.save_config()

    def get_model_config(self, provider: str) -> Dict[str, Any]:
        """获取指定provider的配置"""
        return self.get(f"models.{provider}", {})

    def get_all_models_config(self) -> Dict[str, Any]:
        """获取所有模型配置（遮蔽敏感信息）"""
        models = self.get("models", {})
        masked_models = {}

        for provider, config in models.items():
            masked_config = config.copy()
            if "apiKey" in masked_config:
                masked_config["apiKey"] = mask_sensitive_data(masked_config["apiKey"])
            masked_models[provider] = masked_config

        return masked_models

    def list_custom_models(self):
        """列出自定义模型"""
        if not self.custom_models:
            print("\n暂无自定义模型")
            return

        print("\n自定义模型列表:")
        print("-" * 60)
        for model_id, model in self.custom_models.items():
            print(f"\n  {model_id}")
            print(f"    名称: {model['name']}")
            print(f"    Provider: {model['provider']}")
            print(f"    API端点: {model['api_endpoint']}")
            if model["description"]:
                print(f"    描述: {model['description']}")
