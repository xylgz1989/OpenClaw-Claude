"""
OpenClaw + Claude Code 配置工具
=================================

一个功能强大的统一配置工具，支持Claude Code LLM配置、OpenClaw配置生成，以及两者之间的联动。
"""

import argparse
from pathlib import Path

__version__ = "2.0.0"
__author__ = "OpenClaw Claude Config Team"


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="OpenClaw + Claude Code 统一配置工具 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s wizard                              # 交互式配置向导
  %(prog)s claude-config --preset zhipu        # 配置Claude Code（交互输入
                                                # API Key）
  %(prog)s claude-test                         # 测试Claude Code连接
  %(prog)s openclaw-config --model zhipu/glm-5 # 配置OpenClaw（交互输入
                                                # API Key）
  %(prog)s models china                        # 列出国内模型
        """,
    )

    # 设置日志
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="设置日志级别",
    )
    parser.add_argument("--log-file", type=Path, help="日志文件路径")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

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
    subparsers.add_parser("openclaw-validate", help="验证OpenClaw配置")

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
    openclaw_custom_parser.add_argument("--description", help="模型描述")

    # models命令
    models_parser = subparsers.add_parser("models", help="列出模型")
    models_parser.add_argument(
        "region",
        nargs="?",
        default="all",
        choices=["all", "china", "international"],
        help="模型区域",
    )

    return parser


def main():
    """主函数"""
    from .cli.wizard import WizardCommand
    from .config.claude import ClaudeCodeConfigManager
    from .config.openclaw import OpenClawConfigManager
    from .core.connection import ConnectionValidator
    from .models.registry import ModelRegistry
    from .utils.security import get_api_key_interactive
    from .utils.logger import setup_logger
    from .utils.validation import (
        validate_api_key,
        validate_url,
        validate_model_id,
        validate_preset_id,
    )
    from .constants import infer_provider
    from .core.exceptions import ConfigError, ConnectionError as CoreConnectionError

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
        if args.command == "wizard":
            wizard = WizardCommand()
            return wizard.execute(args)

        elif args.command == "claude-config":
            claude_config = ClaudeCodeConfigManager()
            connection_validator = ConnectionValidator()

            # 验证预设 ID
            try:
                validate_preset_id(args.preset)
            except ValueError as e:
                logger.error(f"预设 ID 无效: {e}")
                return 1

            # 获取API Key
            api_key = args.api_key or get_api_key_interactive(
                f"Claude Code ({args.preset})"
            )

            # 验证 API Key
            try:
                validate_api_key(api_key)
            except ValueError as e:
                logger.error(f"API Key 无效: {e}")
                return 1

            # 应用预设
            kwargs = {}
            if args.model:
                validate_model_id(args.model)
                kwargs["model"] = args.model

            claude_config.apply_preset(args.preset, api_key, **kwargs)

            # 测试连接
            if not args.no_test:
                print("\n正在测试连接...")
                env = claude_config.get("env", {})
                base_url = env.get("ANTHROPIC_BASE_URL", "")
                api_key = env.get("ANTHROPIC_AUTH_TOKEN", "")
                model = env.get("ANTHROPIC_MODEL", "")

                if base_url and api_key:
                    # 推断provider
                    provider = infer_provider(base_url)

                    result = connection_validator.test_connection(
                        base_url,
                        api_key,
                        model,
                        provider,
                        verify_ssl=not args.no_ssl_verify,
                    )
                    connection_validator.print_result(result)

        elif args.command == "claude-test":
            claude_config = ClaudeCodeConfigManager()
            connection_validator = ConnectionValidator()

            env = claude_config.get("env", {})
            base_url = env.get("ANTHROPIC_BASE_URL", "")
            api_key = env.get("ANTHROPIC_AUTH_TOKEN", "")
            model = env.get("ANTHROPIC_MODEL", "")

            if not base_url or not api_key:
                print("错误: 配置不完整，请先配置Claude Code")
                return 1

            # 推断provider
            provider = infer_provider(base_url)

            result = connection_validator.test_connection(
                base_url, api_key, model, provider, verify_ssl=True
            )
            connection_validator.print_result(result)

            if not result["success"]:
                return 1

        elif args.command == "claude-custom":
            claude_config = ClaudeCodeConfigManager()
            models = {
                "opus": args.opus_model,
                "sonnet": args.sonnet_model,
                "haiku": args.haiku_model,
            }
            claude_config.add_custom_preset(
                args.id, args.name, args.description, args.base_url, models
            )

        elif args.command == "claude-list":
            claude_config = ClaudeCodeConfigManager()
            claude_config.list_presets()
            print("\n当前配置:")
            import json

            print(
                json.dumps(
                    claude_config.get_current_config(),
                    indent=2,
                    ensure_ascii=False,
                )
            )

        elif args.command == "claude-ignore":
            claude_config = ClaudeCodeConfigManager()
            claude_config.create_claudeignore(args.patterns)

        elif args.command == "openclaw-config":
            openclaw_config = OpenClawConfigManager()
            connection_validator = ConnectionValidator()

            # 验证模型 ID
            try:
                validate_model_id(args.model)
            except ValueError as e:
                logger.error(f"模型 ID 无效: {e}")
                return 1

            # 获取API Key
            api_key = args.api_key or get_api_key_interactive(
                f"OpenClaw ({args.model})"
            )

            # 验证 API Key
            try:
                validate_api_key(api_key)
            except ValueError as e:
                logger.error(f"API Key 无效: {e}")
                return 1

            # 测试连接
            if not args.no_test and args.base_url:
                # 验证 Base URL
                try:
                    validate_url(args.base_url)
                except ValueError as e:
                    logger.error(f"Base URL 无效: {e}")
                    return 1
                print("\n正在测试连接...")
                provider = args.model.split("/")[0]
                result = connection_validator.test_connection(
                    args.base_url,
                    api_key,
                    args.model,
                    provider,
                    verify_ssl=not args.no_ssl_verify,
                )
                connection_validator.print_result(result)

                if not result["success"]:
                    continue_input = (
                        input("\n连接失败，是否继续保存配置? [y/N]: ")
                        .strip()
                        .lower()
                    )
                    if continue_input != "y":
                        return 1

            # 设置模型
            openclaw_config.set_model(
                args.model, api_key, args.base_url, test_connection=False
            )

        elif args.command == "openclaw-test":
            openclaw_config = OpenClawConfigManager()
            connection_validator = ConnectionValidator()

            model_config = openclaw_config.get_model_config(args.provider)
            base_url = model_config.get("baseUrl", "")
            api_key = model_config.get("apiKey", "")

            if not base_url or not api_key:
                print(f"错误: {args.provider} 配置不完整")
                return 1

            print(f"\n测试 {args.provider} 连接...")
            print(f"Base URL: {base_url}")

            result = connection_validator.test_connection(
                base_url, api_key, provider=args.provider, verify_ssl=True
            )
            connection_validator.print_result(result)

            if not result["success"]:
                return 1

        elif args.command == "openclaw-validate":
            openclaw_config = OpenClawConfigManager()
            is_valid, messages = openclaw_config.validate_config()
            for msg in messages:
                print(msg)
            if is_valid and not messages:
                print("配置验证通过")
            elif not is_valid:
                return 1

        elif args.command == "openclaw-custom":
            openclaw_config = OpenClawConfigManager()
            openclaw_config.add_custom_model(
                args.id,
                args.name,
                args.provider,
                args.api_endpoint,
                args.description or "",
            )

        elif args.command == "models":
            model_registry = ModelRegistry()
            models = model_registry.get_models(args.region)

            print(f"\n可用模型列表 ({args.region}):")
            print("-" * 60)

            if args.region == "all":
                # 当 region 是 all 时，models 的结构是 {'china': {...}, 'international': {...}}
                for category, providers in models.items():
                    category_name = (
                        "国内模型" if category == "china" else "国际模型"
                    )
                    print(f"\n{category_name}:")
                    for provider_id, provider_info in providers.items():
                        print(f"\n  [{provider_info['name']}]")
                        for model in provider_info.get("models", []):
                            print(f"    {model.id} - {model.name}")
                            print(
                                f"      上下文: "
                                f"{model.context_length // 1000}K tokens"
                            )
                            if model.api_pricing:
                                price_input = model.api_pricing.get(
                                    "input_per_1m", "N/A"
                                )
                                print(
                                    f"      API价格: 输入 {price_input}"
                                    f"元/百万tokens"
                                )
            else:
                # 当 region 不是 all 时，models 的结构是 {'qwen': {...}, 'glm': {...}, ...}
                category_name = (
                    "国内模型" if args.region == "china" else "国际模型"
                )
                print(f"\n{category_name}:")
                for provider_id, provider_info in models.items():
                    print(f"\n  [{provider_info['name']}]")
                    for model in provider_info.get("models", []):
                        print(f"    {model.id} - {model.name}")
                        print(
                            f"      上下文: "
                            f"{model.context_length // 1000}K tokens"
                        )
                        if model.api_pricing:
                            price_input = model.api_pricing.get(
                                "input_per_1m", "N/A"
                            )
                            print(
                                f"      API价格: 输入 {price_input}"
                                f"元/百万tokens"
                            )

        return 0

    except KeyboardInterrupt:
        print("\n\n操作已取消")
        return 130
    except ConfigError as e:
        logger.error(f"配置错误: {e}")
        return 2
    except CoreConnectionError as e:
        logger.error(f"连接错误: {e}")
        return 3
    except ValueError as e:
        logger.error(f"参数错误: {e}")
        return 4
    except Exception as e:
        logger.error(f"未知错误: {e}", exc_info=True)
        return 1
