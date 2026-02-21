"""
验证工具模块
"""

import re
from typing import Optional


def validate_api_key(api_key: str) -> bool:
    """验证 API Key 格式

    Args:
        api_key: API Key 字符串

    Returns:
        是否有效

    Raises:
        ValueError: API Key 格式无效
    """
    if not api_key:
        raise ValueError("API Key 不能为空")

    if len(api_key) < 10:
        raise ValueError("API Key 长度太短，至少需要 10 个字符")

    # 检查是否包含基本的有效字符
    if not re.match(r'^[a-zA-Z0-9\-_\.]+$', api_key):
        raise ValueError("API Key 包含无效字符")

    return True


def validate_url(url: str) -> bool:
    """验证 URL 格式

    Args:
        url: URL 字符串

    Returns:
        是否有效

    Raises:
        ValueError: URL 格式无效
    """
    if not url:
        raise ValueError("URL 不能为空")

    if not url.startswith(("http://", "https://")):
        raise ValueError("URL 必须以 http:// 或 https:// 开头")

    # 基本的 URL 格式验证
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not url_pattern.match(url):
        raise ValueError("URL 格式无效")

    return True


def validate_model_id(model_id: str) -> bool:
    """验证模型 ID 格式

    Args:
        model_id: 模型 ID 字符串

    Returns:
        是否有效

    Raises:
        ValueError: 模型 ID 格式无效
    """
    if not model_id:
        raise ValueError("模型 ID 不能为空")

    # 模型 ID 应该是 provider/model 格式，或者简单的名称
    if '/' in model_id:
        parts = model_id.split('/')
        if len(parts) != 2:
            raise ValueError("模型 ID 格式应为 provider/model 或 model")
        if not parts[0] or not parts[1]:
            raise ValueError("模型 ID 格式无效")

    return True


def validate_preset_id(preset_id: str) -> bool:
    """验证预设 ID 格式

    Args:
        preset_id: 预设 ID 字符串

    Returns:
        是否有效

    Raises:
        ValueError: 预设 ID 格式无效
    """
    if not preset_id:
        raise ValueError("预设 ID 不能为空")

    # 预设 ID 只能包含字母、数字、连字符和下划线
    if not re.match(r'^[a-zA-Z0-9\-_]+$', preset_id):
        raise ValueError("预设 ID 只能包含字母、数字、连字符和下划线")

    return True
