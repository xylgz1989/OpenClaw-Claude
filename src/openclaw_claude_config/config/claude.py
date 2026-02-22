"""
Claude Code配置管理器
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from .base import BaseConfigManager
from ..core.exceptions import ConfigError
from ..utils.security import set_secure_permissions, mask_sensitive_data


class ClaudeCodeConfigManager(BaseConfigManager):
    """Claude Code配置管理器"""

    CLAUDEIGNORE_PATH = Path.home() / ".claudeignore"
    CUSTOM_PRESETS_PATH = Path.home() / ".claude" / "custom_presets.json"

    # 内置预设
    BUILTIN_PRESETS = {
        "zhipu": {
            "name": "智谱 GLM",
            "description": "国产GLM模型，编程能力强",
            "base_url": "https://open.bigmodel.cn/api/anthropic",
            "models": {
                "opus": "glm-5",
                "sonnet": "glm-4.7",
                "haiku": "glm-4.5-air",
            },
        },
        "zai": {
            "name": "Z.AI Coding",
            "description": "智谱Coding Plan专用端点",
            "base_url": "https://api.z.ai/api/coding/paas/v4",
            "models": {
                "opus": "glm-5",
                "sonnet": "glm-4.7",
                "haiku": "glm-4.5-air",
            },
        },
        "aliyun": {
            "name": "阿里云百炼",
            "description": "通义千问模型",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "models": {
                "opus": "qwen3.5-plus",
                "sonnet": "qwen3.5-plus",
                "haiku": "qwen3.5-turbo",
            },
        },
        "deepseek": {
            "name": "DeepSeek",
            "description": "深度求索，价格优惠",
            "base_url": "https://api.deepseek.com/anthropic",
            "models": {
                "opus": "deepseek-v4",
                "sonnet": "deepseek-chat",
                "haiku": "deepseek-chat",
            },
        },
        "kimi": {
            "name": "Kimi (Moonshot)",
            "description": "月之暗面，长上下文",
            "base_url": "https://api.moonshot.cn/anthropic",
            "models": {
                "opus": "kimi-k2.5",
                "sonnet": "kimi-k2.5",
                "haiku": "kimi-k2.5",
            },
        },
        "minimax": {
            "name": "MiniMax",
            "description": "MiniMax M2.5",
            "base_url": "https://api.minimaxi.com/anthropic",
            "models": {"opus": "m2.5", "sonnet": "m2.5", "haiku": "m2.5"},
        },
        "anthropic": {
            "name": "Anthropic官方",
            "description": "Claude官方API",
            "base_url": "https://api.anthropic.com",
            "models": {
                "opus": "claude-opus-4-5",
                "sonnet": "claude-sonnet-4-20250514",
                "haiku": "claude-haiku-4-20250514",
            },
        },
        "siliconflow": {
            "name": "硅基流动",
            "description": "开源模型推理平台",
            "base_url": "https://api.siliconflow.cn/v1",
            "models": {
                "opus": "Qwen/Qwen3.5-397B-A17B",
                "sonnet": "Qwen/Qwen3.5-Plus",
                "haiku": "Qwen/Qwen3.5-Turbo",
            },
        },
        "openrouter": {
            "name": "OpenRouter",
            "description": "全球模型API集市",
            "base_url": "https://openrouter.ai/api/v1",
            "models": {
                "opus": "anthropic/claude-opus-4-5",
                "sonnet": "anthropic/claude-sonnet-4",
                "haiku": "anthropic/claude-haiku-4",
            },
        },
    }

    # 默认.claudeignore内容
    DEFAULT_CLAUDEIGNORE = """# 依赖目录
node_modules/
venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/

# 构建输出
dist/
build/
*.egg-info/

# 日志文件
*.log
logs/

# 临时文件
*.tmp
*.temp
.DS_Store
Thumbs.db

# 版本控制
.git/
.gitignore
.svn/

# IDE配置
.vscode/
.idea/
*.swp
*.swo

# 大型资源文件
*.mp4
*.mp3
*.avi
*.mov
*.zip
*.tar.gz
*.rar

