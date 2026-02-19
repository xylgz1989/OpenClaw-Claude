"""
安全工具模块
"""

import os
import stat
from pathlib import Path
from typing import Optional
import getpass
import keyring


def set_secure_permissions(file_path: Path) -> bool:
    """设置文件的安全权限（仅所有者可读写）

    Args:
        file_path: 文件路径

    Returns:
        是否成功设置权限
    """
    try:
        # 设置文件权限为仅所有者可读写 (600)
        file_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        return True
    except OSError as e:
        print(f"警告: 无法设置文件权限: {e}")
        return False


def get_api_key_interactive(service_name: str) -> str:
    """交互式获取API Key

    Args:
        service_name: 服务名称

    Returns:
        API Key
    """
    # 首先尝试从keyring获取
    try:
        stored_key = keyring.get_password(f"openclaw-{service_name}", "api_key")
        if stored_key:
            use_stored = input(f"是否使用已保存的{service_name} API Key? [Y/n]: ").strip().lower()
            if use_stored in ["", "y"]:
                return stored_key
    except Exception:
        pass

    # 交互式输入
    while True:
        api_key = getpass.getpass(f"请输入{service_name} API Key: ").strip()
        if not api_key:
            print("API Key不能为空")
            continue

        confirm_key = getpass.getpass("请再次输入API Key确认: ").strip()
        if api_key != confirm_key:
            print("两次输入的API Key不匹配，请重试")
            continue

        # 询问是否保存
        save_key = input("是否保存API Key到系统密钥环? [Y/n]: ").strip().lower()
        if save_key in ["", "y"]:
            try:
                keyring.set_password(f"openclaw-{service_name}", "api_key", api_key)
                print("API Key已安全保存")
            except Exception as e:
                print(f"警告: 无法保存API Key到密钥环: {e}")

        return api_key


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """遮蔽敏感数据

    Args:
        data: 原始数据
        mask_char: 遮蔽字符
        visible_chars: 可见字符数

    Returns:
        遮蔽后的数据
    """
    if len(data) <= visible_chars:
        return mask_char * len(data)
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)