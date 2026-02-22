"""
Entry point for the OpenClaw Claude Config CLI (with fallback, quota monitoring, and notifications).
"""

import sys

# 导入所有命令模块
from .fallback import create_parser as create_fallback_parser, execute as execute_fallback
from .quota import create_parser as create_quota_parser, execute as execute_quota
from .notification import create_parser as create_notification_parser, execute as execute_notification
# 导入原有命令
from .wizard import WizardCommand

try:
    from ..config.claude import ClaudeCodeConfigManager
    from ..config.openclaw import OpenClawConfigManager
    from ..core.connection import ConnectionValidator
    from ..models.registry import ModelRegistry
    from ..utils.security import get_api_key_interactive
    from ..utils.logger import setup_logger, get_logger
    from ..utils.validation import (
        validate_api_key,
        validate_url,
        validate_model_id,
        validate_preset_id,
    )
    from ..constants import infer_provider
    from ..core.exceptions import ConfigError, ConnectionError as CoreConnectionError
except ImportError:
    # 如果导入失败，使用简化版本
    print("警告: 某些模块导入失败，CLI 功能受限")
    WizardCommand = None


def create_parser():
    """Create command line argument parser（包含新命令）"""
    import argparse

    parser = argparse.ArgumentParser(
        description="OpenClaw + Claude Code 统一配置工具 v2.0.2（含智能切换 + 配额监控 + 告警通知）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例（原有命令）:
  %(prog)s wizard                              # 交互式配置向导
  %(prog)s claude-config --preset zhipu        # 配置Claude Code
  %(prog)s claude-test                         # 测试Claude Code连接

示例（新增命令）:
  %(prog)s fallback status                      # 查看切换状态
  %(prog)s fallback trigger --from glm --to deepseek --reason manual  # 手动切换
  %(prog)s fallback history --last 10           # 查看切换历史
  %(prog)s quota status --all                   # 查看配额状态
  %(prog)s provider list                        # 列出所有提供商
  %(prog)s notification status                   # 查看通知状态
  %(prog)s notification send --provider deepseek --level warning    # 发送告警通知
  %(prog)s notification test --channels email webhook --message "测试" # 测试通知

        """,
    )

    # 设置日志
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="设置日志级别",
    )
    parser.add_argument("--log-file", help="日志文件路径")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 原有命令
    if WizardCommand is not None:
        # wizard命令
        subparsers.add_parser("wizard", help="交互式配置向导")

        # claude-config命令
        claude_parser = subparsers.add_parser(
            "claude-config", help="配置Claude Code"
        )
        claude_parser.add_argument("--preset", required=True, help="预设名称")
        claude_parser.add_argument("--api-key", help="API Key（建议使用交互输入）")
        claude_parser.add_argument("--model", help="指定模型（覆盖预设）")
        claude_parser.add_argument(
            "--no-test", action="store_true", help="跳过连接测试"
        )
        claude_parser.add_argument(
            "--no-ssl-verify", action="store_true", help="禁用SSL验证（不推荐）"
        )

        # claude-test命令
        subparsers.add_parser("claude-test", help="测试Claude Code连接")

        # claude-custom命令
        claude_custom_parser = subparsers.add_parser(
            "claude-custom", help="添加自定义Claude预设"
        )
        claude_custom_parser.add_argument("--id", required=True, help="预设ID")
        claude_custom_parser.add_argument("--name", required=True, help="预设名称")
        claude_custom_parser.add_argument(
            "--description", required=True, help="预设描述"
        )
        claude_custom_parser.add_argument(
            "--base-url", required=True, help="Base URL"
        )
        claude_custom_parser.add_argument(
            "--opus-model", required=True, help="Opus模型ID"
        )
        claude_custom_parser.add_argument(
            "--sonnet-model", required=True, help="Sonnet模型ID"
        )
        claude_custom_parser.add_argument(
            "--haiku-model", required=True, help="Haiku模型ID"
        )

        # claude-list命令
        subparsers.add_parser("claude-list", help="列出Claude Code配置")

        # claude-ignore命令
        claude_ignore_parser = subparsers.add_parser(
            "claude-ignore", help="创建.claudeignore"
        )
        claude_ignore_parser.add_argument(
            "--patterns", nargs="+", help="自定义忽略模式"
        )

        # openclaw-config命令
        openclaw_parser = subparsers.add_parser(
            "openclaw-config", help="配置OpenClaw"
        )
        openclaw_parser.add_argument("--model", required=True, help="模型ID")
        openclaw_parser.add_argument(
            "--api-key", help="API Key（建议使用交互输入）"
        )
        openclaw_parser.add_argument("--base-url", help="Base URL")
        openclaw_parser.add_argument(
            "--no-test", action="store_true", help="跳过连接测试"
        )
        openclaw_parser.add_argument(
            "--no-ssl-verify", action="store_true", help="禁用SSL验证（不推荐）"
        )

        # openclaw-test命令
        openclaw_test_parser = subparsers.add_parser(
            "openclaw-test", help="测试OpenClaw模型连接"
        )
        openclaw_test_parser.add_argument(
            "--provider", required=True, help="Provider名称"
        )

        # openclaw-validate命令
        subparsers.add_parser(
            "openclaw-validate", help="验证OpenClaw配置"
        )

        # openclaw-custom命令
        openclaw_custom_parser = subparsers.add_parser(
            "openclaw-custom", help="添加自定义模型"
        )
        openclaw_custom_parser.add_argument(
            "--id", required=True, help="模型ID (格式: provider/model)"
        )
        openclaw_custom_parser.add_argument(
            "--name", required=True, help="模型名称"
        )
        openclaw_custom_parser.add_argument(
            "--provider", required=True, help="Provider名称"
        )
        openclaw_custom_parser.add_argument(
            "--api-endpoint", required=True, help="API端点"
        )
        openclaw_custom_parser.add_argument(
            "--description", help="模型描述"
        )

        # models命令
        models_parser = subparsers.add_parser("models", help="列出模型")
        models_parser.add_argument(
            "region",
            nargs="?",
            default="all",
            choices=["all", "china", "international"],
            help="模型区域",
        )

    # 新增命令
    # fallback命令
    create_fallback_parser(subparsers)

    # quota命令
    create_quota_parser(subparsers)

    # notification命令
    create_notification_parser(subparsers)

    # provider命令
    from .provider import create_parser as create_provider_parser

    return parser


def main():
    """主函数（包含新命令）"""
    parser = create_parser()
    args = parser.parse_args()

    # 设置日志
    logger = setup_logger(
        "openclaw_claude_config", level=args.log_level, log_file=args.log_file
    )

    if not args.command:
        parser.print_help()
        return 0

    try:
        # 执行命令
        if args.command in ["fallback"]:
            from .fallback import execute
            return execute(args)
        elif args.command in ["quota"]:
            from .quota import execute
            return execute(args)
        elif args.command in ["notification"]:
            from .notification import execute
            return execute(args)
        elif args.command in ["provider"]:
            from .provider import execute
            return execute(args)
        elif args.command == "wizard" and WizardCommand is not None:
            wizard = WizardCommand()
            return wizard.execute(args)

        else:
            # 原有命令需要完整的导入
            if WizardCommand is None:
                logger.error("模块导入失败，无法执行原有命令")
                print("新增命令（fallback、quota、notification、provider）已可用")
                return 1
            # 导入原有命令处理逻辑
            # TODO: 这里可以复制原有的命令处理逻辑
            print(f"\n⚠️  原有命令执行需要完整实现")
            print("新增命令（fallback、quota、notification、provider）已可用")
            return 0

    except KeyboardInterrupt:
        print("\n\n操作已取消")
        return 130
    except Exception as e:
        logger.error(f"未知错误: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