# 测试数据
test-data/
fixtures/
"""

    def __init__(self):
        settings_path = Path.home() / ".claude" / "settings.json"
        super().__init__(settings_path)
        self.custom_presets = {}
        self.load_custom_presets()

    def create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        return {
            "env": {},
            "permissions": {"allowed": ["all"], "denied": []},
            "hooks": {},
            "_schema": {"version": "2.0"},
        }

    def validate_config(self) -> tuple[bool, List[str]]:
        """验证配置"""
        errors = []

        # 检查必需的环境变量
        required_env = ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"]
        for key in required_env:
            if not self.get(f"env.{key}"):
                errors.append(f"缺少必需的环境变量: {key}")

        # 检查Base URL格式
        base_url = self.get("env.ANTHROPIC_BASE_URL")
        if base_url and not base_url.startswith(("http://", "https://")):
            errors.append("ANTHROPIC_BASE_URL必须以http://或https://开头")

        return len(errors) == 0, errors

    def load_custom_presets(self) -> Dict[str, Any]:
        """加载自定义预设"""
        if self.CUSTOM_PRESETS_PATH.exists():
            try:
                with open(
                    self.CUSTOM_PRESETS_PATH, "r", encoding="utf-8"
                ) as f:
                    self.custom_presets = json.load(f)
                self.logger.info("已加载自定义预设")
            except Exception as e:
                self.logger.error(f"加载自定义预设失败: {e}")
                self.custom_presets = {}
        else:
            self.custom_presets = {}

        return self.custom_presets

    def save_custom_presets(self) -> bool:
        """保存自定义预设"""
        try:
            self.CUSTOM_PRESETS_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(self.CUSTOM_PRESETS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.custom_presets, f, indent=2, ensure_ascii=False)

            # 设置安全权限
            set_secure_permissions(self.CUSTOM_PRESETS_PATH)

            self.logger.info("自定义预设已保存")
            return True
        except Exception as e:
            self.logger.error(f"保存自定义预设失败: {e}")
            return False

    def apply_preset(
        self,
        preset_id: str,
        api_key: str,
        model: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """应用预设配置"""
        # 合并内置预设和自定义预设
        all_presets = {**self.BUILTIN_PRESETS, **self.custom_presets}

        if preset_id not in all_presets:
            available = ", ".join(all_presets.keys())
            raise ConfigError(f"未知预设: {preset_id}。可用预设: {available}")

        preset = all_presets[preset_id]

        # 构建环境变量配置
        env_config = {
            "ANTHROPIC_AUTH_TOKEN": api_key,
            "ANTHROPIC_API_KEY": api_key,
            "ANTHROPIC_BASE_URL": preset["base_url"],
        }

        # 设置模型
        if model:
            env_config["ANTHROPIC_MODEL"] = model
        else:
            env_config["ANTHROPIC_MODEL"] = preset["models"]["sonnet"]

        # 添加分层模型配置
        env_config["ANTHROPIC_DEFAULT_OPUS_MODEL"] = preset["models"].get(
            "opus", preset["models"]["sonnet"]
        )
        env_config["ANTHROPIC_DEFAULT_SONNET_MODEL"] = preset["models"].get(
            "sonnet", preset["models"]["sonnet"]
        )
        env_config["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = preset["models"].get(
            "haiku", preset["models"]["sonnet"]
        )
        env_config["ANTHROPIC_SMALL_FAST_MODEL"] = preset["models"].get(
            "haiku", preset["models"]["sonnet"]
        )

        # 更新配置
        self.update({"env": env_config})

        # 保存配置
        self.save_config()

        # 打印成功信息（遮蔽API Key）
        masked_key = mask_sensitive_data(api_key)
        self.logger.info(f"已应用预设: {preset['name']}")
        self.logger.info(f"描述: {preset['description']}")
        self.logger.info(f"Base URL: {preset['base_url']}")
        self.logger.info(f"API Key: {masked_key}")
        self.logger.info(f"默认模型: {env_config['ANTHROPIC_MODEL']}")
        self.logger.info("提示: 重启Claude Code使配置生效")

        return True

    def add_custom_preset(
        self,
        preset_id: str,
        name: str,
        description: str,
        base_url: str,
        models: Dict[str, str],
    ) -> bool:
        """添加自定义预设"""
        if preset_id in self.BUILTIN_PRESETS:
            raise ConfigError(
                f"预设ID '{preset_id}' 与内置预设冲突，请使用其他ID"
            )

        self.custom_presets[preset_id] = {
            "name": name,
            "description": description,
            "base_url": base_url,
            "models": models,
        }

        return self.save_custom_presets()

    def create_claudeignore(
        self, custom_patterns: Optional[List[str]] = None
    ) -> bool:
        """创建.claudeignore文件"""
        content = self.DEFAULT_CLAUDEIGNORE

        if custom_patterns:
            content += "\n\n# 自定义规则\n"
            for pattern in custom_patterns:
                content += f"{pattern}\n"

        try:
            with open(self.CLAUDEIGNORE_PATH, "w", encoding="utf-8") as f:
                f.write(content)

            # 设置权限
            set_secure_permissions(self.CLAUDEIGNORE_PATH)

            self.logger.info(f"已创建.claudeignore: {self.CLAUDEIGNORE_PATH}")
            return True
        except Exception as e:
            self.logger.error(f"创建.claudeignore失败: {e}")
            return False

    def list_presets(self):
        """列出所有可用预设"""
        print("\n内置预设配置:")
        print("-" * 60)
        for preset_id, preset in self.BUILTIN_PRESETS.items():
            print(f"\n  [{preset_id}] {preset['name']}")
            print(f"      描述: {preset['description']}")
            print(f"      Base URL: {preset['base_url']}")
            print(
                f"      模型: Opus={preset['models']['opus']}, "
                f"Sonnet={preset['models']['sonnet']}"
            )

        if self.custom_presets:
            print("\n自定义预设配置:")
            print("-" * 60)
            for preset_id, preset in self.custom_presets.items():
                print(f"\n  [{preset_id}] {preset['name']}")
                print(f"      描述: {preset['description']}")
                print(f"      Base URL: {preset['base_url']}")

    def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置（遮蔽敏感信息）"""
        config = self.config.copy()
        if "env" in config:
            env = config["env"].copy()
            for key in env:
                if "KEY" in key or "TOKEN" in key:
                    env[key] = mask_sensitive_data(env[key])
            config["env"] = env
        return config
