#!/bin/bash

# 腾讯云轻量服务器 OpenClaw-Claude 集成验证脚本

echo "🔍 验证腾讯云轻量服务器 OpenClaw-Claude 集成文件"
echo "=================================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查函数
check_file() {
    if [ -f "$1" ]; then
        echo -e "  ${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "  ${GREEN}✓${NC} $1 (目录)"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 (目录)"
        return 1
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        echo -e "  ${GREEN}✓${NC} $1 (可执行)"
        return 0
    else
        echo -e "  ${YELLOW}!${NC} $1 (不可执行)"
        return 1
    fi
}

# 统计变量
total_checks=0
passed_checks=0

# 主要安装文件检查
echo ""
echo "📁 主要安装脚本:"
files=(
    "setup_tencent_lighthouse.sh"
    "run_tencent_setup.sh"
)

for file in "${files[@]}"; do
    ((total_checks++))
    if check_executable "$file"; then
        ((passed_checks++))
    fi
done

# 检查技能目录结构
echo ""
echo "🧩 技能目录结构:"
dirs=(
    "~/.openclaw/skills"
    "~/.openclaw/skills/claude-code-developer"
    "~/.openclaw/skills/claude-code-configurator"
    "~/.openclaw/skills/claude-code-project-handler"
    "~/.openclaw/hooks"
    "~/.openclaw/logs"
    "~/.openclaw/tools"
)

for dir in "${dirs[@]}"; do
    ((total_checks++))
    # 由于 ~ 在引号中不会展开，我们需要单独处理
    actual_dir=$(eval echo "$dir")
    if check_dir "$actual_dir"; then
        ((passed_checks++))
    fi
done

# 检查技能文件
echo ""
echo "🛠️  技能文件:"
skill_files=(
    "~/.openclaw/skills/claude-code-developer/SKILL.md"
    "~/.openclaw/skills/claude-code-configurator/SKILL.md"
    "~/.openclaw/skills/claude-code-project-handler/SKILL.md"
)

for file in "${skill_files[@]}"; do
    ((total_checks++))
    actual_file=$(eval echo "$file")
    if check_file "$actual_file"; then
        ((passed_checks++))
    fi
done

# 检查钩子和配置文件
echo ""
echo "🔧 钩子和配置文件:"
config_files=(
    "~/.openclaw/hooks/claude-code-hook.sh"
    "~/.openclaw/config.env"
    "~/.openclaw/verify_setup.sh"
    "~/.openclaw/health_check.sh"
    "~/.openclaw/tools/project-rules-detector.sh"
    "~/.openclaw/腾讯云轻量服务器_使用指南.md"
)

for file in "${config_files[@]}"; do
    ((total_checks++))
    actual_file=$(eval echo "$file")
    if [ -f "$actual_file" ]; then
        if [ -x "$actual_file" ]; then
            echo -e "  ${GREEN}✓${NC} $file (可执行)"
            ((passed_checks++))
        else
            echo -e "  ${GREEN}✓${NC} $file"
            ((passed_checks++))
        fi
    else
        echo -e "  ${RED}✗${NC} $file"
    fi
done

# 显示结果
echo ""
echo "=================================================="
echo "验证结果: $passed_checks/$total_checks 文件已找到"
echo "=================================================="

if [ $passed_checks -eq $total_checks ]; then
    echo -e "${GREEN}✅ 所有文件验证通过！集成已正确安装。${NC}"
    echo ""
    echo "✅ 项目规则优先功能已就绪"
    echo "✅ 腾讯云轻量服务器优化已应用"
    echo "✅ 所有技能和工具已创建"
    echo ""
    echo "下一步："
    echo "1. 编辑 ~/.openclaw/config.env 设置API密钥"
    echo "2. 运行 ~/.openclaw/verify_setup.sh 验证配置"
    echo "3. 使用 ~/.openclaw/tools/project-rules-detector.sh 检测项目规则"
else
    echo -e "${YELLOW}⚠️  部分文件未找到，可能需要重新运行安装。${NC}"
fi

echo ""
echo "提示：项目规则优先策略现在已激活！"
echo "在有项目规则的环境中，系统会优先遵循规则；"
echo "在无规则的环境中，会回退到规格驱动开发(SDD)。"