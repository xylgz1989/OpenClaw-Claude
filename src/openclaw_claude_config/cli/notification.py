"""
Notification commands for OpenClaw Claude Config CLI
"""

import argparse
from typing import Optional

from ..config.provider_manager import ProviderManager
from ..core.alert_engine import AlertEngine, AlertLevel
from ..notifications.manager import get_notification_manager
from ..utils.logger import get_logger


def create_parser(subparsers):
    """Create notification command parser"""
    notification_parser = subparsers.add_parser("notification", help="告警通知命令")

    notification_subparsers = notification_parser.add_subparsers(dest="notification_command", help="可用命令")

    # notification send 命令
    send_parser = notification_subparsers.add_parser("send", help="发送告警通知")
    send_parser.add_argument("--provider", help="提供商ID（可选）")
    send_parser.add_argument("--level", choices=["info", "warning", "critical"], help="告警等级")

    # notification test 命令
    test_parser = notification_subparsers.add_parser("test", help="测试通知")
    test_parser.add_argument("--channels", nargs="+", help="通知渠道（可选，默认全部）")

    # notification status 命令
    status_parser = notification_subparsers.add_parser("status", help="查看通知状态")

    return notification_parser


def handle_notification_send(args) -> int:
    """Handle notification send command"""
    logger = get_logger(__name__)
    provider_manager = ProviderManager()
    alert_engine = AlertEngine(provider_manager)
    notification_manager = get_notification_manager()

    if not notification_manager.channels:
        print("\n❌ 没有配置的通知渠道")
        return 1

    # Check if provider is specified
    provider_id = args.provider
    if not provider_id:
        print("\n⚠️  未指定提供商")
        print("\n请使用 --provider 参数指定提供商ID，或全局发送所有待处理的告警")
        return 1

    # Create alert
    provider = provider_manager.get_provider(provider_id)
    if not provider:
        print(f"\n❌ 提供商 {provider_id} 不存在")
        return 1

    # Check alert level
    if not args.level:
        print("\n⚠️  未指定告警等级")
        return 1

    level = args.level

    # Create alert
    alert = alert_engine.create_alert(
        provider_id=provider_id,
        level=level,
        message=f"测试告警",
        metadata={"test": True}
    )

    if not alert:
        print(f"\n❌ 创建告警失败")
        return 1

    # Send notification via all channels
    print(f"\n发送告警通知到所有渠道...")

    results = notification_manager.send_alert(alert, channels=None)

    success_count = sum(1 for r in results.values() if r.get('success', False))
    failed_count = len(results) - success_count

    print(f"\n发送结果:")
    for channel, result in results.items():
        status_icon = "✅" if result.get('success', False) else "❌"
        print(f"  {channel}: {status_icon}")

        if not result.get('success'):
            print(f"    错误: {result.get('error', 'Unknown error')}")

    print(f"\n总结: {success_count} 成功, {failed_count} 失败")

    if success_count > 0:
        return 0
    else:
        return 1


def handle_notification_test(args) -> int:
    """Handle notification test command"""
    logger = get_logger(__name__)
    notification_manager = get_notification_manager()

    if not notification_manager.channels:
        print("\n❌ 没有配置的通知渠道")
        return 1

    test_message = f"测试告警消息 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    print(f"\n发送测试消息到所有通知渠道...")
    print(f"消息: {test_message}")

    # Send test message
    results = notification_manager.send_test_message(
        message=test_message,
        channels=args.channels or None
    )

    print(f"\n发送结果:")
    success_count = sum(1 for r in results.values() if r.get('success', False))
    failed_count = len(results) - success_count

    for channel, result in results.items():
        status_icon = "✅" if result.get('success', False) else "❌"
        print(f"  {channel}: {status_icon}")

        if not result.get('success'):
            print(f"    错误: {result.get('error', 'Unknown error')}")

    print(f"\n总结: {success_count} 成功, {failed_count} 失败")

    if success_count > 0:
        return 0
    else:
        return 1


def handle_notification_status(args) -> int:
    """Handle notification status command"""
    logger = get_logger(__name__)
    notification_manager = get_notification_manager()

    print("\n通知状态:")

    if not notification_manager.channels:
        print("  ❌ 没有配置的通知渠道")
        return 0

    print(f"  可用渠道: {list(notification_manager.channels.keys())}")
    for channel, notifier in notification_manager.channels.items():
            enabled_icon = "✅" if notifier.enabled else "❌"
            print(f"  {channel}: {enabled_icon}")

    # Check if fallback is enabled
    config = notification_manager.provider_manager.get_fallback_config()
    fallback_enabled = config.get('enabled', False)

    print(f"  智能切换: {fallback_enabled}")

    return 0


def execute(args) -> int:
    """Execute notification commands"""
    if args.notification_command == "send":
        return handle_notification_send(args)
    elif args.notification_command == "test":
        return handle_notification_test(args)
    elif args.notification_command == "status":
        return handle_notification_status(args)
    else:
        print("未知命令")
        return 1
