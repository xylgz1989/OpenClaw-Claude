# LLM 配额切换功能 - Phase 2 开发计划

## 📋 Phase 2 开发概述

**开发周期**：1 周  
**开始日期**：2026-02-22  
**状态**：📋 规划中  
**前置条件**：Phase 1 完成

---

## 🎯 Phase 2 目标

### 主要目标
1. 实现告警引擎（AlertEngine）
2. 实现多渠道通知（邮件、Webhook、Feishu）
3. 实现告警模板管理
4. 实现告警节流控制

---

## 📁 任务分解

### Week 2: 告警引擎（5 个任务）

#### 任务 2.1：AlertEngine 核心
- [ ] 实现 AlertEngine 类
- [ ] 实现告警队列管理
- [ ] 实现告警优先级管理
- [ ] 实现告警状态追踪

**交付物：**
- `app/core/alert_engine.py`
- `tests/unit/test_alert_engine.py`

#### 任务 2.2：邮件通知
- [ ] 实现 EmailNotifier 类
- [ ] 实现 SMTP 连接配置
- [ ] 实现邮件模板渲染
- [ ] 实现附件支持
- [ ] 实现重试机制

**交付物：**
- `app/notifications/email/notifier.py`
- `app/notifications/email/templates/`
  - `warning.html`
  - `critical.html`
  - `quota_exhausted.html`
  - `provider_switched.html`
- `tests/unit/test_email_notifier.py`

#### 任务 2.3：Webhook 通知
- [ ] 实现 WebhookNotifier 类
- [ ] 实现 Webhook 签名
- [ ] 实现重试机制
- [ ] 实现超时控制

**交付物：**
- `app/notifications/webhook/notifier.py`
- `tests/unit/test_webhook_notifier.py`

#### 任务 2.4：Feishu 通知
- [ ] 实现 FeishuNotifier 类
- [ ] 实现 Feishu Bot API 集成
- [ ] 实现富文本消息
- [ ] 实现消息卡片
- [ ] 实现按钮交互

**交付物：**
- `app/notifications/feishu/notifier.py`
- `tests/unit/test_feishu_notifier.py`

#### 任务 2.5：告警节流控制
- [ ] 实现节流器类
- [ ] 实现时间窗口管理
- [ ] 实现频率限制
- [ ] 实现优先级队列
- [ ] 实现冷却机制

**交付物：**
- `app/core/alert_throttler.py`
- `tests/unit/test_alert_throttler.py`

---

### Week 2: 用户体验（4 个任务）

#### 任务 2.6：可视化界面
- [ ] 创建 Web Dashboard 框架
- [ ] 实现配额使用进度条
- [ ] 实现提供商状态卡片
- [ ] 实现使用趋势图
- [ ] 实现告警历史列表
- [ ] 实现系统状态概览

**交付物：**
- `app/dashboard/` (5 个 Vue 3 组件)
  - `Dashboard.vue`
  - `ProviderCard.vue`
  - `QuotaProgress.vue`
  - `AlertHistory.vue`
  - `SystemStatus.vue`
- `app/dashboard/api/` (5 个 API 端点)

#### 任务 2.7：CLI 命令行工具
- [ ] 实现主命令解析器
- [ ] 实现 `llm-config status` 命令
- [ ] 实现切换命令 `llm-config switch`
- [ ] 实现禁用自动切换命令
- [ ] 实现查看历史命令 `llm-config history`
- [ ] 实现配置验证命令 `llm-config validate`

**交付物：**
- `cli/llm-config` (可执行文件)
- `tests/integration/test_cli_tool.py`

#### 任务 2.8：切换历史记录
- [ ] 实现切换事件存储
- [ ] 实现历史查询 API
- [ ] 实现历史统计
- [ ] 实现历史导出

**交付物：**
- `app/core/fallback_history.py`
- `app/api/history/` (2 个 API 端点)
- `tests/unit/test_fallback_history.py`

---

### Week 2: 集成测试（3 个任务）

#### 任务 2.9：告警发送测试
- [ ] 邮件通知发送测试
- [ ] Webhook 通知发送测试
- [ ] Feishu 通知发送测试
- [ ] 节流机制测试
- [ ] 模板渲染测试

**交付物：**
- `tests/integration/test_alert_sending.py`

#### 任务 2.10：端到端测试（5 个测试）
- [ ] 完整的告警和通知流程测试
- [ ] 配额可视化界面测试
- [ ] CLI 命令行工具测试
- [ ] 切换历史查询测试
- [ ] 配置热更新测试

**交付物：**
- `tests/e2e/test_alert_notification.py`
- `tests/e2e/test_visual_dashboard.py`
- `tests/e2e/test_cli_tool.py`
- `tests/e2e/test_fallback_history.py`
- `tests/e2e/test_config_reload.py`

---

## 🏗️ 技术设计

### 告警引擎架构

```
AlertEngine
├── AlertQueue (Redis List)
├── Throttler (节流控制)
├── TemplateManager (模板管理)
└── NotificationRouter (通知路由)
    ├── EmailNotifier
    ├── WebhookNotifier
    └── FeishuNotifier
```

### 数据流

