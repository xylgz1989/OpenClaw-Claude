"""
Fallback commands for OpenClaw Claude Config CLI
"""

import argparse
from typing import Optional

from ..config.provider_manager import ProviderManager
from ..core.fallback_engine import FallbackEngine, FallbackReason
from ..core.quota_monitor import QuotaMonitor
from ..utils.logger import setup_logger, get_logger


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
    fallback_engine = FallbackEngine(provider_manager)

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
            if provider:
                print(f"    - {provider_id}: {provider.get('name', 'N/A')}")

    return 0


def handle_fallback_trigger(args) -> int:
    """Handle fallback trigger command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()
    fallback_engine = FallbackEngine(provider_manager)

    print(f"\n手动触发切换:")
    print(f"  从: {args.from_provider}")

    if args.to_provider:
        print(f"  到: {args.to_provider}")
    else:
        print(f"  到: (自动选择最佳提供商）")

    print(f"  原因: {args.reason}")

    if args.strategy:
        print(f"  策略: {args.strategy}")

    # 执行切换
    result = fallback_engine.trigger_fallback(
        from_provider_id=args.from_provider,
        reason=args.reason,
        strategy=args.strategy,
        to_provider_id=args.to_provider
    )

    if result.get('success'):
        print(f"\n✅ 切换成功")
        print(f"  从: {result.get('from_provider_id')} -> {result.get('to_provider_id')}")
        print(f"  原因: {result.get('reason')}")
        return 0
    else:
        print(f"\n❌ 切换失败: {result.get('error', 'Unknown error')}")
        return 1


def handle_fallback_history(args) -> int:
    """Handle fallback history command"""
    logger = get_logger(__name__)

    print(f"\n切换历史（最近 {args.last} 条）:")
    history = []
    # TODO: 实现从数据库获取历史
    if history:
        for event in history[:args.last]:
            print(f"\n  [{event['timestamp']}]")
            print(f"    从: {event['from_provider_id']} -> {event['to_provider_id']}")
            print(f"    原因: {event['reason']}")
            print(f"    策略: {event.get('strategy', 'N/A')}")
            print(f"    成功: {'是' if event.get('success') else '否'}")
    else:
        print("  ⚠️  切换历史需要数据库支持")
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
