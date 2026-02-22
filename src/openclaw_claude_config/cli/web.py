"""
Web dashboard commands for OpenClaw Claude Config CLI
"""

import argparse


def create_parser(subparsers):
    """Create web command parser"""
    web_parser = subparsers.add_parser("web", help="Web Dashboard 命令")

    web_subparsers = web_parser.add_subparsers(dest="web_command", help="可用命令")

    # web start 命令
    start_parser = web_subparsers.add_parser("start", help="启动 Web Dashboard")
    start_parser.add_argument("--host", default="127.0.0.1", help="监听地址（默认：127.0.0.1）")
    start_parser.add_argument("--port", type=int, default=8000, help="监听端口（默认：8000）")
    start_parser.add_argument("--reload", action="store_true", help="启用热重载（开发模式）")

    return web_parser


def handle_web_start(args) -> int:
    """Handle web start command"""
    try:
        from ...web.app import run_web_server

        print(f"\n🚀 启动 Web Dashboard...")
        print(f"📍 地址: http://{args.host}:{args.port}")
        print(f"🔄 热重载: {'启用' if args.reload else '禁用'}")
        print(f"\n按 Ctrl+C 停止服务器\n")

        run_web_server(
            host=args.host,
            port=args.port,
            reload=args.reload
        )

    except KeyboardInterrupt:
        print("\n\n🛑 Web Dashboard 已停止")
        return 0
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return 1


def execute(args) -> int:
    """Execute web commands"""
    if args.web_command == "start":
        return handle_web_start(args)
    else:
        print("未知命令")
        return 1
