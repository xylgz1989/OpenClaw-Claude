"""
常量定义模块
"""

from typing import Optional

# 已知的 Provider 列表
KNOWN_PROVIDERS = [
    "anthropic",
    "openai",
    "zhipu",
    "qwen",
    "deepseek",
    "kimi",
    "minimax",
]

# 连接测试默认配置
DEFAULT_TIMEOUT = 15  # 秒
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1  # 秒

# 模型映射
MODEL_TIER_MAPPING = {
    "opus": "最高性能",
    "sonnet": "平衡性能",
    "haiku": "快速响应",
}


def infer_provider(base_url: str) -> Optional[str]:
    """从 URL 推断 provider

    Args:
        base_url: API 基础 URL

    Returns:
        Provider 名称，如果无法推断则返回 None
    """
    if not base_url:
        return None

    base_url_lower = base_url.lower()

    for provider in KNOWN_PROVIDERS:
        if provider in base_url_lower:
            return provider

    # 特殊路径推断
    if "/anthropic" in base_url_lower:
        return "anthropic"
    elif "/openai" in base_url_lower:
        return "openai"

    return None
