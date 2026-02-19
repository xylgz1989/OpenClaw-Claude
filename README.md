# OpenClaw-Claude
you can send message to OpenClaw, OpenClaw call Claude code to work

## OpenClaw-Claude Code Integration Addition

As an extension to the core functionality, this repository also includes:

### ✨ Additional Features

#### 1. Intelligent Project Rule Prioritization
- **Rule Detection**: Automatically detects existing project rules in project files
- **Priority Processing**: Prioritizes project rules over Specification Driven Development (SDD)
- **SDD Fallback**: Falls back to SDD when no project rules are found
- **Smart Decision Making**: Intelligent handling based on project context

#### 2. Tencent Cloud Light Server Optimization
- **Resource Management**: Optimized for resource-constrained environments
- **Network Stability**: Enhanced connection handling for cloud environments
- **Timeout Adjustments**: Tuned timeouts suitable for light servers
- **Monitoring**: Built-in resource and performance monitoring

#### 3. OpenClaw Integration
- **Skill-based Architecture**: Modular skill system for different capabilities
- **Zero-polling Hooks**: Efficient completion notification system
- **Secure Configuration**: Safe API key handling
- **Cross-platform**: Works across different operating systems

### 🚀 Quick Start

#### Prerequisites
- Linux/Unix environment (optimized for Tencent Cloud Light Server)
- bash shell
- curl
- OpenClaw installed and running

#### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/xylgz1989/OpenClaw-Claude.git
   cd OpenClaw-Claude
   ```

2. Run the Tencent Cloud Light Server setup:
   ```bash
   chmod +x run_tencent_setup.sh
   ./run_tencent_setup.sh
   ```

3. Configure your API keys:
   ```bash
   nano ~/.openclaw/config.env
   ```

4. Verify the installation:
   ```bash
   ~/.openclaw/verify_setup.sh
   ```

### 🛠️ Usage

#### Project Rule Detection
To detect project rules in a directory:
```bash
~/.openclaw/tools/project-rules-detector.sh [project_directory]
```

#### System Health Check
Monitor system status:
```bash
~/.openclaw/health_check.sh
```

#### Integration Commands
Once OpenClaw is configured, use natural language commands such as:
```
Claude, please implement [feature] following the project rules
```
or
```
Claude, please use SDD to develop [feature]
```

### 📁 Project Structure

```
OpenClaw-Claude/
├── setup_tencent_lighthouse.sh    # Main setup for Tencent Cloud
├── run_tencent_setup.sh          # Run script for setup
├── verify_installation.sh        # Verify installation
├── docs/                         # Documentation
│   ├── README.md
│   ├── USAGE_GUIDE.md
│   └── TROUBLESHOOTING.md
├── .github/
│   └── workflows/
│       └── ci.yml               # CI/CD pipeline
├── LICENSE
├── CHANGELOG.md
└── CONTRIBUTING.md
```

### ⚙️ Configuration

#### API Keys
Edit `~/.openclaw/config.env` to set:
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `OPENCLAW_TOKEN` - Your OpenClaw authentication token

#### Environment Variables
The configuration file includes:
- Network timeout settings
- Resource limits for light servers
- Logging configuration
- Backup settings

### 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started.

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🛡️ Security

This tool handles API keys and sensitive configuration data. Please follow security best practices:
- Store API keys securely and do not commit them to version control
- Regularly rotate your API keys
- Review the code for any security concerns before using

### 🐛 Issues

If you encounter any problems, please file an issue on the [Issues](https://github.com/xylgz1989/OpenClaw-Claude/issues) page.