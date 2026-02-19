#!/bin/bash

# OpenClaw-Claude Code Cloud Server Setup (Fixed Syntax Version)
# Simplified version with corrected syntax to pass CI checks

set -e  # Exit on error

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No color

# Colored output functions
print_status() {
    echo -e "${BLUE}[Status]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[Success]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[Warning]${NC} $1"
}

print_error() {
    echo -e "${RED}[Error]${NC} $1"
}

# Skip verification in automated environment
pause_for_verification() {
    echo "[AUTO] Skipping verification: $1"
}

# Detect cloud environment
detect_cloud_environment() {
    print_status "Detecting cloud environment..."

    if [ -f /sys/class/dmi/id/product_name ]; then
        PRODUCT_NAME=$(cat /sys/class/dmi/id/product_name 2>/dev/null || echo "unknown")
        print_status "Cloud provider detected: $PRODUCT_NAME"
    else
        print_warning "Could not detect cloud provider"
    fi
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check if essential tools are available
    for cmd in curl; do
        if ! command -v "$cmd" &> /dev/null; then
            print_error "$cmd is not installed"
            exit 1
        fi
    done

    print_success "Prerequisites satisfied"
}

# Create main directories
create_directories() {
    print_status "Creating OpenClaw directories..."

    mkdir -p ~/.openclaw/skills
    mkdir -p ~/.openclaw/hooks
    mkdir -p ~/.openclaw/tools
    mkdir -p ~/.openclaw/backups

    print_success "Directory structure created"
}

# Create Claude Code Developer Skill
create_developer_skill() {
    print_status "Creating Claude Code Developer Skill..."

    mkdir -p ~/.openclaw/skills/claude-code-developer

    cat > ~/.openclaw/skills/claude-code-developer/SKILL.md << 'EOF_SKILL'
# Claude Code Developer Skill

## Purpose
This skill enables Claude Code to operate in a specification-driven development mode with OpenClaw integration.

## Features
- Zero-polling completion notifications
- Backup storage of results
- Cloud-optimized settings
- Project rule prioritization

## Workflow
1. Define your project specifications
2. Claude implements following the specs
3. Completion automatically notified to OpenClaw
4. Results backed up for reliability

## Commands
- Use normal Claude Code commands but with OpenClaw integration
- Results are stored to /tmp/claude_latest_result.json
- OpenClaw is notified via API when tasks complete

## Notes
- Requires Claude Code to be installed separately
- Uses the hook system for asynchronous notifications
EOF_SKILL

    print_success "Claude Code Developer Skill created"
}

# Create Claude Code Configurator Skill
create_config_skill() {
    print_status "Creating Claude Code Configurator Skill..."

    mkdir -p ~/.openclaw/skills/claude-code-configurator

    cat > ~/.openclaw/skills/claude-code-configurator/SKILL.md << 'EOF_CONFIG'
# Claude Code Configurator Skill

## Purpose
This skill provides configuration capabilities for Claude Code integration with OpenClaw.

## Features
- API key management
- Model configuration
- Custom provider setup
- Connection testing

## Commands
- claude-config --preset <preset_name> --api-key <api_key>
- claude-custom --id <provider_id> --name <name> ...
- claude-test
- claude-ignore

## Presets Supported
- anthropic: Anthropic Claude models
- openai: OpenAI GPT models
- zhipu: Zhipu GLM models
- qwen: Tongyi Qwen models
- deepseek: DeepSeek models
- kimi: Kimi models
- minimax: MiniMax models

## Security Notes
- Interactive API key input
- SSL verification enabled by default
- Support for skipping connection tests
EOF_CONFIG

    print_success "Claude Code Configurator Skill created"
}

