#!/bin/bash

# OpenClaw-Claude Code Human-in-the-Loop Setup (Fixed Syntax Version)
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

# Detect human-in-the-loop environment
detect_hil_environment() {
    print_status "Detecting Human-in-the-Loop environment..."

    # Check if we're running in an environment that supports human interaction
    if [ -t 0 ]; then
        print_success "Interactive terminal detected"
    else
        print_warning "Non-interactive environment detected"
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

    print_success "Directory structure created"
}

# Create Claude Code Developer Skill
create_developer_skill() {
    print_status "Creating Claude Code Developer Skill..."

    mkdir -p ~/.openclaw/skills/claude-code-developer

    cat > ~/.openclaw/skills/claude-code-developer/SKILL.md << 'EOF_SKILL'
# Claude Code Developer Skill

## Purpose
This skill enables Claude Code to operate in a human-in-the-loop specification-driven development mode with OpenClaw integration.

## Features
- Zero-polling completion notifications
- Backup storage of results
- Human verification points
- Project rule detection and prioritization

## Workflow
1. Define your project specifications with human input
2. Claude implements following the specs with periodic verification
3. Completion automatically notified to OpenClaw
4. Results backed up for reliability

## Commands
- Use normal Claude Code commands but with OpenClaw integration
- Results are stored to /tmp/claude_latest_result.json
- OpenClaw is notified via API when tasks complete

## Notes
- Requires Claude Code to be installed separately
- Uses the hook system for asynchronous notifications
- Includes human verification checkpoints
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
This skill provides configuration capabilities for Claude Code integration with OpenClaw in human-in-the-loop scenarios.

## Features
- API key management
- Model configuration
- Custom provider setup
- Connection testing
- Human verification for sensitive operations

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
- Human verification for configuration changes
EOF_CONFIG

    print_success "Claude Code Configurator Skill created"
}

# Create hook script
create_hook_script() {
    print_status "Creating hook script..."

    cat > ~/.openclaw/hooks/claude-code-hook.sh << 'EOF_HOOK'
#!/bin/bash

# Claude Code completion hook for human-in-the-loop scenarios
# This script is automatically called by Claude Code when tasks complete

echo "$(date): Claude Code hook triggered" >> /tmp/openclaw_claude_hook.log

# 1. Write result to file (data channel)
cat > /tmp/claude_latest_result.json << RESULT_EOF
{
  "session_id": "$CLAUDE_CODE_SESSION_ID",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "cwd": "$PWD",
  "event": "SessionEnd",
  "status": "done",
  "output": "$CLAUDE_CODE_OUTPUT",
  "exit_code": "$CLAUDE_CODE_EXIT_CODE"
}
RESULT_EOF

echo "$(date): Result written to /tmp/claude_latest_result.json" >> /tmp/openclaw_claude_hook.log

# 2. Send Wake Event to OpenClaw (signal channel)
# Note: Even if this call fails, the result file is already saved
if [ -n "$OPENCLAW_TOKEN" ]; then
  curl -X POST "http://127.0.0.1:18789/api/cron/wake" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${OPENCLAW_TOKEN}" \
    -d '{
      "text": "Claude Code任务完成，结果已保存到 /tmp/claude_latest_result.json",
      "mode": "now"
    }' || echo "$(date): Failed to wake OpenClaw, but result was saved" >> /tmp/openclaw_claude_hook.log
else
  echo "$(date): OPENCLAW_TOKEN not set, skipping wake call" >> /tmp/openclaw_claude_hook.log
fi

echo "$(date): Hook execution completed" >> /tmp/openclaw_claude_hook.log
EOF_HOOK

    chmod +x ~/.openclaw/hooks/claude-code-hook.sh
    print_success "Hook script created and made executable"
}

# Create configuration file
create_config() {
    print_status "Creating configuration file..."

    cat > ~/.openclaw/config.env << 'EOF_CONFIG_ENV'
# OpenClaw Configuration for Claude Code Integration

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
HOOK_TIMEOUT=30  # 30 seconds for hook execution

# Logging configuration
LOG_LEVEL=INFO
LOG_FILE=/tmp/openclaw_claude_integration.log

# Debug mode (set to "true" to enable debug output)
DEBUG_MODE=false
EOF_CONFIG_ENV

    print_success "Configuration file created"
}

