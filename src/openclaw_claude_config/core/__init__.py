"""
Core module

避免循环导入：所有模块按需导入
"""

from .exceptions import ConfigError, ConnectionError

__all__ = [
    'ConfigError',
    'ConnectionError',
]
