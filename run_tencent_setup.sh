#!/bin/bash

# 腾讯云轻量服务器 OpenClaw-Claude 集成运行脚本
# 包含项目规则优先和规格驱动开发混合模式

echo "=================================================="
echo "腾讯云轻量服务器 OpenClaw-Claude 集成设置"
echo "项目规则优先 + 规格驱动开发 混合模式"
echo "=================================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 彩色输出函数
print_status() {
    echo -e "${BLUE}[状态]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[注意]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    print_warning "警告：建议不要以root身份运行此脚本"
    echo "为安全起见，请在普通用户下运行，脚本会在需要时使用sudo"
fi

# 确认操作
echo "此脚本将设置针对腾讯云轻量服务器的OpenClaw-Claude集成，包含："
echo "  1. 项目规则优先的智能技能"
echo "  2. 腾讯云轻量服务器(CentOS)优化配置"
echo "  3. 规格驱动开发(SDD)回退机制"
echo "  4. 资源优化和监控功能"
echo ""

read -p "确定要继续吗？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "操作已取消"
    exit 1
fi

# 检查是否已存在设置
if [ -d ~/.openclaw/skills ]; then
    print_warning "检测到现有的OpenClaw设置"
    echo "选项："
    echo "  1. 更新现有设置（保留配置，更新技能）"
    echo "  2. 重新安装（覆盖所有文件）"
    echo "  3. 仅配置API密钥"
    echo "  4. 退出"
    echo ""

    while true; do
        read -p "请选择 (1-4): " choice
        case $choice in
            1)
                print_status "更新现有设置..."
                # 保存现有配置
                if [ -f ~/.openclaw/config.env ]; then
                    cp ~/.openclaw/config.env ~/.openclaw/config.env.backup.$(date +%Y%m%d_%H%M%S)
                    print_success "配置已备份"
                fi
                break
                ;;
            2)
                print_status "重新安装（将覆盖所有现有文件）..."
                read -p "确定要覆盖现有设置吗？(y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm -rf ~/.openclaw
                else
                    print_error "操作已取消"
                    exit 1
                fi
                break
                ;;
            3)
                print_status "配置API密钥..."
                if [ -f ~/.openclaw/config.env ]; then
                    echo "当前配置文件存在，是否编辑？"
                    read -p "(y/N): " -n 1 -r
                    echo
                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                        nano ~/.openclaw/config.env
                    fi
                else
                    print_error "配置文件不存在，请先运行完整安装"
                    exit 1
                fi
                exit 0
                ;;
            4)
                print_status "退出"
                exit 0
                ;;
            *)
                echo "请选择 1-4"
                ;;
        esac
    done
fi

echo ""
print_status "开始安装腾讯云轻量服务器优化的OpenClaw-Claude集成..."

# 运行主要设置脚本
if [ -f "./setup_tencent_lighthouse.sh" ]; then
    chmod +x ./setup_tencent_lighthouse.sh
    ./setup_tencent_lighthouse.sh
else
    print_error "主设置脚本 setup_tencent_lighthouse.sh 不存在"
    exit 1
fi

# 检查安装是否成功
if [ -f ~/.openclaw/config.env ]; then
    print_success "集成安装完成！"

    echo ""
    echo "=================================================="
    print_success "安装完成！以下是下一步操作："
    echo "=================================================="
    echo ""

    echo "1. 配置API密钥："
    echo "   编辑 ~/.openclaw/config.env 文件"
    echo "   设置 ANTHROPIC_API_KEY 和 OPENCLAW_TOKEN"
    echo ""

    echo "2. 验证安装："
    echo "   ~/.openclaw/verify_setup.sh"
    echo ""

    echo "3. 检查服务器健康状态："
    echo "   ~/.openclaw/health_check.sh"
    echo ""

    echo "4. 查看使用指南："
    echo "   ~/.openclaw/腾讯云轻量服务器_使用指南.md"
    echo ""

    echo "5. 测试项目规则检测（在项目目录中）："
    echo "   ~/.openclaw/tools/project-rules-detector.sh"
    echo ""

    print_success "特别说明："
    echo "• 系统现在支持智能决策：有项目规则时优先遵循，无规则时使用SDD"
    echo "• 已针对腾讯云轻量服务器进行优化，包括资源管理和网络连接"
    echo "• 所有操作都有日志记录，便于监控和调试"
    echo ""

else
    print_error "安装可能未完成，请检查错误信息"
    exit 1
fi

print_success "腾讯云轻量服务器 OpenClaw-Claude 集成设置完成！"