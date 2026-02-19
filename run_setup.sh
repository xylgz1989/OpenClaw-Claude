#!/bin/bash

# OpenClaw-Claude Code Integration Setup Runner
# Wrapper script to run the main setup with configuration prompts

echo "=================================================="
echo "OpenClaw-Claude Code Integration Setup"
echo "Cloud Server Edition with Human-in-the-Loop"
echo "=================================================="
echo ""

# Function to prompt for API keys
prompt_for_config() {
    echo "🔐 Configuration Setup"
    echo "----------------------"
    echo "We need your API keys to complete the setup."
    echo "These will be stored securely in ~/.openclaw/config.env"
    echo ""

    read -p "Enter your Anthropic API Key (or press Enter to skip for now): " ANTHROPIC_KEY
    if [ -n "$ANTHROPIC_KEY" ]; then
        echo "Updating configuration with Anthropic API Key..."
        sed -i "s|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=$ANTHROPIC_KEY|" ~/.openclaw/config.env
    fi

    read -p "Enter your OpenClaw Token (or press Enter to skip for now): " OPENCLAW_TOKEN
    if [ -n "$OPENCLAW_TOKEN" ]; then
        echo "Updating configuration with OpenClaw Token..."
        sed -i "s|^OPENCLAW_TOKEN=.*|OPENCLAW_TOKEN=$OPENCLAW_TOKEN|" ~/.openclaw/config.env
    fi

    echo ""
    echo "✅ Configuration updated!"
    echo ""
}

# Check if setup has been run before
if [ -d ~/.openclaw/skills ]; then
    echo "⚠️  Existing OpenClaw setup detected!"
    echo ""
    echo "Options:"
    echo "  1. Continue with configuration setup only"
    echo "  2. Run full setup again (will overwrite existing files)"
    echo "  3. Exit"
    echo ""

    while true; do
        read -p "Choose an option (1-3): " choice
        case $choice in
            1)
                echo "Proceeding with configuration setup..."
                if [ -f ~/.openclaw/config.env ]; then
                    prompt_for_config
                    echo "Configuration updated. You can now use the integration."
                    echo "Run verification: ~/.openclaw/verify_setup.sh"
                else
                    echo "Configuration file not found. Please run the full setup first."
                fi
                break
                ;;
            2)
                echo "Running full setup again..."
                break
                ;;
            3)
                echo "Exiting setup."
                exit 0
                ;;
            *)
                echo "Please choose 1, 2, or 3."
                ;;
        esac
    done
else
    echo "No existing OpenClaw setup detected. Proceeding with full setup..."
    echo ""
fi

echo ""
echo "Starting the main setup script..."
echo ""

# Run the main setup script
./setup_openclaw_claude_cloud.sh

# After setup, optionally configure API keys
echo ""
echo "Would you like to configure your API keys now?"
while true; do
    read -p "Configure now? (y/n): " yn
    case $yn in
        [Yy]* )
            prompt_for_config
            break
            ;;
        [Nn]* )
            echo "You can configure your API keys later by editing ~/.openclaw/config.env"
            break
            ;;
        * ) echo "Please answer y or n.";;
    esac
done

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "============================"
echo ""
echo "Next Steps:"
echo "1. Verify your setup: ~/.openclaw/verify_setup.sh"
echo "2. Check system health: ~/.openclaw/health_check.sh"
echo "3. Review usage guide: ~/.openclaw/CLOUD_USAGE_GUIDE.md"
echo ""
echo "For production use, consider:"
echo "- Running under a dedicated user account"
echo "- Setting up systemd service for OpenClaw"
echo "- Configuring firewall rules"
echo "- Setting up log rotation"
echo ""
echo "The integration is now ready to use with human oversight capabilities!"