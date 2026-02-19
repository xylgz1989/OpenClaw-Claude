# OpenClaw-Claude Code Integration Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Features](#features)
6. [Troubleshooting](#troubleshooting)

## Overview

The OpenClaw-Claude Code Integration provides a seamless bridge between OpenClaw and Claude Code, featuring intelligent project rule prioritization and Tencent Cloud Light Server optimization. This integration enables efficient project development by automatically detecting project rules and applying the most appropriate development methodology.

### Key Benefits:
- **Smart Decision Making**: Automatically detects and prioritizes existing project rules
- **Flexible Fallback**: Falls back to Specification Driven Development (SDD) when no rules exist
- **Cloud Optimized**: Specifically designed for resource-constrained environments like Tencent Cloud Light Server
- **Secure**: Handles sensitive API keys safely with proper permissions

## Installation

### Prerequisites
- Linux/Unix environment (tested on CentOS for Tencent Cloud Light Server)
- bash shell
- curl command-line tool
- OpenClaw installed and running

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/openclaw-claude-integration.git
   cd openclaw-claude-integration
   ```

2. Make the setup script executable and run it:
   ```bash
   chmod +x run_tencent_setup.sh
   ./run_tencent_setup.sh
   ```

3. Follow the prompts to complete the installation

## Configuration

### API Keys
After installation, configure your API keys in the configuration file:
```bash
nano ~/.openclaw/config.env
```

Set the following variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `OPENCLAW_TOKEN`: Your OpenClaw authentication token

### Environment Variables
The configuration file includes various settings optimized for cloud environments:
- Network timeouts adjusted for cloud connectivity
- Resource limits appropriate for light servers
- Logging configuration
- Backup settings

## Usage

### Project Rule Detection
To detect project rules in a specific directory:
```bash
~/.openclaw/tools/project-rules-detector.sh [project_directory]
```

### System Health Check
Monitor system status and resource usage:
```bash
~/.openclaw/health_check.sh
```

### Installation Verification
Verify that all components are correctly installed:
```bash
~/.openclaw/verify_setup.sh
```

### Integration Commands
Once configured, use natural language commands in OpenClaw such as:
- `Claude, please implement [feature] following the project rules`
- `Claude, please use SDD to develop [feature]`

## Features

### 1. Intelligent Project Rule Prioritization
The system intelligently handles different development scenarios:

**With Project Rules**:
1. Detects existing project rules in files like PROJECT_RULES.md, CONTRIBUTING.md, etc.
2. Parses and understands the project's constraints and requirements
3. Executes tasks following the established rules and conventions

**Without Project Rules**:
1. Detects absence of project rules
2. Automatically falls back to Specification Driven Development (SDD) workflow
3. Follows the complete SDD process: constitution → specify → plan → tasks → analyze → implement

### 2. Tencent Cloud Light Server Optimization
The integration includes several optimizations for resource-constrained environments:

- **Extended Timeouts**: Network and process timeouts adjusted for cloud performance
- **Resource Monitoring**: Automatic monitoring of memory and disk usage
- **Efficient Processes**: Optimized for limited CPU and memory resources
- **Connection Stability**: Enhanced retry mechanisms for cloud network reliability

### 3. Zero-polling Hook System
An efficient notification system that:
- Minimizes token consumption by avoiding constant polling
- Automatically notifies OpenClaw when Claude Code tasks complete
- Stores results in multiple locations for reliability

## Troubleshooting

### Common Issues

#### 1. Permission Errors
If experiencing permission errors:
1. Check that the configuration directory has secure permissions (700):
   ```bash
   chmod 700 ~/.openclaw
   ```

#### 2. API Connection Problems
If API calls are failing:
1. Verify your API keys in `~/.openclaw/config.env`
2. Ensure your network allows connections to Anthropic's API
3. Check for any firewall restrictions

#### 3. OpenClaw Service Not Responding
If the health check shows OpenClaw is not responding:
1. Ensure OpenClaw is installed and running
2. Verify OpenClaw is listening on the expected port (default: 18789)
3. Check OpenClaw logs for any errors

#### 4. Script Execution Errors
If bash scripts are not executing:
1. Ensure scripts have execute permissions:
   ```bash
   chmod +x ~/.openclaw/hooks/*.sh
   chmod +x ~/.openclaw/tools/*.sh
   ```
2. Check bash version compatibility

### Support
If you encounter issues not addressed here:
1. Check the [Issues](https://github.com/yourusername/openclaw-claude-integration/issues) page
2. File a new issue with detailed information about your problem
3. Include your OS, OpenClaw version, and error messages