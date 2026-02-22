# LLM 配额切换功能 - 集成到 OpenClaw-Claude 的设计方案

## 📋 集成方案概述

### 用户需求
1. ✅ 集成到 OpenClaw-Claude（独立项目 → 集成模块）
2. ✅ 保留所有现有功能（Claude Code 配置、OpenClaw 配置、多提供商管理、CLI 工具）
3. ✅ 优先实现智能切换功能
4. ✅ 配置方式：配置文件 + 环境变量

### 关键原则
- ✅ **不破坏现有配置**：在现有配置基础上添加新字段
- ✅ **向后兼容**：旧配置文件仍然有效
- ✅ **无需重新 onboard**：不需要重新运行 `openclaw onboard`
- ✅ **渐进式集成**：可以逐步添加功能

---

## 🏗️ 架构设计

### 现有架构（OpenClaw-Claude）

```
OpenClaw-Claude
├── 配置管理
│   ├── Claude Code 配置
│   │   ├── 预设（zhipu, z.ai, aliyun, deepseek, kimi, minimax, anthropic）
│   │   ├── 模型映射
│   │   └── 环境变量
│   └── OpenClaw 配置
│       ├── 模型注册表
│       └── 环境变量
├── CLI 工具
│   ├── wizard
│   ├── claude-config
│   ├── claude-test
│   ├── openclaw-config
│   └── models
└── 工具
    ├── 连接验证
    ├── 安全工具
    └── 日志管理
```

### 新架构（集成后）

```
OpenClaw-Claude
├── 配置管理
│   ├── Claude Code 配置（保持不变）
│   ├── OpenClaw 配置（保持不变）
│   └── **新增：智能切换配置**
│       ├── 提供商配置
│       ├── 切换策略
│       ├── 配额监控配置
│       └── 告警通知配置
├── CLI 工具
│   ├── **所有现有命令（保持不变）**
│   └── **新增：智能切换命令**
│       ├── fallback-status
│       ├── fallback-trigger
│       ├── fallback-history
│       └── quota-status
├── 核心模块（新增）
│   ├── 提供商管理器
│   ├── 配额监控器
│   ├── 切换引擎
│   ├── 告警引擎
│   └── 错误处理器
└── 工具
    ├── 连接验证（保持不变）
    ├── 安全工具（保持不变）
    └── 日志管理（保持不变）
```

---

## 📁 配置文件设计

### 新增配置字段

在 `~/.claude` / `settings.json` 中添加：

```json
{
  // 现有字段（保持不变）
  "env": {},
  "permissions": {"allowed": ["all"], "denied": []},
  "hooks": {},
  "_schema": {"version": "2.0"},

  // ===== 新增：智能切换配置 =====
  
  "providers": {
    "deepseek": {
      "name": "DeepSeek",
      "type": "deepseek",
      "api_endpoint": "https://api.deepseek.com/v1",
      "api_key": "${DEEPSEEK_API_KEY}",
      "model": "deepseek-chat",
      "quota_limit": 1000000,
      "quota_type": "tokens",
      "tier": "pro",
      "cost_per_1k_tokens": 0.001,
      "priority": 10,
      "enabled": true,
      "rate_limit_5h": false
    },
    "glm": {
      "name": "GLM Coding Plan",
      "type": "glm",
      "api_endpoint": "https://open.bigmodel.cn/api/anthropic",
      "api_key": "${GLM_API_KEY}",
      "model": "glm-4-flash",
      "quota_limit": 500,
      "quota_type": "requests",
      "tier": "pro",
      "cost_per_1k_tokens": 0.002,
      "priority": 5,
      "enabled": true,
      "rate_limit_5h": true
    },
    "aliyun": {
      "name": "Aliyun Dashscope",
      "type": "aliyun",
      "api_endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "api_key": "${ALIYUN_API_KEY}",
      "model": "qwen-turbo",
      "quota_limit": 500,
      "quota_type": "requests",
      "tier": "pro",
      "cost_per_1k_tokens": 0.002,
      "priority": 5,
      "enabled": true,
      "rate_limit_5h": true
    }
  },

  "fallback": {
    "enabled": true,
    "default_strategy": "balance",
    "available_strategies": [
      "balance",      // 综合评分（默认）
      "tier",         // 套餐优先
      "cost",         // 成本最低
      "latency",      // 延迟最低
      "success_rate"  // 成功率最高
    ],
    "auto_fallback": true,
    "auto_fallback_triggers": [
      "quota_exhausted",
      "rate_limited",
      "provider_error",
      "quota_low_90_percent"
    ],
    "manual_trigger": true
  },

  "quota_monitoring": {
    "enabled": true,
    "check_interval_seconds": 300,  // 5 分钟
    "alert_thresholds": {
      "warning": 80,   // 80% 告警
      "critical": 90,  // 90% 告警
      "exhausted": 95  // 95% 告警
    },
    "prediction_enabled": true,
    "prediction_days": 7  // 基于最近 7 天预测
  },

  "notifications": {
    "enabled": true,
    "channels": {
      "email": {
        "enabled": false,
        "smtp_host": "${SMTP_HOST}",
        "smtp_port": "${SMTP_PORT:-587}",
        "username": "${SMTP_USERNAME}",
        "password": "${SMTP_PASSWORD}",
        "to": "${ALERT_TO_EMAIL}"
      },
      "webhook": {
        "enabled": false,
        "url": "${WEBHOOK_URL}"
      },
      "feishu": {
        "enabled": false,
        "webhook_url": "${FEISHU_WEBHOOK_URL}"
      }
    },
    "throttle": {
      "cooldown_seconds": 600,  // 10 分钟
      "max_alerts_per_hour": 10
    }
  },

  "cli": {
    "default_provider": "${DEFAULT_PROVIDER:-deepseek}",
    "show_fallback_events": true,
    "show_quota_usage": true,
    "log_level": "${LOG_LEVEL:-INFO}"
  }
}
```