```
QuotaMonitor → (配额不足?)
  → 是 → AlertEngine → (检查节流)
  → 是 → NotificationRouter → (选择渠道) → 发送
  → 记录发送状态
  → 告警节流
```

---

## 📊 交付物清单

### 核心模块（5 个）
1. ✅ `app/core/alert_engine.py`
2. ✅ `app/core/alert_throttler.py`
3. ✅ `app/core/fallback_history.py`

### 通知模块（3 个）
1. ✅ `app/notifications/email/notifier.py`
2. ✅ `app/notifications/webhook/notifier.py`
3. ✅ `app/notifications/feishu/notifier.py`

### 前端组件（5 个）
1. ✅ `app/dashboard/Dashboard.vue`
2. ✅ `app/dashboard/ProviderCard.vue`
3. ✅ `app/dashboard/QuotaProgress.vue`
4. ✅ `app/dashboard/AlertHistory.vue`
5. ✅ `app/dashboard/SystemStatus.vue`

### API 端点（7 个）
1. ✅ 配额状态 API
2. ✅ 告警历史 API
3. ✅ 切换历史 API
4. ✅ 配额可视化 API
5. ✅ 告警配置 API
6. ✅ CLI 命令 API
7. ✅ 系统状态 API

### CLI 工具
1. ✅ `cli/llm-config`
2. ✅ `tests/integration/test_cli_tool.py`

### 测试文件（9 个）
1. ✅ `tests/unit/test_alert_engine.py`
2. ✅ `tests/unit/test_alert_throttler.py`
3. ✅ `tests/unit/test_fallback_history.py`
4. ✅ `tests/unit/test_email_notifier.py`
5. ✅ `tests/unit/test_webhook_notifier.py`
6. ✅ `tests/unit/test_feishu_notifier.py`
7. ✅ `tests/integration/test_alert_sending.py`
8. ✅ `tests/e2e/test_visual_dashboard.py`
9. ✅ `tests/e2e/test_cli_tool.py`

---

## ✅ Phase 2 验收标准

### 功能验收
- [ ] 告警引擎正常工作
- [ ] 支持 3 种通知渠道
- [ ] 告警模板可配置
- [ ] 节流机制正常工作

### 测试验收
- [ ] 单元测试覆盖率 ≥ 85%
- [ ] 集成测试用例数 ≥ 10
- [ ] 端到端测试用例数 ≥ 5

### 用户体验验收
- [ ] Web Dashboard 功能完整
- [ ] CLI 命令行工具易用
- [ ] 可视化界面美观
- [ ] 响应时间 < 1s

---

## 📝 开发环境

### 技术栈
- **前端**：Vue 3 + TypeScript
- **UI 框架**：Element Plus
- **图表库**：ECharts
- **构建工具**：Vite

### 测试工具
- **单元测试**：pytest
- **集成测试**：Playwright
- **E2E 测试框架**：Playwright

---

## 🗂️ 文件结构

```
app/
├── dashboard/          # Vue 3 Dashboard
│   ├── components/
│   │   ├── Dashboard.vue
│   │   ├── ProviderCard.vue
│   │   ├── QuotaProgress.vue
│   │   ├── AlertHistory.vue
│   │   └── SystemStatus.vue
│   ├── api/              # Dashboard API
│   │   ├── status.py
│   │   ├── alerts.py
│   │   ├── providers.py
│   │   └── history.py
│   └── main.ts
├── notifications/         # 通知模块
│   ├── email/
│   │   ├── notifier.py
│   │   └── templates/
│   ├── webhook/
│   │   ├── notifier.py
│   │   └── signatures.py
│   └── feishu/
│       └── notifier.py
├── core/
│   ├── alert_engine.py
│   ├── alert_throttler.py
│   └── fallback_history.py
└── utils/
    └── security.py
cli/
└── llm-config
tests/
├── unit/
└── e2e/
    ├── test_alert_engine.py
    ├── test_alert_throttler.py
    ├── test_fallback_history.py
    ├── test_email_notifier.py
    ├── test_webhook_notifier.py
    ├── test_feishu_notifier.py
    ├── test_cli_tool.py
    └── e2e/
        ├── test_alert_sending.py
        ├── test_visual_dashboard.py
        ├── test_cli_tool.py
        └── test_config_reload.py
```

---

## 🚀 开发时间线

| 周期 | 任务 | 状态 |
|------|------|------|
| **Week 1** | 基础设施 + ProviderManager | ✅ 已完成 |
| **Week 2** | 配额监控器 + 切换引擎 | ✅ 已完成 |
| **Phase 3** | 告警和通知 | 🚀 开始 |

---

## 📊 Phase 2 开发进度

```
Phase 2: [░░░░░░░░░] 0%
  告警引擎: [░░░░░░░░] 0%
  用户体验: [░░░░░░░░] 0%
  集成测试: [░░░░░░░░] 0%
```

---

## 🎯 本周目标

1. 实现告警引擎核心功能
2. 实现邮件、Webhook、Feishu 3 种通知渠道
3. 实现告警模板和节流控制
4. 实现基础的 Web Dashboard

---

**Phase 2 开发计划已准备就绪！** 📋

**等待 Phase 1 完成后开始！**