# Create enhanced hook script for cloud environments
create_hook_script() {
    print_status "Creating enhanced hook script for cloud environment..."

    cat > ~/.openclaw/hooks/claude-code-hook.sh << 'EOF_HOOK'
#!/bin/bash

# Enhanced Claude Code completion hook for cloud environments
# Includes additional logging, error handling, and cloud-specific optimizations

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE="/var/log/openclaw_claude_hook.log"

# Ensure log directory exists
mkdir -p /var/log

# Function to log with timestamp
log_message() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

log_message "=== Claude Code hook triggered ==="
log_message "Session ID: $CLAUDE_CODE_SESSION_ID"
log_message "Current working directory: $PWD"
log_message "User: $(whoami)"

# Capture execution environment for debugging
log_message "Environment variables: CLAUDE_CODE_SESSION_ID, PWD, USER"

# 1. Prepare result data with comprehensive session information
RESULT_DATA=$(cat << RESULT_EOF
{
  "session_id": "$CLAUDE_CODE_SESSION_ID",
  "timestamp": "$TIMESTAMP",
  "server_info": {
    "hostname": "$(hostname)",
    "cloud_provider": "$(if [ -f /sys/class/dmi/id/product_name ]; then cat /sys/class/dmi/id/product_name 2>/dev/null; else echo 'unknown'; fi)",
    "os": "$(uname -s)",
    "kernel": "$(uname -r)"
  },
  "cwd": "$PWD",
  "event": "SessionEnd",
  "status": "done",
  "output": "$CLAUDE_CODE_OUTPUT",
  "exit_code": "$CLAUDE_CODE_EXIT_CODE",
  "duration_seconds": $(( $(date +%s) - $SECONDS ))
}
RESULT_EOF
)

# 2. Write result to multiple locations for redundancy
PRIMARY_RESULT_FILE="/tmp/claude_latest_result.json"
BACKUP_RESULT_FILE="/var/log/claude_result_$(date +%Y%m%d_%H%M%S).json"

echo "$RESULT_DATA" > "$PRIMARY_RESULT_FILE"
echo "$RESULT_DATA" > "$BACKUP_RESULT_FILE"

log_message "Result written to $PRIMARY_RESULT_FILE and $BACKUP_RESULT_FILE"

# 3. Send Wake Event to OpenClaw with retry mechanism
if [ -n "$OPENCLAW_TOKEN" ]; then
    MAX_RETRIES=3
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        log_message "Attempting to wake OpenClaw (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)..."

        RESPONSE=$(curl -s -w "%{http_code}" \
            -X POST "http://127.0.0.1:18789/api/cron/wake" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${OPENCLAW_TOKEN}" \
            -d '{
              "text": "Claude Code任务完成，结果已保存到 '"$PRIMARY_RESULT_FILE"'",
              "mode": "now"
            }' 2>/dev/null)

        HTTP_CODE="${RESPONSE: -3}"

        if [ "$HTTP_CODE" -eq 200 ]; then
            log_message "Successfully woken OpenClaw"
            break
        else
            log_message "Failed to wake OpenClaw, HTTP code: $HTTP_CODE"
            RETRY_COUNT=$((RETRY_COUNT + 1))

            if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                sleep $((RETRY_COUNT * 2))  # Exponential backoff
            fi
        fi
    done

    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        log_message "Failed to wake OpenClaw after $MAX_RETRIES attempts, but result was saved"
    fi
else
    log_message "OPENCLAW_TOKEN not set, skipping wake call"
fi

# 4. Create a status file to indicate completion
touch "/tmp/claude_task_completed_$(date +%s).flag"

log_message "Hook execution completed at $(date -u)"
EOF_HOOK

    chmod +x ~/.openclaw/hooks/claude-code-hook.sh
    print_success "Enhanced hook script created and made executable"
}

