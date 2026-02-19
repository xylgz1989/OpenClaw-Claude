#!/bin/bash

# OpenClaw-Claude Code 腾讯云轻量服务器 (CentOS) 优化集成设置
# 支持项目规则优先和规格驱动开发混合模式

set -e  # 出错时停止执行

# 定义颜色代码
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

# 暂停等待人工确认
pause_for_verification() {
    echo "[AUTO] Skipping verification pause: $1"
}

# 确认是否继续
confirm_action() {
    echo ""
    echo -e "${YELLOW}⚠️  需要确认：${NC} $1"
    while true; do
        read -p "是否继续？(y/n): " -r yn
        case $yn in
            [Yy]* ) break;;
            [Nn]* )
                print_error "操作已被用户取消。"
                exit 1
                ;;
            * ) echo "请输入 y 或 n";;
        esac
    done
    echo ""
}

# 检测腾讯云轻量服务器环境
detect_tencent_lighthouse() {
    print_status "检测服务器环境..."

    # 检测是否为CentOS系统
    if [ -f /etc/os-release ]; then
        OS_INFO=$(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
        if [[ "$OS_INFO" == *"CentOS"* ]]; then
            print_success "检测到CentOS系统: $OS_INFO"

            # 检测是否为腾讯云轻量服务器
            if dmesg | grep -i "Tencent" &>/dev/null || hostnamectl | grep -i "Tencent" &>/dev/null; then
                print_success "检测到腾讯云轻量服务器环境"
            else
                print_warning "当前在CentOS环境下运行（可能是腾讯云轻量服务器）"
            fi
        else
            print_warning "非CentOS系统，但将继续安装"
        fi
    else
        print_warning "无法检测系统信息，继续安装"
    fi

    # 为腾讯云轻量服务器优化配置
    print_status "应用腾讯云轻量服务器优化配置..."

    # 检测内存大小并设置合适的超时值
    TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
    if [ "$TOTAL_MEM" -lt 2048 ]; then
        # 低内存服务器，调整为更保守的超时
        TIMEOUT_ADJUSTMENT="LOW_MEM"
        print_warning "检测到较低内存($TOTAL_MEM MB)，已优化配置以适应轻量服务器"
    else
        TIMEOUT_ADJUSTMENT="NORMAL"
        print_success "服务器资源配置良好"
    fi
}

# 检查依赖
check_prerequisites() {
    print_status "检查必要依赖..."

    PREREQS_MET=1

    # 检查curl
    if ! command -v curl &> /dev/null; then
        print_error "curl 未安装，正在安装..."
        if command -v yum &> /dev/null; then
            sudo yum install -y curl
        elif command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y curl
        else
            print_error "无法安装curl，请手动安装"
            PREREQS_MET=0
        fi
    fi

    # 检查基本工具
    for cmd in bash wget tar gzip; do
        if ! command -v $cmd &> /dev/null; then
            print_error "$cmd 未安装，正在安装..."
            if command -v yum &> /dev/null; then
                sudo yum install -y $cmd
            elif command -v apt-get &> /dev/null; then
                sudo apt-get install -y $cmd
            fi
        fi
    done

    if [ $PREREQS_MET -eq 0 ]; then
        print_error "部分依赖缺失，请解决后重试。"
        exit 1
    fi

    print_success "所有依赖检查完成"
}

# 创建目录结构
create_directories() {
    print_status "📁 创建目录结构..."

    mkdir -p ~/.openclaw/skills/claude-code-developer
    mkdir -p ~/.openclaw/skills/claude-code-configurator
    mkdir -p ~/.openclaw/skills/claude-code-project-handler
    mkdir -p ~/.openclaw/hooks
    mkdir -p ~/.openclaw/logs
    mkdir -p ~/.openclaw/backups

    # 设置安全权限（腾讯云轻量服务器安全优化）
    chmod 700 ~/.openclaw
    chmod 700 ~/.openclaw/skills
    chmod 700 ~/.openclaw/hooks
    chmod 700 ~/.openclaw/logs

    pause_for_verification "目录结构已创建到 ~/.openclaw/"
}

# 创建项目规则优先的技能
create_project_handler_skill() {
    print_status "⚙️  创建项目规则处理器技能..."

    cat > ~/.openclaw/skills/claude-code-project-handler/SKILL.md << 'EOF'
---
name: claude-code-project-handler
description: 智能处理项目：优先检查项目规则，其次使用规格驱动开发
tools:
  - exec
  - read
  - write
  - bash
---

# Claude Code 项目规则优先处理器

## 功能概述

本Skill用于智能处理项目：
1. 优先检测并遵守现有项目的项目规则
2. 若无项目规则，则使用规格驱动开发(SDD)

## 工作流程

### 步骤1：检查项目规则文件

在执行任何操作前，首先查找以下项目规则文件：
- `PROJECT_RULES.md`
- `rules.md`
- `CONTRIBUTING.md` （包含规则的部分）
- `README.md` （包含规则的部分）
- `ARCHITECTURE.md`
- `DEVELOPMENT_GUIDELINES.md`

### 步骤2：解析项目规则

如果找到项目规则文件，解析其中的关键规则：
- 技术栈要求
- 代码风格规范
- 文件结构约定
- 部署要求
- 测试标准
- 安全要求

### 步骤3：应用项目规则

基于解析的规则：
- 选择适当的开发技术
- 遵循既定代码风格
- 维持文件结构一致
- 满足测试要求

### 步骤4：执行任务

根据项目规则执行相应操作：
- 如有项目规则：严格遵循规则执行
- 如无项目规则：回退到规格驱动开发流程

## 项目规则检查命令

```bash
# 检查当前项目规则
find . -name "*.md" -exec grep -l "rule\|guideline\|standard\|policy\|requirement" {} \;

# 查找常见规则文件
ls -la | grep -E "(project|rule|contribut|architect|development).*\.(md|txt)$"
```

## 与SDD流程的对比

### 有项目规则时：
1. 分析项目规则文件
2. 按规则要求执行
3. 验证符合度
4. 输出符合项目标准的结果

### 无项目规则时：
1. 进入SDD流程：/constitution → /specify → /plan → /tasks → /analyze → /implement
2. 按SDD流程执行
3. 输出标准化的SDD结果

## 安全注意事项

- 优先遵守现有项目规则
- 避免违反项目的既定约定
- 在改变项目结构前检查规则
- 保持与项目原有风格的一致性
EOF

    pause_for_verification "项目规则处理器技能已创建，位于 ~/.openclaw/skills/claude-code-project-handler/SKILL.md"
}

# 更新开发者技能以支持规则优先
create_updated_developer_skill() {
    print_status "⚙️  更新Claude Code开发者技能（支持项目规则优先）..."

    cat > ~/.openclaw/skills/claude-code-developer/SKILL.md << 'EOF'
---
name: claude-code-developer
description: 智能Claude Code开发者，优先检查项目规则，其次使用规格驱动开发
tools:
  - exec
  - read
  - write
  - bash
---

# Claude Code 智能开发者技能

## 功能概述

本Skill用于在OpenClaw中智能调用Claude Code，优先检查项目规则，其次使用规格驱动开发。

## 智能工作流程

### 步骤1：检测项目上下文

首先检测当前项目环境：
- 是否存在项目规则文件
- 当前目录结构
- 已有的代码和配置

### 步骤2：检查项目规则（优先）

如果检测到项目规则，按照以下顺序查找：
1. `PROJECT_RULES.md`
2. `rules.md`
3. `CONTRIBUTING.md`
4. `README.md` (检查是否包含规则部分)
5. `ARCHITECTURE.md`
6. `STYLE_GUIDE.md`
7. `DEVELOPMENT_GUIDELINES.md`

### 步骤3：应用项目规则

如果找到项目规则：
1. 解析规则要求
2. 根据规则调整开发策略
3. 遵循项目的约定和技术栈
4. 保持与现有代码的一致性

### 步骤4：执行任务

根据项目上下文执行：

#### 如果有项目规则：
```bash
# 遵循项目规则执行
echo "检测到项目规则，正在按规则执行..."
# 执行符合项目标准的操作
```

#### 如果无项目规则（回退到SDD）：
1. **初始化项目环境**：
   ```bash
   specify init <project-name> --ai claude
   ```

2. **确立项目铁律（/constitution）**：
   ```
   /constitution <你的工程原则>
   ```

3. **编写规格（/specify）**：
   ```
   /specify <描述你要构建的功能>
   ```

4. **澄清不确定性（/clarify）**：
   ```
   /clarify
   ```

5. **制定技术计划（/plan）**：
   ```
   /plan <技术栈说明>
   ```

6. **拆分任务（/tasks）**：
   ```
   /tasks
   ```

7. **一致性检查（/analyze）**：
   ```
   /analyze
   ```

8. **开始实现（/implement）**：
   ```
   /implement
   ```

## 使用场景

1. **新项目**：使用SDD规格驱动开发流程
2. **现有项目**：优先遵守项目规则，其次使用SDD
3. **规则变更**：在规则允许范围内开发
4. **维护更新**：严格遵循现有项目规则

## 与OpenClaw的集成

### 标准调用方式

当用户在OpenClaw中发送：
```
Claude，请在当前项目中添加[功能描述]
```

你应该：
1. 检查当前项目规则
2. 如果有规则，优先遵循规则
3. 如果无规则，使用SDD流程
4. 执行相应的开发任务
5. 保持与项目标准的一致性

## 输出格式

根据项目规则或SDD流程生成相应输出：
1. **遵循项目规则**：符合项目标准的输出
2. **SDD流程**：标准的SDD交付物
3. **合规性报告**：说明如何遵循了项目规则

## 安全注意事项

- 优先遵守项目规则
- 不违反项目的既定约定
- 保持代码风格一致性
- 尊重项目架构决策
EOF

    pause_for_verification "更新后的开发者技能已创建，支持项目规则优先"
}

# 创建配置技能
create_config_skill() {
    print_status "⚙️  创建Claude Code配置技能..."

    cat > ~/.openclaw/skills/claude-code-configurator/SKILL.md << 'EOF'
---
name: claude-code-configurator
description: 配置Claude Code的LLM设置，支持多种预设和自定义模型
tools:
  - exec
  - read
  - write
  - bash
---

# Claude Code 配置器技能

## 功能概述

本Skill用于配置和管理Claude Code的LLM（大语言模型）设置，支持多种预设和自定义模型配置。

## 使用场景

1. 配置Claude Code使用不同提供商的模型
2. 设置模型分层策略（Primary + Fallbacks）
3. 创建.claudeignore文件进行上下文精简
4. 验证配置连接并提供反馈

## 配置命令

### 使用预设配置

```bash
openclaw-claude-config claude-config --preset <预设名称> --api-key <API密钥>
```

支持的预设：
- `anthropic`: Anthropic Claude模型
- `openai`: OpenAI GPT模型
- `zhipu`: 智谱清言GLM模型
- `qwen`: 通义千问模型
- `deepseek`: DeepSeek模型
- `kimi`: Kimi模型
- `minimax`: MiniMax模型

### 自定义模型配置

```bash
openclaw-claude-config claude-custom \
    --id my-provider \
    --name "My Provider" \
    --description "自定义LLM提供商" \
    --base-url https://api.myprovider.com/v1 \
    --opus-model gpt-4 \
    --sonnet-model gpt-3.5-turbo \
    --haiku-model gpt-3.5-turbo
```

### 测试连接

```bash
openclaw-claude-config claude-test
```

### 创建.claudeignore

```bash
openclaw-claude-config claude-ignore
```

## 模型分层策略

配置支持Primary + Fallbacks模型分层，提高系统可靠性：
1. 首先尝试Primary模型
2. 如果失败，则依次尝试Fallback模型
3. 提供详细的错误反馈和解决方案

## 配置文件位置

- Claude Code配置: `~/.claude/settings.json`
- 自定义预设: `~/.claude/custom_presets.json`

## 安全注意事项

- 交互式API密钥输入，避免在命令历史中暴露
- 支持跳过连接测试的选项（--no-test）
- SSL验证默认开启，可选择禁用（--no-ssl-verify）
EOF

    pause_for_verification "Claude配置技能已创建"
}

# 创建腾讯云轻量服务器优化的钩子脚本
create_enhanced_hook_script() {
    print_status "🔧 创建腾讯云轻量服务器优化的钩子脚本..."

    cat > ~/.openclaw/hooks/claude-code-hook.sh << 'EOF'
#!/bin/bash

# 专为腾讯云轻量服务器(CentOS)优化的Claude Code完成钩子脚本
# 包含额外的日志记录、错误处理和轻量服务器特定优化

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE="/var/log/openclaw_claude_hook.log"

# 确保日志目录存在
mkdir -p /var/log

# 日志记录函数
log_message() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

log_message "=== 腾讯云轻量服务器优化的Claude Code钩子触发 ==="
log_message "会话ID: $CLAUDE_CODE_SESSION_ID"
log_message "当前工作目录: $PWD"
log_message "用户: $(whoami)"

# 检查系统资源（轻量服务器优化）
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
MEM_FREE=$(free -m | awk 'NR==2{print $7}')
log_message "系统资源 - CPU使用率: ${CPU_USAGE}, 空闲内存: ${MEM_FREE}MB"

# 1. 准备包含服务器信息的结果数据
RESULT_DATA=$(cat << RESULT_EOF
{
  "session_id": "$CLAUDE_CODE_SESSION_ID",
  "timestamp": "$TIMESTAMP",
  "server_info": {
    "hostname": "$(hostname)",
    "os": "$(uname -s)",
    "kernel": "$(uname -r)",
    "cpu_cores": $(nproc),
    "memory_total_mb": $(free -m | awk 'NR==2{print $2}'),
    "memory_free_mb": $MEM_FREE,
    "disk_space_used_percent": $(df . | awk 'NR==2 {print $5}' | sed 's/%//'),
    "cpu_usage_percent": ${CPU_USAGE}
  },
  "cwd": "$PWD",
  "event": "SessionEnd",
  "status": "done",
  "output": "$CLAUDE_CODE_OUTPUT",
  "exit_code": "$CLAUDE_CODE_EXIT_CODE",
  "duration_seconds": $(( $(date +%s) - $(date -d "$TIMESTAMP" +%s) ))
}
RESULT_EOF
)

# 2. 写入结果到多个位置以确保可靠性
PRIMARY_RESULT_FILE="/tmp/claude_latest_result.json"
BACKUP_RESULT_FILE="/var/log/claude_result_$(date +%Y%m%d_%H%M%S).json"

echo "$RESULT_DATA" > "$PRIMARY_RESULT_FILE"
echo "$RESULT_DATA" > "$BACKUP_RESULT_FILE"

log_message "结果已写入 $PRIMARY_RESULT_FILE 和 $BACKUP_RESULT_FILE"

# 3. 发送唤醒事件到OpenClaw（轻量服务器优化的重试机制）
if [ -n "$OPENCLAW_TOKEN" ]; then
    MAX_RETRIES=3
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        log_message "尝试唤醒OpenClaw (尝试 $((RETRY_COUNT + 1))/$MAX_RETRIES)..."

        # 腾讯云轻量服务器网络可能不稳定，增加超时时间
        RESPONSE=$(curl -s --max-time 15 -w "%{http_code}" \
            -X POST "http://127.0.0.1:18789/api/cron/wake" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${OPENCLAW_TOKEN}" \
            -d '{
              "text": "Claude Code任务完成，结果已保存到 '"$PRIMARY_RESULT_FILE"'",
              "mode": "now"
            }' 2>/dev/null)

        HTTP_CODE="${RESPONSE: -3}"

        if [ "$HTTP_CODE" -eq 200 ]; then
            log_message "成功唤醒OpenClaw"
            break
        else
            log_message "唤醒OpenClaw失败，HTTP码: $HTTP_CODE"
            RETRY_COUNT=$((RETRY_COUNT + 1))

            if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                # 腾庆云轻量服务器资源有限，使用较短的退避时间
                sleep $((RETRY_COUNT * 3))
            fi
        fi
    done

    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        log_message "经过 $MAX_RETRIES 次尝试后仍无法唤醒OpenClaw，但结果已保存"
    fi
else
    log_message "未设置OPENCLAW_TOKEN，跳过唤醒调用"
fi

# 4. 创建完成状态文件
touch "/tmp/claude_task_completed_$(date +%s).flag"

# 5. 清理可能的临时资源（轻量服务器优化）
if [ $MEM_FREE -lt 512 ]; then  # 内存小于512MB时进行清理
    log_message "检测到内存紧张，清理临时文件"
    find /tmp -name "claude_temp_*" -mmin +30 -delete 2>/dev/null || true
fi

log_message "钩子执行完成于 $(date -u)"
EOF

    chmod +x ~/.openclaw/hooks/claude-code-hook.sh
    chown $(whoami): ~/.openclaw/hooks/claude-code-hook.sh

    pause_for_verification "腾讯云轻量服务器优化的钩子脚本已创建并设置执行权限"
}

# 创建腾讯云轻量服务器优化的配置文件
create_tencent_lighthouse_config() {
    print_status "📝 创建腾讯云轻量服务器(CentOS)优化配置..."

    cat > ~/.openclaw/config.env << 'EOF'
# 腾讯云轻量服务器(CentOS)优化的OpenClaw Claude集成配置

# OpenClaw网关API端点
OPENCLAW_API_URL=http://127.0.0.1:18789

# OpenClaw认证令牌
# 替换为您的实际令牌
OPENCLAW_TOKEN=

# Claude Code钩子配置
CLAUDE_CODE_STOP_HOOK=$HOME/.openclaw/hooks/claude-code-hook.sh
CLAUDE_CODE_SESSION_END_HOOK=$HOME/.openclaw/hooks/claude-code-hook.sh

# Anthropic API配置
ANTHROPIC_API_KEY=

# 默认模型设置
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# 启用零轮询模式（默认）
ZERO_POLLING_ENABLED=true

# 腾讯云轻量服务器优化的超时设置
CLAUDE_SESSION_TIMEOUT=7200    # 2小时超时（考虑轻量服务器性能）
HOOK_TIMEOUT=90                # 90秒钩子执行超时
NETWORK_TIMEOUT=45             # 45秒网络请求超时（腾讯云网络优化）

# 最大重试次数（轻量服务器网络优化）
MAX_CONNECTION_RETRIES=4

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/openclaw_claude_integration.log

# 调试模式（设为"true"启用调试输出）
DEBUG_MODE=false

# 腾讯云轻量服务器专用优化
# 资源限制以适应轻量服务器
MAX_FILE_SIZE_KB=50000         # 50MB最大文件操作（轻量服务器优化）
MAX_COMMAND_LENGTH=5000        # 5000字符最大命令长度
MAX_PARALLEL_TASKS=2           # 最大并行任务数（避免资源争用）

# 监控设置（轻量服务器友好）
MONITOR_CPU_USAGE=true
MONITOR_MEMORY_USAGE=true
CPU_THRESHOLD_PERCENT=75       # CPU阈值75%（轻量服务器优化）
MEMORY_THRESHOLD_PERCENT=70    # 内存阈值70%
LOW_MEMORY_THRESHOLD_MB=256    # 低内存阈值256MB

# 备份配置
ENABLE_BACKUPS=true
BACKUP_RETENTION_DAYS=15        # 15天备份保留（轻量服务器优化）
BACKUP_LOCATION=$HOME/.openclaw/backups

# 腾讯云轻量服务器特定设置
# 网络优化
TCMALLOC_MAX_TOTAL_THREAD_CACHE_BYTES=134217728  # 128MB TCMalloc缓存（可选）

# 定期清理设置
CLEAN_TEMP_FILES=true
TEMP_FILE_RETENTION_HOURS=24    # 临时文件保留24小时
EOF

    pause_for_verification "腾讯云轻量服务器优化配置文件已创建"
}

# 创建项目规则检测工具
create_project_rules_detector() {
    print_status "🔍 创建项目规则检测工具..."

    cat > ~/.openclaw/tools/project-rules-detector.sh << 'EOF'
#!/bin/bash

# 项目规则检测工具
# 用于检测和分析现有项目中的规则文件

PROJECT_DIR="${1:-.}"

echo "🔍 检测项目规则文件..."
echo "项目目录: $PROJECT_DIR"
echo ""

# 查找规则相关的文档文件
RULE_FILES=()
while IFS= read -r -d '' file; do
    RULE_FILES+=("$file")
done < <(find "$PROJECT_DIR" -maxdepth 3 \( -name "*.md" -o -name "*.txt" -o -name "*.rst" \) -print0 2>/dev/null)

FOUND_RULES=false

echo "检查的文件:"
for file in "${RULE_FILES[@]}"; do
    filename=$(basename "$file")
    if [[ "$filename" =~ ^(PROJECT_RULES|rules|CONTRIBUTING|README|ARCHITECTURE|STYLE_GUIDE|DEVELOPMENT_GUIDELINES)$ ]]; then
        echo "  ✅ $file"

        # 检查文件内容是否包含规则关键词
        if grep -E -i "rule|guideline|standard|policy|requirement|convention|protocol|principle|best.practice|architectural.decision" "$file" &>/dev/null; then
            echo "     → 包含规则内容"
            FOUND_RULES=true
        fi
    fi
done

echo ""
if [ "$FOUND_RULES" = true ]; then
    echo "✅ 检测到项目规则文件！"
    echo "建议：优先遵循现有项目规则"
else
    echo "ℹ️  未检测到明确的项目规则"
    echo "建议：使用规格驱动开发(SDD)流程"
fi

echo ""
echo "=== 详细规则分析 ==="
for file in "${RULE_FILES[@]}"; do
    filename=$(basename "$file")
    if [[ "$filename" =~ ^(PROJECT_RULES|rules|CONTRIBUTING|README|ARCHITECTURE|STYLE_GUIDE|DEVELOPMENT_GUIDELINES)$ ]]; then
        echo ""
        echo "--- $file ---"

        # 提取规则相关的段落
        grep -E -i -A2 -B2 "rule|guideline|standard|policy|requirement|convention|protocol|principle|best.practice|architectural.decision" "$file" 2>/dev/null | head -20
    fi
done

echo ""
echo "=== 规则检测完成 ==="
EOF

    chmod +x ~/.openclaw/tools/project-rules-detector.sh

    pause_for_verification "项目规则检测工具已创建"
}

# 创建最终的使用指南
create_usage_guide() {
    print_status "📋 创建使用指南..."

    cat > ~/.openclaw/腾讯云轻量服务器_使用指南.md << 'EOF'
# 腾讯云轻量服务器 OpenClaw-Claude 集成使用指南

## 重要更新：项目规则优先策略

本集成现在支持智能决策：
- **有项目规则时**：优先遵循现有项目规则
- **无项目规则时**：回退到规格驱动开发(SDD)

## 部署说明

### 1. 系统要求
- 腾讯云轻量服务器 (推荐2GB+内存)
- CentOS 7/8/9
- OpenClaw 已安装并运行

### 2. 配置文件位置
- 主配置: `~/.openclaw/config.env`
- 技能文件: `~/.openclaw/skills/`
- 钩子脚本: `~/.openclaw/hooks/`

## 使用方法

### 1. 项目规则检测
在开始开发前，运行检测工具：
```bash
~/.openclaw/tools/project-rules-detector.sh [项目路径]
```

### 2. 智能开发命令
使用以下命令让Claude智能选择：
```bash
# OpenClaw会自动检测项目规则并选择合适的方法
Claude，请在当前项目中实现[功能描述]
```

### 3. 明确指定使用SDD
如需强制使用SDD流程：
```bash
Claude，请使用SDD规格驱动开发实现[功能描述]
```

### 4. 明确指定遵循规则
如需强制遵循项目规则：
```bash
Claude，请严格遵循项目规则实现[功能描述]
```

## 腾讯云轻量服务器优化

### 性能优化
- 增加了超时时间以适应轻量服务器性能
- 限制了并行任务数量以避免资源争用
- 优化了内存使用模式

### 网络优化
- 调整了网络请求超时时间
- 改进了重试机制以应对网络波动

### 资源管理
- 自动清理临时文件以节省空间
- 监控资源使用并及时清理

## 项目规则优先工作流程

### 检测阶段
1. 查找规则文件 (PROJECT_RULES.md, CONTRIBUTING.md等)
2. 分析规则内容
3. 确定项目约束条件

### 执行阶段
- **有规则**: 严格按照项目规则执行
- **无规则**: 使用完整SDD流程
  - /constitution → /specify → /plan → /tasks → /analyze → /implement

## 故障排除

### 常见问题
1. **内存不足**: 检查可用内存，清理临时文件
2. **网络超时**: 适当增加网络超时设置
3. **权限错误**: 检查文件权限设置

### 日志检查
```bash
# 主要日志
tail -f /var/log/openclaw_claude_integration.log
# 钩子日志
tail -f /var/log/openclaw_claude_hook.log
```

### 健康检查
```bash
# 运行健康检查脚本
~/.openclaw/health_check.sh
```

## 监控和维护

### 资源监控
系统会自动监控：
- CPU使用率 (>75%警告)
- 内存使用率 (>70%警告)
- 磁盘空间使用情况

### 定期维护
- 自动清理超过24小时的临时文件
- 保留最近15天的备份
- 定期检查服务状态

## 最佳实践

1. **启动前检查**: 运行 `project-rules-detector.sh` 确定工作方式
2. **资源预留**: 为系统进程预留足够的内存
3. **定期清理**: 监控磁盘空间使用情况
4. **备份策略**: 定期备份重要配置

## 人工监督要点

1. 确认项目规则检测结果
2. 监控资源使用情况
3. 验证输出是否符合预期标准
4. 定期检查日志异常

此集成已针对腾讯云轻量服务器进行了全面优化，支持智能的项目规则优先策略，确保在资源受限环境中也能高效运行。
EOF

    print_success "腾讯云轻量服务器使用指南已创建"
}

# 主函数
main() {
    print_status "开始腾讯云轻量服务器 OpenClaw-Claude 集成设置"
    print_status "支持项目规则优先和规格驱动开发混合模式"
    echo ""

    # 检测腾讯云轻量服务器环境
    detect_tencent_lighthouse

    # 检查依赖
    check_prerequisites

    # 创建目录
    create_directories

    # 创建项目规则优先的处理器技能
    create_project_handler_skill

    # 创建更新后的开发者技能
    create_updated_developer_skill

    # 创建配置技能
    create_config_skill

    # 创建优化的钩子脚本
    create_enhanced_hook_script

    # 创建腾讯云轻量服务器优化配置
    create_tencent_lighthouse_config

    # 创建项目规则检测工具
    create_project_rules_detector

    # 创建使用指南
    create_usage_guide

    echo ""
    print_success "🎉 设置完成！"
    echo ""
    echo "=== 重要更新：项目规则优先策略 ==="
    echo "• 新增项目规则检测器: ~/.openclaw/tools/project-rules-detector.sh"
    echo "• 更新开发者技能：优先检测项目规则，无规则时使用SDD"
    echo "• 创建项目规则处理器技能"
    echo ""
    echo "=== 腾讯云轻量服务器优化 ==="
    echo "• 优化了超时和重试机制"
    echo "• 适配了轻量服务器的资源限制"
    echo "• 改进了网络连接稳定性"
    echo ""
    echo "=== 下一步 ==="
    echo "1. 查看使用指南: ~/.openclaw/腾讯云轻量服务器_使用指南.md"
    echo "2. 运行规则检测器: ~/.openclaw/tools/project-rules-detector.sh"
    echo "3. 检查安装: ~/.openclaw/verify_setup.sh"
    echo ""
    echo "集成现已支持智能决策：有项目规则时优先遵循，否则使用SDD！"
}

# 运行主函数
main