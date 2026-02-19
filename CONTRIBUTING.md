# Contributing to OpenClaw-Claude Code Integration

Thank you for your interest in contributing to OpenClaw-Claude Code Integration! This document outlines the process for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check the existing issues to see if the bug has already been reported
2. Open a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, OpenClaw version, etc.)

### Suggesting Enhancements

1. Check existing issues for similar suggestions
2. Open a new issue with:
   - Clear description of the enhancement
   - Reason why it would be useful
   - Potential implementation approach (if known)

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Update documentation as needed
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/openclaw-claude-integration.git
   cd openclaw-claude-integration
   ```

2. Make sure you have the prerequisites installed:
   - bash shell
   - curl
   - OpenClaw installed and running

3. Run the setup script:
   ```bash
   chmod +x run_tencent_setup.sh
   ./run_tencent_setup.sh
   ```

## Project Specific Guidelines

### 1. Project Rule Prioritization
- Ensure that the system correctly detects and prioritizes project rules
- Maintain backward compatibility with SDD fallback
- Update the project-rules-detector.sh to recognize new rule formats

### 2. Tencent Cloud Light Server Optimization
- Optimize for resource-constrained environments
- Use appropriate timeouts and retry mechanisms
- Implement efficient resource monitoring

### 3. Security Considerations
- Handle API keys securely
- Don't hardcode sensitive information
- Follow security best practices in bash scripting

## Coding Standards

- Use descriptive function and variable names
- Add comments for complex logic
- Follow bash best practices
- Ensure cross-platform compatibility where possible
- Include error handling for critical operations

## Running Tests

Currently, the integration relies on manual verification. You can test the installation by running:

```bash
~/.openclaw/verify_setup.sh
~/.openclaw/health_check.sh
```

## Pull Request Process

1. Ensure your code follows the project's style and standards
2. Update documentation as needed
3. Add tests for new functionality
4. Verify that all existing functionality still works
5. Submit your PR with a clear description of the changes

## Questions?

If you have any questions about contributing, feel free to open an issue or contact the maintainers.

Thank you for your contributions!