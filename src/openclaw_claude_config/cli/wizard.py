"""
配置向导命令
"""

import sys
from typing import List
from .base import BaseCommand
from ..config.claude import ClaudeCodeConfigManager
from ..config.openclaw import OpenClawConfigManager
from ..core.connection import ConnectionValidator
from ..models.registry import ModelRegistry
from ..utils.security import get_api_key_interactive
from ..utils.logger import get_logger


class WizardCommand(BaseCommand):
    """交互式配置向导"""

    def __init__(self):
        super().__init__()
        self.claude_config = ClaudeCodeConfigManager()
        self.openclaw_config = OpenClawConfigManager()
        self.connection_validator = ConnectionValidator()
        self.model_registry = ModelRegistry()

    def execute(self, args: Any) -> int:
        """执行配置向导"""
        try:
            print("=" * 60)
            print("OpenClaw + Claude Code 配置向导")
            print("=" * 60)

            # 配置Claude Code
            if not self._configure_claude_code():
                return 1

            # 配置OpenClaw
            if not self._configure_openclaw():
                return 1

            print("\n" + "=" * 60)
            print("配置完成!")
            print("=" * 60)

            return 0
        except Exception as e:
            return self.handle_error(e)

    def _configure_claude_code(self) -> bool:
        """配置Claude Code"""
        print("\n[1/3] 配置Claude Code")
        print("-" * 40)

        # 列出预设
        self.claude_config.list_presets()

        # 选择预设
        preset = self._get_user_input("\n请选择预设", required=True)
        api_key = get_api_key_interactive(f"Claude Code ({preset})")

        # 应用预设
        try:
            self.claude_config.apply_preset(preset, api_key)
        except Exception as e:
            self.logger.error(f"应用预设失败: {e}")
            return False

        # 测试连接
        print("\n正在测试连接...")
        result = self._test_claude_connection()
        self.connection_validator.print_result(result)

        if not result["success"]:
            retry = self._get_user_input(
                "连接失败，是否重试? [y/N]", default="n"
            ).lower()
            if retry == "y":
                return self._configure_claude_code()

        # 创建.claudeignore
        create_ignore = self._get_user_input(
            "\n是否创建.claudeignore文件? [Y/n]", default="y"
        ).lower()
        if create_ignore in ["", "y"]:
            custom_patterns = self._get_custom_ignore_patterns()
            self.claude_config.create_claudeignore(custom_patterns)

        return True

    def _configure_openclaw(self) -> bool:
        """配置OpenClaw"""
        print("\n[2/3] 配置OpenClaw")
        print("-" * 40)

        # 列出可用模型
        self._list_available_models()

        # 选择模型
        model = self._get_user_input("\n请选择模型", required=True)
        api_key = get_api_key_interactive(f"OpenClaw ({model})")

        # 获取base_url（如果需要）
        base_url = None
        if not self._is_builtin_model(model):
            base_url = self._get_user_input("请输入Base URL", required=True)

        # 设置模型
        try:
            # 先测试连接
            if base_url:
                print("\n正在测试连接...")
                result = self.connection_validator.test_connection(
                    base_url, api_key, model, verify_ssl=True
                )
                self.connection_validator.print_result(result)

                if not result["success"]:
                    retry = self._get_user_input(
                        "连接失败，是否继续保存配置? [y/N]", default="n"
                    ).lower()
                    if retry != "y":
                        return False

            # 设置模型配置
            self.openclaw_config.set_model(
                model, api_key, base_url, test_connection=False
            )

            # 验证配置
            is_valid, messages = self.openclaw_config.validate_config()
            if is_valid:
                print("\n配置验证通过!")
            else:
                print("\n配置验证警告:")
                for msg in messages:
                    print(f"  - {msg}")

        except Exception as e:
            self.logger.error(f"配置OpenClaw失败: {e}")
            return False

        return True

    def _list_available_models(self):
        """列出可用模型"""
        print("\n可用模型:")
        all_models = self.model_registry.get_models("all")

        for category, providers in all_models.items():
            category_name = "国内模型" if category == "china" else "国际模型"
            print(f"\n{category_name}:")
            for provider_info in providers.values():
                for model in provider_info.get("models", []):
                    print(f"  {model.id} - {model.name}")

    def _get_custom_ignore_patterns(self) -> List[str]:
        """获取自定义忽略模式"""
        patterns = []
        print("\n请输入自定义忽略模式（每行一个，输入空行结束）:")
        while True:
            pattern = input("> ").strip()
            if not pattern:
                break
            patterns.append(pattern)
        return patterns

    def _is_builtin_model(self, model_id: str) -> bool:
        """检查是否为内置模型"""
        return self.model_registry.get_model_info(model_id) is not None

    def _test_claude_connection(self) -> dict:
        """测试Claude Code连接"""
        env = self.claude_config.get("env", {})
        base_url = env.get("ANTHROPIC_BASE_URL", "")
        api_key = env.get("ANTHROPIC_AUTH_TOKEN", "")
        model = env.get("ANTHROPIC_MODEL", "")

        if not base_url or not api_key:
            return {
                "success": False,
                "message": "配置不完整，缺少Base URL或API Key",
                "error_type": "config",
            }

        # 推断provider
        provider = None
        for p in [
            "anthropic",
            "openai",
            "zhipu",
            "qwen",
            "deepseek",
            "kimi",
            "minimax",
        ]:
            if p in base_url.lower():
                provider = p
                break

        return self.connection_validator.test_connection(
            base_url, api_key, model, provider, verify_ssl=True
        )

    def _get_user_input(
        self, prompt: str, required: bool = False, default: str = None
    ) -> str:
        """获取用户输入"""
        while True:
            if default:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "

            value = input(full_prompt).strip()

            if not value and default:
                return default
            elif not value and required:
                print("此项为必填项，请输入")
                continue
            else:
                return value
