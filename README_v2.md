# OpenClaw + Claude Code 统一配置工具 v2

🚀 一个功能强大的统一配置工具，支持Claude Code LLM配置、OpenClaw配置生成，以及两者之间的联动。

## ✨ 功能特性

### 1. Claude Code LLM配置（参考cc-switch）

- **模型分层策略**: 支持Primary + Fallbacks模型分层
- **上下文文件精简**: 自动创建`.claudeignore`文件
- **预设配置**: 支持9种内置预设，一键切换
- **自定义预设**: 支持添加自定义LLM预设

### 2. 连接验证功能

每种LLM设置后都会自动验证连接，反馈成功或具体失败原因：

- ✅ **连接成功**: 显示延迟和可用模型数量
- ❌ **认证失败**: API Key无效或已过期
- ❌ **权限不足**: 无法访问该资源
- ❌ **模型不存在**: 指定的模型ID无效
- ❌ **速率限制**: 请求过于频繁
- ❌ **网络错误**: DNS解析失败或连接超时
- ❌ **SSL证书错误**: 证书验证失败

### 3. 自定义LLM设置

支持用户添加自定义模型配置：

```bash
# 添加自定义Claude预设
python openclaw_claude_config_v2.py claude-custom \
    --id my-provider \
    --name "My Provider" \
    --description "自定义LLM提供商" \
    --base-url https://api.myprovider.com/v1 \
    --opus-model gpt-4 \
    --sonnet-model gpt-3.5-turbo \
    --haiku-model gpt-3.5-turbo

# 添加自定义OpenClaw模型
python openclaw_claude_config_v2.py openclaw-custom \
    --id myprovider/my-model \
    --name "My Model" \
    --provider myprovider \
    --api-endpoint https://api.myprovider.com/v1
```

### 4. OpenClaw完整配置生成

- **保证配置后可正常运行**
- **模型分层策略**: primary + fallbacks
- **支持通道配置**: 飞书、企业微信、钉钉等
- **配置验证**: 自动检查必需字段和端口范围

### 5. 支持的模型

#### 国内模型 (2026最新)
| 厂商 | 模型 | 上下文 | API定价 |
|------|------|--------|---------|
| 通义千问 | Qwen 3.5-Plus | 1M tokens | ¥0.8/百万 |
| 智谱清言 | GLM-5 | 200K tokens | ¥2.0/百万 |
| DeepSeek | DeepSeek-V4 | 1M tokens | ¥0.5/百万 |
| Kimi | Kimi K2.5 | 256K tokens | ¥0.6/百万 |
| MiniMax | M2.5 | 256K tokens | ¥2.0/百万 |

#### 国际模型
| 厂商 | 模型 | 上下文 | API定价 |
|------|------|--------|---------|
| Anthropic | Claude Opus 4.5 | 200K tokens | $15/百万 |
| Anthropic | Claude Sonnet 4 | 200K tokens | $3/百万 |

## 🚀 快速开始

### 交互式配置向导

```bash
python openclaw_claude_config_v2.py wizard
```

向导将引导您完成：
1. 配置Claude Code LLM（自动测试连接）
2. 配置OpenClaw（自动测试连接）

### 配置Claude Code

```bash
# 使用预设配置（自动测试连接）
python openclaw_claude_config_v2.py claude-config --preset zhipu --api-key YOUR_API_KEY

# 跳过连接测试
python openclaw_claude_config_v2.py claude-config --preset zhipu --api-key YOUR_API_KEY --no-test

# 测试当前配置
python openclaw_claude_config_v2.py claude-test

# 添加自定义预设
python openclaw_claude_config_v2.py claude-custom \
    --id my-provider \
    --name "My Provider" \
    --description "自定义LLM提供商" \
    --base-url https://api.myprovider.com/v1 \
    --opus-model gpt-4 \
    --sonnet-model gpt-3.5-turbo \
    --haiku-model gpt-3.5-turbo
```

### 配置OpenClaw

```bash
# 设置模型（自动测试连接）
python openclaw_claude_config_v2.py openclaw-config \
    --model zhipu/glm-5 \
    --api-key YOUR_API_KEY \
    --base-url https://open.bigmodel.cn/api/paas/v4

# 跳过连接测试
python openclaw_claude_config_v2.py openclaw-config \
    --model zhipu/glm-5 \
    --api-key YOUR_API_KEY \
    --base-url https://open.bigmodel.cn/api/paas/v4 \
    --no-test

# 测试指定provider的连接
python openclaw_claude_config_v2.py openclaw-test --provider zhipu

# 添加自定义模型
python openclaw_claude_config_v2.py openclaw-custom \
    --id myprovider/my-model \
    --name "My Model" \
    --provider myprovider \
    --api-endpoint https://api.myprovider.com/v1

# 验证配置
python openclaw_claude_config_v2.py openclaw-validate
```

### 列出可用模型

```bash
# 列出所有模型
python openclaw_claude_config_v2.py models all

# 仅列出国内模型
python openclaw_claude_config_v2.py models china

# 仅列出国际模型
python openclaw_claude_config_v2.py models international
```

## 📁 配置文件

### Claude Code配置
- 路径: `~/.claude/settings.json`
- 自定义预设: `~/.claude/custom_presets.json`

### OpenClaw配置
- 路径: `~/.openclaw/openclaw.json`
- 自定义模型: `~/.openclaw/custom_models.json`

## 🔧 连接验证说明

工具会在设置LLM后自动测试连接，验证内容包括：

1. **DNS解析**: 检查Base URL是否可解析
2. **网络连接**: 检查是否能连接到服务器
3. **SSL证书**: 检查证书是否有效
4. **认证**: 检查API Key是否有效
5. **权限**: 检查是否有访问权限
6. **模型可用性**: 检查指定模型是否存在

### 错误类型

| 错误类型 | 说明 | 解决方案 |
|---------|------|---------|
| auth | 认证失败 | 检查API Key是否正确 |
| network | 网络错误 | 检查网络连接或Base URL |
| model | 模型不存在 | 检查模型ID是否正确 |
| rate_limit | 速率限制 | 稍后再试或升级套餐 |
| server | 服务器错误 | 服务端问题，稍后重试 |
| config | 配置错误 | 检查配置是否完整 |

## 📋 系统要求

- Python 3.8+
- 支持操作系统: CentOS, Ubuntu, Debian, RHEL, Fedora, Arch, macOS, Windows

## 📄 许可证

MIT License