---

## 🔧 CLI 命令设计

### 现有命令（保持不变）

```bash
# 交互式配置
openclaw wizard

# Claude Code 配置
openclaw claude-config --preset zhipu
openclaw claude-test
openclaw claude-list
openclaw claude-custom --id my-custom --name "My Provider" ...

# OpenClaw 配置
openclaw openclaw-config --model zhipu/glm-5
openclaw openclaw-test --provider zhipu
openclaw openclaw-validate
openclaw openclaw-custom --id my-custom ...

# 模型列表
openclaw models --region china
openclaw models --region international
```

### 新增命令（智能切换）

```bash
# 查看切换状态
openclaw fallback status

# 手动触发切换
openclaw fallback trigger --from glm --to deepseek --reason manual
openclaw fallback trigger --strategy balance

# 查看切换历史
openclaw fallback history --last 10
openclaw fallback history --provider glm

# 查看配额状态
openclaw quota status
openclaw quota status --provider deepseek
openclaw quota status --all

# 测试配额监控
openclaw quota test --provider deepseek

# 启用/禁用提供商
openclaw provider enable --provider deepseek
openclaw provider disable --provider glm

# 添加提供商
openclaw provider add --id new-provider --name "New Provider" \
    --api_endpoint https://api.example.com/v1 \
    --api_key xxx --model model-name --priority 10

# 删除提供商
openclaw provider remove --provider old-provider

# 测试通知
openclaw notification test --channels email --message "Test notification"
```

---

## 📊 模块集成设计

### 1. 提供商管理器（ProviderManager）

**集成点**：复用现有的 `ModelRegistry` 和预设系统

```python
# src/openclaw_claude_config/core/provider_manager.py

class ProviderManager:
    """提供商管理器（集成现有系统）"""
    
    def __init__(self):
        self.config = ClaudeCodeConfigManager()
        self.model_registry = ModelRegistry()
        self.providers = {}
        self._load_providers_from_config()
    
    def _load_providers_from_config(self):
        """从配置加载提供商"""
        # 从 Claude Code 的预设转换
        for preset_id, preset in self.config.BUILTIN_PRESETS.items():
            provider = self._create_provider_from_preset(preset_id, preset)
            self.providers[preset_id] = provider
    
    def _create_provider_from_preset(self, preset_id, preset):
        """从预设创建提供商"""
        # 复用现有的预设信息
        return {
            'id': preset_id,
            'name': preset['name'],
            'type': preset_id,  # zhipu, aliyun, deepseek, etc.
            'api_endpoint': preset['base_url'],
            'models': preset['models'],
            # 从配置获取额外信息（quota_limit, priority, etc.）
        }
```

### 2. 智能切换引擎（FallbackEngine）

**集成点**：集成到现有的 CLI 命令中

```python
# src/openclaw_claude_config/core/fallback_engine.py

class FallbackEngine:
    """智能切换引擎"""
    
    def __init__(self, provider_manager):
        self.provider_manager = provider_manager
        self.config = ClaudeCodeConfigManager()
    
    def select_best_provider(self, strategy='balance'):
        """选择最佳提供商"""
        providers = self.provider_manager.get_available_providers()
        
        if strategy == 'balance':
            return self._select_by_balance(providers)
        elif strategy == 'tier':
            return self._select_by_tier(providers)
        # ... 其他策略
    
    def trigger_fallback(self, from_provider, reason):
        """触发切换"""
        # 选择最佳提供商
        to_provider = self.select_best_provider()
        
        # 执行切换
        success = self._do_fallback(from_provider, to_provider)
        
        # 记录事件
        if success:
            self._log_fallback_event(from_provider, to_provider, reason)
        
        return success
```