# Create cloud-optimized configuration
create_config() {
    print_status "Creating cloud-optimized configuration file..."

    cat > ~/.openclaw/config.env << 'EOF_CONFIG_ENV'
# OpenClaw Configuration for Claude Code Integration - Cloud Optimized

# API Endpoint for OpenClaw Gateway
OPENCLAW_API_URL=http://127.0.0.1:18789

# OpenClaw Authentication Token
# Replace with your actual token
OPENCLAW_TOKEN=

# Claude Code Hook Configuration
CLAUDE_CODE_STOP_HOOK=$HOME/.openclaw/hooks/claude-code-hook.sh
CLAUDE_CODE_SESSION_END_HOOK=$HOME/.openclaw/hooks/claude-code-hook.sh

# Anthropic API Configuration
ANTHROPIC_API_KEY=

# Default model settings
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Enable zero-polling mode by default
ZERO_POLLING_ENABLED=true

# Timeout settings
CLAUDE_SESSION_TIMEOUT=3600  # 1 hour timeout
HOOK_TIMEOUT=60  # 60 seconds for hook execution (increased for cloud)

# Logging configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/openclaw_claude_integration.log

# Debug mode (set to "true" to enable debug output)
DEBUG_MODE=false

# Cloud-specific optimizations
# Increase timeouts for potential network latency in cloud environments
NETWORK_TIMEOUT=30
MAX_CONNECTION_RETRIES=5

# Resource limits to prevent excessive usage in cloud environment
MAX_FILE_SIZE_KB=100000  # 100MB max file operations
MAX_COMMAND_LENGTH=10000  # Max command length to prevent buffer overflow

# Backup configuration (for cloud reliability)
ENABLE_BACKUPS=true
BACKUP_RETENTION_DAYS=30
BACKUP_LOCATION=$HOME/.openclaw/backups

# Monitoring settings
MONITOR_CPU_USAGE=true
MONITOR_MEMORY_USAGE=true
CPU_THRESHOLD_PERCENT=80
MEMORY_THRESHOLD_PERCENT=85
EOF_CONFIG_ENV

    print_success "Cloud-optimized configuration file created"
}

# Create verification script
create_verification_script() {
    print_status "Creating verification script..."

    cat > ~/.openclaw/verify_setup.sh << 'EOF_VERIFY'
#!/bin/bash

# Comprehensive verification script for OpenClaw-Claude integration

echo "🔍 Verifying OpenClaw-Claude Code Integration Setup..."
echo "====================================================="

# Function to print verification results
print_result() {
    STATUS=$1
    MESSAGE=$2

    if [ "$STATUS" = "PASS" ]; then
        echo -e "\033[0;32m✓ PASS\033[0m $MESSAGE"
    elif [ "$STATUS" = "WARN" ]; then
        echo -e "\033[1;33m! WARN\033[0m $MESSAGE"
    else
        echo -e "\033[0;31m✗ FAIL\033[0m $MESSAGE"
    fi
}

# Check if OpenClaw is running
echo ""
echo "Checking OpenClaw status..."
if curl -s --max-time 10 http://127.0.0.1:18789/api/health > /dev/null 2>&1; then
    print_result "PASS" "OpenClaw is running and accessible"
else
    print_result "FAIL" "OpenClaw is not running or not accessible at http://127.0.0.1:18789"
    echo "💡 Hint: Start OpenClaw first before using this integration"
fi

echo ""
echo "Checking skills..."
if [ -f ~/.openclaw/skills/claude-code-developer/SKILL.md ]; then
    print_result "PASS" "Claude Code Developer Skill found"
else
    print_result "FAIL" "Claude Code Developer Skill missing"
fi

if [ -f ~/.openclaw/skills/claude-code-configurator/SKILL.md ]; then
    print_result "PASS" "Claude Code Configurator Skill found"
else
    print_result "FAIL" "Claude Code Configurator Skill missing"
fi

echo ""
echo "Checking hooks..."
if [ -f ~/.openclaw/hooks/claude-code-hook.sh ]; then
    print_result "PASS" "Claude Code Hook script found"
    if [ -x ~/.openclaw/hooks/claude-code-hook.sh ]; then
        print_result "PASS" "Hook script is executable"
    else
        print_result "FAIL" "Hook script is not executable"
    fi
else
    print_result "FAIL" "Claude Code Hook script missing"
fi

echo ""
echo "Checking configuration..."
if [ -f ~/.openclaw/config.env ]; then
    print_result "PASS" "Configuration file found"

    # Check if API keys are set
    if grep -q "ANTHROPIC_API_KEY=.*[^=]$" ~/.openclaw/config.env 2>/dev/null && [ -z "$ANTHROPIC_API_KEY" ]; then
        print_result "WARN" "ANTHROPIC_API_KEY is not set in configuration"
    else
        print_result "PASS" "ANTHROPIC_API_KEY is set"
    fi

    if grep -q "OPENCLAW_TOKEN=.*[^=]$" ~/.openclaw/config.env 2>/dev/null && [ -z "$OPENCLAW_TOKEN" ]; then
        print_result "WARN" "OPENCLAW_TOKEN is not set in configuration"
    else
        print_result "PASS" "OPENCLAW_TOKEN is set"
    fi
else
    print_result "FAIL" "Configuration file missing"
fi

echo ""
echo "Checking permissions..."
PERMS=$(stat -c %a ~/.openclaw 2>/dev/null || echo "unknown")
if [ "$PERMS" = "700" ]; then
    print_result "PASS" "Main directory has secure permissions (700)"
else
    print_result "WARN" "Main directory permissions are $PERMS, consider changing to 700"
fi

echo ""
echo "Checking system resources..."
TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
USED_MEM=$(free -m | awk 'NR==2{print $3}')
MEM_PERCENT=$(awk "BEGIN {printf \"%.2f\", $USED_MEM * 100 / $TOTAL_MEM}")
echo "Memory usage: ${MEM_PERCENT}% (${USED_MEM}MB/${TOTAL_MEM}MB)"

if (( $(echo "$MEM_PERCENT > 85" | bc -l) )); then
    print_result "WARN" "Memory usage is high ($MEM_PERCENT%)"
else
    print_result "PASS" "Memory usage is acceptable ($MEM_PERCENT%)"
fi

echo ""
echo "Skills available for OpenClaw:"
echo "• claude-code-developer: For spec-driven development"
echo "• claude-code-configurator: For Claude Code configuration"

echo ""
echo "====================================================="
echo "Setup verification complete."
EOF_VERIFY

    chmod +x ~/.openclaw/verify_setup.sh
    print_success "Verification script created and made executable"
}

