"""
配置管理基类
"""

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from ..core.exceptions import ConfigError
from ..utils.logger import get_logger
from ..utils.security import set_secure_permissions


class BaseConfigManager(ABC):
    """配置管理器基类"""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.logger = get_logger(self.__class__.__name__)
        self.config: Dict[str, Any] = {}
        self.load_config()

    @abstractmethod
    def create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        pass

    @abstractmethod
    def validate_config(self) -> tuple[bool, List[str]]:
        """验证配置"""
        pass

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 清理JSON注释（如果需要）
                    content = self._clean_json_content(content)
                    self.config = json.loads(content)
                self.logger.info(f"已加载配置: {self.config_path}")
            except json.JSONDecodeError as e:
                self.logger.error(f"配置文件格式错误: {e}")
                raise ConfigError(f"配置文件格式错误: {e}")
            except Exception as e:
                self.logger.error(f"加载配置失败: {e}")
                raise ConfigError(f"加载配置失败: {e}")
        else:
            self.logger.info("配置文件不存在，创建默认配置")
            self.config = self.create_default_config()
            self.save_config()

        return self.config

    def save_config(self) -> bool:
        """保存配置"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # 创建备份
            if self.config_path.exists():
                self._create_backup()

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            # 设置安全权限
            set_secure_permissions(self.config_path)

            self.logger.info(f"配置已保存: {self.config_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            raise ConfigError(f"保存配置失败: {e}")

    def _clean_json_content(self, content: str) -> str:
        """清理JSON内容中的注释"""
        # 移除单行注释 //
        content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
        # 移除多行注释 /* ... */
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        # 移除尾随逗号
        content = re.sub(r",(\s*[}\]])", r"\1", content)
        return content

    def _create_backup(self):
        """创建配置备份"""
        backup_dir = self.config_path.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.config_path.stem}_{timestamp}.json"
        backup_path = backup_dir / backup_name

        import shutil

        shutil.copy2(self.config_path, backup_path)
        self.logger.info(f"已创建备份: {backup_path}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持嵌套键）"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """设置配置值（支持嵌套键）"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def update(self, updates: Dict[str, Any]):
        """批量更新配置"""
        for key, value in updates.items():
            self.set(key, value)

    def get_version(self) -> str:
        """获取配置版本"""
        return self.get("_schema.version", "1.0")

    def set_version(self, version: str):
        """设置配置版本"""
        self.set("_schema.version", version)
