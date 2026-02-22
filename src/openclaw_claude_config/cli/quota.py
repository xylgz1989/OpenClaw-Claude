"""
Quota commands for OpenClaw Claude Config CLI
"""

import argparse

from ..config.provider_manager import ProviderManager
from ..core.quota_monitor import QuotaMonitor
from ..utils.logger import get_logger


def create_parser(subparsers):
    """Create quota command parser"""
    quota_parser = subparsers.add_parser("quota", help="配额监控命令")

    quota_subparsers = quota_parser.add_subparsers(dest="quota_command", help="可用命令")

    # quota status 命令
    status_parser = quota_subparsers.add_parser("status", help="查看配额状态")
    status_parser.add_argument("--provider", help="提供商ID（可选）")
    status_parser.add_argument("--all", action="store_true", help="显示所有提供商")

    # quota test 命令
    test_parser = quota_subparsers.add_parser("test", help="测试配额监控")
    test_parser.add_argument("--provider", required=True, help="提供商ID")

    return quota_parser


def handle_quota_status(args) -> int:
    """Handle quota status command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()
    quota_monitor = QuotaMonitor(provider_manager)

    quota_config = provider_manager.get_quota_monitoring_config()

    print("\n配额监控状态:")
    print(f"  启用: {quota_config.get('enabled', False)}")
    print(f"  检查间隔: {quota_config.get('check_interval_seconds', 300)} 秒")

    alert_thresholds = quota_config.get("alert_thresholds", {})
    print(f"  告警阈值:")
    print(f"    警告: {alert_thresholds.get('warning', 80)}%")
    print(f"    严重: {alert_thresholds.get('critical', 90)}%")
    print(f"    耗尽: {alert_thresholds.get('exhausted', 95)}%")

    if args.all:
        providers = provider_manager.list_providers(enabled_only=False)
        print(f"\n  所有提供商: {len(providers)}")
        for provider_id, provider in providers.items():
            print(f"    - {provider_id}: {provider.get('name', 'N/A')}")
            print(f"      启用: {provider.get('enabled', False)}")

            if provider.get('quota_limit'):
                print(f"      配额限制: {provider.get('quota_limit')}")
                print(f"      配额类型: {provider.get('quota_type', 'N/A')}")

            # 查询配额
            quota_info = quota_monitor.query_quota(provider_id)
            if quota_info:
                used = quota_info.get('used', 0)
                limit = quota_info.get('limit')
                if limit:
                    usage_percentage = (used / limit * 100) if limit else 0
                    remaining = limit - used

                    print(f"      已用: {used}")
                    print(f"      限制: {limit}")
                    print(f"      剩余: {remaining}")
                    print(f"      使用率: {usage_percentage:.1f}%")

                    # 检查告警
                    alerts = quota_monitor.check_quota_alerts(provider_id, quota_info)
                    if alerts:
                        print(f"      告警: {len(alerts)} 个")
                        for alert in alerts:
                            print(f"        - {alert['level']}: {alert['message']}")
                else:
                    print(f"      状态: 无配额信息")
            else:
                print(f"      状态: 配额查询失败")

    elif args.provider:
        provider = provider_manager.get_provider(args.provider)
        if provider:
            print(f"\n提供商 {args.provider}:")
            print(f"  名称: {provider.get('name', 'N/A')}")
            print(f"  启用: {provider.get('enabled', False)}")

            if provider.get('quota_limit'):
                print(f"  配额限制: {provider.get('quota_limit')}")
                print(f"  配额类型: {provider.get('quota_type', 'N/A')}")

            # 查询配额
            quota_info = quota_monitor.query_quota(provider_id)
            if quota_info:
                used = quota_info.get('used', 0)
                limit = quota_info.get('limit')
                if limit:
                    usage_percentage = (used / limit * 100) if limit else 0
                    remaining = limit - used

                    print(f"  已用: {used}")
                    print(f"  限制: {limit}")
                    print(f"  剩余: {remaining}")
                    print(f"  使用率: {usage_percentage:.1f}%")

                    # 检查告警
                    alerts = quota_monitor.check_quota_alerts(provider_id, quota_info)
                    if alerts:
                        print(f"  告警: {len(alerts)} 个")
                        for alert in alerts:
                            print(f"    - {alert['level']}: {alert['message']}")
                else:
                    print(f"  状态: 无配额信息")
            else:
                print(f"  状态: 配额查询失败")
        else:
            print(f"\n提供商 {args.provider} 不存在")
            return 1

    else:
        available = provider_manager.get_available_providers()
        print(f"\n可用提供商: {len(available)}")
        for provider_id in available:
            provider = provider_manager.get_provider(provider_id)
            print(f"  - {provider_id}: {provider.get('name', 'N/A')}")

    return 0


def handle_quota_test(args) -> int:
    """Handle quota test command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()
    quota_monitor = QuotaMonitor(provider_manager)

    print(f"\n测试配额监控: {args.provider}")

    # 查询配额
    quota_info = quota_monitor.query_quota(args.provider)
    if quota_info:
        used = quota_info.get('used', 0)
        limit = quota_info.get('limit')
        if limit:
            usage_percentage = (used / limit * 100) if limit else 0

            print(f"\n  已用: {used}")
            print(f"  限制: {limit}")
            print(f"  剩余: {limit - used}")
            print(f"  使用率: {usage_percentage:.1f}%")

            # 检查告警
            alerts = quota_monitor.check_quota_alerts(args.provider, quota_info)
            if alerts:
                print(f"\n  告警: {len(alerts)} 个")
                for alert in alerts:
                    print(f"    - {alert['level']}: {alert['message']}")
            else:
                print("\n  ⚠️  无告警")

        # 测试 API 连接
        provider = provider_manager.get_provider(args.provider)
        if provider:
            print(f"\n  测试 API 连接...")
            print(f"  API 端点: {provider.get('api_endpoint')}")
            # TODO: 实现实际的连接测试
            print(f"\n  ⚠️  连接测试需要进一步实现")

            return 0
        else:
            print(f"\n❌ 提供商 {args.provider} 不存在")
            return 1

    return 0


def execute(args) -> int:
    """Execute quota commands"""
    if args.quota_command == "status":
        return handle_quota_status(args)
    elif args.quota_command == "test":
        return handle_quota_test(args)
    else:
        print("未知命令")
        return 1
