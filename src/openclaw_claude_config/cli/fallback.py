"""
Fallback commands for OpenClaw Claude Config CLI
"""

import argparse
from typing import Optional

from ..config.provider_manager import ProviderManager
from ..utils.logger import setup_logger, get_logger
from ..utils.security import get_api_key_interactive


def create_parser(subparsers):
    """Create fallback command parser"""
    fallback_parser = subparsers.add_parser("fallback", help="智能切换命令")

    fallback_subparsers = fallback_parser.add_subparsers(dest="fallback_command", help="可用命令")

    # fallback status 命令
    status_parser = fallback_subparsers.add_parser("status", help="查看切换状态")

    # fallback trigger 命令
    trigger_parser = fallback_subparsers.add_parser("trigger", help="手动触发切换")
    trigger_parser.add_argument("--from", dest="from_provider", required=True, help="当前提供商ID")
    trigger_parser.add_argument("--to", dest="to_provider", required=False, help="目标提供商ID（可选，默认为最佳提供商）")
    trigger_parser.add_argument("--reason", default="manual", help="切换原因")
    trigger_parser.add_argument("--strategy", default=None, help="切换策略（balance, tier, cost, latency, success_rate）")

    # fallback history 命令
    history_parser = fallback_subparsers.add_parser("history", help="查看切换历史")
    history_parser.add_argument("--last", type=int, default=10, help="显示最近 N 条记录")

    return fallback_parser


def handle_fallback_status(args) -> int:
    """Handle fallback status command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()

    fallback_config = provider_manager.get_fallback_config()

    print("\n智能切换状态:")
    print(f"  启用: {fallback_config.get('enabled', False)}")
    print(f"  默认策略: {fallback_config.get('default_strategy', 'N/A')}")
    print(f"  自动切换: {fallback_config.get('auto_fallback', False)}")

    if fallback_config.get('enabled', False):
        available_providers = provider_manager.get_available_providers()
        print(f"\n  可用提供商: {len(available_providers)}")
        for provider_id in available_providers:
            provider = provider_manager.get_provider(provider_id)
            print(f"    - {provider_id}: {provider.get('name', 'N/A')}")

    return 0


def handle_fallback_trigger(args) -> int:
    """Handle fallback trigger command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()

    print(f"\n手动触发切换:")
    print(f"  从: {args.from_provider}")

    if args.to_provider:
        print(f"  到: {args.to_provider}")
    else:
        print(f"  到: (自动选择最佳提供商）")

    print(f"  原因: {args.reason}")

    if args.strategy:
        print(f"  策略: {args.strategy}")

    # TODO: 实现实际的切换逻辑
    # 这需要切换引擎的实现

    print("\n⚠️  注意: 切换功能需要进一步的实现")
    print("请参考开发计划中的 Phase 1 任务。")

    return 0


def handle_fallback_history(args) -> int:
    """Handle fallback history command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()

    print(f"\n切换历史（最近 {args.last} 条）:")
    print("  ⚠️  注意: 切换历史需要数据库支持")
    print("请参考开发计划中的 Phase 1 任务。")

    return 0


def execute(args) -> int:
    """Execute fallback commands"""
    if args.fallback_command == "status":
        return handle_fallback_status(args)
    elif args.fallback_command == "trigger":
        return handle_fallback_trigger(args)
    elif args.fallback_command == "history":
        return handle_fallback_history(args)
    else:
        print("未知命令")
        return 1
