"""
Provider commands for OpenClaw Claude Config CLI
"""

import argparse

from ..config.provider_manager import ProviderManager
from ..utils.logger import get_logger
from ..utils.security import get_api_key_interactive


def create_parser(subparsers):
    """Create provider command parser"""
    provider_parser = subparsers.add_parser("provider", help="提供商管理命令")

    provider_subparsers = provider_parser.add_subparsers(dest="provider_command", help="可用命令")

    # provider enable 命令
    enable_parser = provider_subparsers.add_parser("enable", help="启用提供商")
    enable_parser.add_argument("--provider", required=True, help="提供商ID")

    # provider disable 命令
    disable_parser = provider_subparsers.add_parser("disable", help="禁用提供商")
    disable_parser.add_argument("--provider", required=True, help="提供商ID")

    # provider add 命令
    add_parser = provider_subparsers.add_parser("add", help="添加提供商")
    add_parser.add_argument("--id", required=True, help="提供商ID")
    add_parser.add_argument("--name", required=True, help="提供商名称")
    add_parser.add_argument("--api_endpoint", required=True, help="API 端点")
    add_parser.add_argument("--api_key", help="API Key（可选，建议使用交互输入）")
    add_parser.add_argument("--model", help="模型名称")
    add_parser.add_argument("--quota_limit", type=int, help="配额限制")
    add_parser.add_argument("--quota_type", help="配额类型（tokens/requests）")
    add_parser.add_argument("--tier", help="套餐类型（free/pro/enterprise）")
    add_parser.add_argument("--cost_per_1k_tokens", type=float, help="成本（每 1K tokens）")
    add_parser.add_argument("--priority", type=int, default=0, help="优先级")
    add_parser.add_argument("--rate_limit_5h", action="store_true", help="是否启用 5 小时限额")

    # provider remove 命令
    remove_parser = provider_subparsers.add_parser("remove", help="删除提供商")
    remove_parser.add_argument("--provider", required=True, help="提供商ID")

    # provider list 命令
    list_parser = provider_subparsers.add_parser("list", help="列出所有提供商")
    list_parser.add_argument("--enabled-only", action="store_true", help="仅显示启用的提供商")

    return provider_parser


def handle_provider_enable(args) -> int:
    """Handle provider enable command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()

    success = provider_manager.enable_provider(args.provider)

    if success:
        print(f"\n✅ 已启用提供商: {args.provider}")
    else:
        print(f"\n❌ 启用提供商失败: {args.provider}")
        return 1

    return 0


def handle_provider_disable(args) -> int:
    """Handle provider disable command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()

    success = provider_manager.disable_provider(args.provider)

    if success:
        print(f"\n✅ 已禁用提供商: {args.provider}")
    else:
        print(f"\n❌ 禁用提供商失败: {args.provider}")
        return 1

    return 0


def handle_provider_add(args) -> int:
    """Handle provider add command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()

    # 获取 API Key
    api_key = args.api_key or get_api_key_interactive(f"提供商 {args.id}")

    success = provider_manager.add_provider(
        provider_id=args.id,
        name=args.name,
        api_endpoint=args.api_endpoint,
        api_key=api_key,
        model=args.model,
        quota_limit=args.quota_limit,
        quota_type=args.quota_type,
        tier=args.tier,
        cost_per_1k_tokens=args.cost_per_1k_tokens,
        priority=args.priority,
        rate_limit_5h=args.rate_limit_5h
    )

    if success:
        print(f"\n✅ 已添加提供商: {args.id}")
        print(f"  名称: {args.name}")
        print(f"  API 端点: {args.api_endpoint}")
    else:
        print(f"\n❌ 添加提供商失败: {args.id}")
        return 1

    return 0


def handle_provider_remove(args) -> int:
    """Handle provider remove command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()

    success = provider_manager.remove_provider(args.provider)

    if success:
        print(f"\n✅ 已删除提供商: {args.provider}")
    else:
        print(f"\n❌ 删除提供商失败: {args.provider}")
        return 1

    return 0


def handle_provider_list(args) -> int:
    """Handle provider list command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()

    providers = provider_manager.list_providers(enabled_only=args.enabled_only)

    print(f"\n提供商列表 ({'已启用' if args.enabled_only else '全部'}):")
    print("-" * 60)

    for provider_id, provider in providers.items():
        status_icon = "✅" if provider.get("enabled", False) else "❌"
        print(f"\n  [{provider_id}] {provider.get('name', 'N/A')}")
        print(f"    状态: {status_icon}")
        print(f"    API 端点: {provider.get('api_endpoint', 'N/A')}")
        print(f"    模型: {provider.get('model', 'N/A')}")
        print(f"    优先级: {provider.get('priority', 0)}")

        if provider.get('quota_limit'):
            print(f"    配额限制: {provider.get('quota_limit')} {provider.get('quota_type', '')}")
            print(f"    套餐: {provider.get('tier', 'N/A')}")
            print(f"    成本: {provider.get('cost_per_1k_tokens', 'N/A')} 元/1K tokens")

        if provider.get('rate_limit_5h'):
            print(f"    5小时时限额: ✅")

    print("\n" + "-" * 60)

    return 0


def execute(args) -> int:
    """Execute provider commands"""
    if args.provider_command == "enable":
        return handle_provider_enable(args)
    elif args.provider_command == "disable":
        return handle_provider_disable(args)
    elif args.provider_command == "add":
        return handle_provider_add(args)
    elif args.provider_command == "remove":
        return handle_provider_remove(args)
    elif args.provider_command == "list":
        return handle_provider_list(args)
    else:
        print("未知命令")
        return 1
