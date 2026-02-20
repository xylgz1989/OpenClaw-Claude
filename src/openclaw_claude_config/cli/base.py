"""
CLI命令基类
"""

from abc import ABC, abstractmethod
from typing import Any
from ..core.exceptions import ConfigError
from ..utils.logger import get_logger


class BaseCommand(ABC):
    """CLI命令基类"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def execute(self, args: Any) -> int:
        """执行命令

        Args:
            args: 命令参数

        Returns:
            退出码（0表示成功）
        """
        pass

    def handle_error(self, error: Exception) -> int:
        """处理错误

        Args:
            error: 异常对象

        Returns:
            退出码
        """
        if isinstance(error, ConfigError):
            self.logger.error(f"配置错误: {error.message}")
            if error.details:
                for key, value in error.details.items():
                    self.logger.error(f"  {key}: {value}")
            return 1
        else:
            self.logger.error(f"未知错误: {error}", exc_info=True)
            return 2