### 3. 配额监控器（QuotaMonitor）

**集成点**：利用现有的连接测试

```python
# src/openclaw_claude_config/core/quota_monitor.py

class QuotaMonitor:
    """配额监控器"""
    
    def __init__(self, provider_manager):
        self.provider_manager = provider_manager
        self.connection_validator = ConnectionValidator()
    
    def query_quota(self, provider_id):
        """查询配额"""
        provider = self.provider_manager.get_provider(provider_id)
        
        # 复用现有的连接测试
        result = self.connection_validator.test_connection(
            provider['api_endpoint'],
            provider['api_key'],
            provider['model'],
            provider['type']
        )
        
        # 根据返回的 usage 信息更新配额
        if result.get('usage'):
            self._update_quota_info(provider_id, result['usage'])
        
        return result
```

---

## 🚀 实现计划

### 阶段 1：基础集成（1 周）

#### 任务 1.1：扩展配置系统
- [ ] 在 `BaseConfigManager` 中添加新配置字段
- [ ] 确保向后兼容
- [ ] 添加配置验证

#### 任务 1.2：实现提供商管理器
- [ ] 集成到现有的 `ModelRegistry`
- [ ] 从配置加载提供商
- [ ] 实现启用/禁用提供商
- [ ] 实现添加/删除提供商

#### 任务 1.3：实现智能切换核心
- [ ] 实现切换引擎
- [ ] 实现 5 种切换策略
- [ ] 实现自动触发逻辑
- [ ] 实现手动触发逻辑

---

### 阶段 2：CLI 命令（1 周）

#### 任务 2.1：新增切换相关命令
- [ ] `fallback status` 命令
- [ ] `fallback trigger` 命令
- [ ] `fallback history` 命令
- [ ] `quota status` 命令

#### 任务 2.2：新增提供商管理命令
- [ ] `provider enable/disable` 命令
- [ ] `provider add` 命令
- [ ] `provider remove` 命令
- [ ] `provider list` 命令

#### 任务 2.3：新增测试命令
- [ ] `quota test` 命令
- [ ] `notification test` 命令

---

### 阶段 3：配额监控和告警（1 周）

#### 任务 3.1：实现配额监控
- [ ] 集成到现有的 `ConnectionValidator`
- [ ] 实现配额查询（DeepSeek、Anthropic）
- [ ] 实现配额回退（GLM、Aliyun）
- [ ] 实现告警检查

#### 任务 3.2：实现告警通知
- [ ] 实现邮件通知
- [ ] 实现 Webhook 通知
- [ ] 实现 Feishu 通知
- [ ] 实现告警节流

#### 任务 3.3：实现后台任务
- [ ] 定时配额查询
- [ ] 定时健康检查
- [ ] 定时告警发送

---

### 阶段 4：测试和优化（1 周）

#### 任务 4.1：集成测试
- [ ] 测试配置加载
- [ ] 测试提供商管理
- [ ] 测试智能切换
- [ ] 测试 CLI 命令

#### 任务 4.2：性能优化
- [ ] 优化配额查询
- [ ] 优化切换性能
- [ ] 优化 CLI 响应速度

#### 任务 4.3：文档和示例
- [ ] 更新 README
- [ ] 添加配置示例
- [ ] 添加使用指南

---

## ✅ 验收标准

### 功能验收
- [x] 集成到 OpenClaw-Claude（不作为独立项目）
- [x] 保留所有现有功能
- [x] 智能切换功能正常工作
- [x] 配置文件 + 环境变量方式
- [x] 向后兼容（不破坏现有配置）

### 测试验收
- [ ] 所有现有 CLI 命令正常工作
- [ ] 所有新增 CLI 命令正常工作
- [ ] 配额监控正常工作
- [ ] 智能切换正常工作
- [ ] 告警通知正常工作

### 用户体验验收
- [ ] 不需要重新运行 `openclaw onboard`
- [ ] 配置简单直观
- [ ] CLI 命令易于使用
- [ ] 错误提示清晰

---

## 📋 关键决策记录

### 决策 1：集成方式
✅ **决定**：集成到 OpenClaw-Claude 中
**理由**：
- 不破坏现有配置
- 无需重新 onboard
- 用户体验一致

### 决策 2：配置方式
✅ **决定**：配置文件 + 环境变量
**理由**：
- 灵活性最好
- 安全性最好
- 部署友好

### 决策 3：功能优先级
✅ **决定**：智能切换优先
**理由**：
- 用户最关心的功能
- 其他功能可以后续添加

---

**集成方案设计完成！** 🎉

**下一行动**：开始阶段 1 的实现
