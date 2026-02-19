"""
异常定义模块
"""

from typing import Optional, Any, Dict


class ConfigError(Exception):
    """配置相关错误"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConnectionError(ConfigError):
    """连接相关错误"""
    def __init__(self, message: str, error_type: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.error_type = error_type


class ValidationError(ConfigError):
    """验证相关错误"""
    pass


class AuthenticationError(ConnectionError):
    """认证错误"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "auth", details)


class NetworkError(ConnectionError):
    """网络错误"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "network", details)


class ModelError(ConnectionError):
    """模型错误"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "model", details)


class RateLimitError(ConnectionError):
    """速率限制错误"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "rate_limit", details)


class ServerError(ConnectionError):
    """服务器错误"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "server", details)