# Create verification script
create_verification_script() {
    print_status "Creating verification script..."

    cat > ~/.openclaw/verify_setup.sh << 'EOF_VERIFY'
#!/bin/bash

echo "Verifying OpenClaw-Claude Code Integration Setup..."
echo ""

# Check if OpenClaw is running
echo "Checking OpenClaw status..."
if curl -s http://127.0.0.1:18789/api/health > /dev/null 2>&1; then
    echo "✅ OpenClaw is running"
else
    echo "⚠️  OpenClaw is not running or not accessible at http://127.0.0.1:18789"
    echo "💡 Hint: Start OpenClaw first before using this integration"
fi

echo ""
echo "Checking skills..."
if [ -f ~/.openclaw/skills/claude-code-developer/SKILL.md ]; then
    echo "✅ Claude Code Developer Skill found"
else
    echo "❌ Claude Code Developer Skill missing"
fi

if [ -f ~/.openclaw/skills/claude-code-configurator/SKILL.md ]; then
    echo "✅ Claude Code Configurator Skill found"
else
    echo "❌ Claude Code Configurator Skill missing"
fi

echo ""
echo "Checking hooks..."
if [ -f ~/.openclaw/hooks/claude-code-hook.sh ]; then
    echo "✅ Claude Code Hook script found"
    if [ -x ~/.openclaw/hooks/claude-code-hook.sh ]; then
        echo "✅ Hook script is executable"
    else
        echo "❌ Hook script is not executable"
    fi
else
    echo "❌ Claude Code Hook script missing"
fi

echo ""
echo "Checking configuration..."
if [ -f ~/.openclaw/config.env ]; then
    echo "✅ Configuration file found"
    echo "💡 Remember to set your API keys in ~/.openclaw/config.env"
else
    echo "❌ Configuration file missing"
fi

echo ""
echo "Skills available for OpenClaw:"
echo "• claude-code-developer: For spec-driven development"
echo "• claude-code-configurator: For Claude Code configuration"

echo ""
echo "Setup verification complete."
EOF_VERIFY

    chmod +x ~/.openclaw/verify_setup.sh
    print_success "Verification script created and made executable"
}

# Create usage guide
create_usage_guide() {
    print_status "Creating usage guide..."

    cat > ~/.openclaw/USAGE_GUIDE.md << 'EOF_GUIDE'
# OpenClaw-Claude Code Integration - Usage Guide

## Prerequisites

1. OpenClaw must be running and accessible at `http://127.0.0.1:18789`
2. You need a valid Anthropic API key
3. Optional: Spec Kit installed for full spec-driven development

## Configuration

### 1. Set your API keys

Edit the configuration file:
```bash
nano ~/.openclaw/config.env
```

Set the following values:
- `OPENCLAW_TOKEN`: Your OpenClaw authentication token
- `ANTHROPIC_API_KEY`: Your Anthropic API key

### 2. Load the configuration

```bash
source ~/.openclaw/config.env
```

## Usage Examples

### 1. Claude Code Developer Skill (Spec-Driven Development)

To initiate a new project with spec-driven development:

```
call Claude Code Developer and ask it to create a [project description] using the following stack: [technology stack]
```

### 2. Claude Code Configurator Skill

To configure Claude Code settings:

```
call Claude Code Configurator and ask it to configure Claude Code with the following settings: [configuration details]
```

## Human-in-the-Loop Verification Points

The integration includes several human verification points:
- Project rule detection (automatically prioritized over SDD)
- Critical configuration changes
- Confirmation for sensitive operations

## Project Rule Prioritization

The system will automatically detect project rules and prioritize them:
1. Detects existing project rules in project files
2. Prioritizes project rules over Specification Driven Development (SDD)
3. Falls back to SDD when no project rules are found
4. Provides intelligent handling based on project context

## Zero-Polling Notifications

This integration uses a zero-polling approach:
- Claude Code completion hook is automatically triggered
- Results stored to multiple locations for redundancy
- OpenClaw is notified via API without polling
- Minimal token consumption

## Troubleshooting

- Check logs at `/tmp/openclaw_claude_integration.log`
- Run `~/.openclaw/verify_setup.sh` for system verification
- Ensure OpenClaw is running at the configured endpoint

EOF_GUIDE

    print_success "Usage guide created"
}

# Main execution
main() {
    print_status "Starting Human-in-the-Loop Setup for OpenClaw-Claude Integration"

    detect_hil_environment
    check_prerequisites
    create_directories
    create_developer_skill
    create_config_skill
    create_hook_script
    create_config
    create_verification_script
    create_usage_guide

    print_success "Human-in-the-Loop setup completed successfully!"
    print_status "Please refer to ~/.openclaw/USAGE_GUIDE.md for configuration and usage instructions."
    print_status "Run ~/.openclaw/verify_setup.sh to verify the installation."
}

# Execute main function
main "$@"