# Create project rules detector script
create_project_rules_detector() {
    print_status "Creating project rules detector script..."

    cat > ~/.openclaw/tools/project-rules-detector.sh << 'EOF_DETECTOR'
#!/bin/bash

# Project Rules Detector for OpenClaw-Claude Integration
# Automatically detects existing project rules and prioritizes them over SDD

PROJECT_DIR="${1:-.}"

echo "🔍 Detecting project rules in: $PROJECT_DIR"

# Define possible project rule files
RULE_FILES=(
    "PROJECT_RULES.md"
    "CONTRIBUTING.md"
    "CONVENTIONS.md"
    "STYLEGUIDE.md"
    ".github/CONTRIBUTING.md"
    "docs/CONTRIBUTING.md"
    "doc/CONTRIBUTING.md"
    "README.md"
    "DEVELOPMENT.md"
    "DEV_GUIDELINES.md"
    "ARCHITECTURE.md"
    "DESIGN.md"
    "SPECIFICATIONS.md"
    "PROCESS.md"
    "WORKFLOW.md"
)

FOUND_RULES=()

for rule_file in "${RULE_FILES[@]}"; do
    if [ -f "$PROJECT_DIR/$rule_file" ]; then
        echo "✓ Found project rule file: $rule_file"
        FOUND_RULES+=("$rule_file")

        # Check if the file contains actual rule-like content
        if grep -i -E "rule|guideline|standard|convention|principle|pattern|best.practice|do.not|must|should|recommended|avoid|follow" "$PROJECT_DIR/$rule_file" > /dev/null 2>&1; then
            echo "  → Contains rule-like content, will be prioritized"
        fi
    fi
done

if [ ${#FOUND_RULES[@]} -gt 0 ]; then
    echo ""
    echo "🎯 Project rules detected. Integration will prioritize these rules over SDD."
    echo "Files found: ${FOUND_RULES[*]}"

    # Export environment variable to signal rules were found
    export PROJECT_RULES_FOUND=1
    exit 0
else
    echo "ℹ️  No project rules detected. Integration will use SDD (Specification Driven Development) mode."
    export PROJECT_RULES_FOUND=0
    exit 1
fi
EOF_DETECTOR

    chmod +x ~/.openclaw/tools/project-rules-detector.sh
    print_success "Project rules detector script created and made executable"
}

# Create health check script
create_health_check() {
    print_status "Creating health check script..."

    cat > ~/.openclaw/health_check.sh << 'EOF_HEALTH'
#!/bin/bash

# Health Check Script for OpenClaw-Claude Integration on Cloud Servers

echo "🏥 OpenClaw-Claude Health Check"
echo "=============================="

# Check OpenClaw availability
echo ""
echo "1. Checking OpenClaw Service..."
if curl -s --max-time 10 http://127.0.0.1:18789/api/health > /dev/null 2>&1; then
    echo "   ✓ OpenClaw service is running"
else
    echo "   ✗ OpenClaw service is not accessible"
fi

# Check Claude Code integration
echo ""
echo "2. Checking Claude Code Integration..."
if command -v claude-code &> /dev/null; then
    echo "   ✓ Claude Code CLI is available"
else
    echo "   ⚠ Claude Code CLI is not installed"
fi

# Check directory structure
echo ""
echo "3. Checking Directory Structure..."
REQUIRED_DIRS=(
    "$HOME/.openclaw"
    "$HOME/.openclaw/skills"
    "$HOME/.openclaw/hooks"
    "$HOME/.openclaw/tools"
    "$HOME/.openclaw/backups"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✓ $dir exists"
    else
        echo "   ✗ $dir missing"
    fi
done

# Check configuration
echo ""
echo "4. Checking Configuration Files..."
CONFIG_FILES=(
    "$HOME/.openclaw/config.env"
    "$HOME/.openclaw/hooks/claude-code-hook.sh"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file exists"
        if [ -r "$file" ]; then
            echo "   ✓ $file is readable"
        else
            echo "   ✗ $file is not readable"
        fi
        if [ -x "$file" ] && [[ "$file" == *.sh ]]; then
            echo "   ✓ $file is executable"
        fi
    else
        echo "   ✗ $file missing"
    fi
done

# Check skills
echo ""
echo "5. Checking Skills..."
SKILLS=(
    "$HOME/.openclaw/skills/claude-code-developer/SKILL.md"
    "$HOME/.openclaw/skills/claude-code-configurator/SKILL.md"
)

for skill in "${SKILLS[@]}"; do
    if [ -f "$skill" ]; then
        echo "   ✓ $skill exists"
    else
        echo "   ✗ $skill missing"
    fi
done

# Resource check
echo ""
echo "6. Checking System Resources..."
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
MEM_TOTAL=$(free -m | awk 'NR==2{print $2}')
MEM_USED=$(free -m | awk 'NR==2{print $3}')
MEM_PERCENT=$(awk "BEGIN {printf \"%.2f\", $MEM_USED * 100 / $MEM_TOTAL}")

echo "   CPU Usage: ${CPU_USAGE}%"
echo "   Memory: ${MEM_USED}MB/${MEM_TOTAL}MB (${MEM_PERCENT}%)"

# Check if resources are within thresholds
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "   ⚠ High CPU usage detected"
fi

if (( $(echo "$MEM_PERCENT > 85" | bc -l) )); then
    echo "   ⚠ High memory usage detected"
fi

echo ""
echo "7. Checking Log Files..."
LOG_FILES=(
    "/var/log/openclaw_claude_hook.log"
    "/tmp/openclaw_claude_integration.log"
)

for log in "${LOG_FILES[@]}"; do
    if [ -f "$log" ]; then
        echo "   ✓ $log exists"
        RECENT_LINES=$(tail -n 5 "$log" 2>/dev/null | wc -l)
        echo "     Last $RECENT_LINES lines:"
        tail -n 5 "$log" 2>/dev/null | sed 's/^/     /'
    else
        echo "   - $log does not exist yet"
    fi
done

echo ""
echo "Health check completed."
EOF_HEALTH

    chmod +x ~/.openclaw/health_check.sh
    print_success "Health check script created and made executable"
}

# Main execution
main() {
    print_status "Starting Cloud Server Setup for OpenClaw-Claude Integration"

    detect_cloud_environment
    check_prerequisites
    create_directories
    create_developer_skill
    create_config_skill
    create_hook_script
    create_config
    create_verification_script
    create_project_rules_detector
    create_health_check

    print_success "Cloud server setup completed successfully!"
    print_status "Please refer to the documentation for configuration and usage instructions."
    print_status "Run ~/.openclaw/verify_setup.sh to verify the installation."
}

# Execute main function
main "$@"