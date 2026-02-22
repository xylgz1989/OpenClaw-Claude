# LLM 配额切换功能 - Phase 1 开发计划

## 📋 Phase 1 开发概述

**开发周期**：2 周  
**开始日期**：2026-02-22  
**状态**：🚀 开发中

---

## 🎯 Phase 1 目标

### 主要目标
1. 实现基础数据模型和数据库迁移
2. 实现提供商管理器（ProviderManager）
3. 实现配额监控器（QuotaMonitor）
   - 支持实时配额查询（DeepSeek、Anthropic）
   - 支持 5 小时限额错误检测（GLM、阿里云、Kimi、MiniMax）
4. 实现基本切换引擎（FallbackEngine）
5. 实现配置管理器（ConfigManager）

---

## 🗓️ 任务分解

### Week 1: 基础设施

#### 任务 1.1：项目初始化
- [ ] 创建 FastAPI 项目结构
- [ ] 配置 PostgreSQL 数据库
- [ ] 配置 Redis 缓存
- [ ] 配置 Celery 任务队列
- [ ] 设置项目依赖
- [ ] 配置开发环境

**交付物：**
- FastAPI 项目骨架
- 数据库连接配置
- 基础中间件配置

#### 任务 1.2：数据模型设计
- [ ] 定义 Provider 数据模型
- [ ] 定义 QuotaInfo 数据模型
- [ ] 定义 Alert 数据模型
- [ ] 定义 FallbackEvent 数据模型
- [ ] 创建 SQLAlchemy 模型文件
- [ ] 编写数据库迁移脚本

**交付物：**
- `app/models/provider.py`
- `app/models/quota.py`
- `app/models/alert.py`
- `app/models/fallback.py`
- `alembic/versions/001_initial_schema.py`

#### 任务 1.3：数据库迁移
- [ ] 执行 Alembic 迁移
- [ ] 验证表结构
- [ ] 创建测试数据
- [ ] 编写种子数据脚本

**交付物：**
- 数据库表创建成功
- 测试数据加载完成

---

### Week 1: ProviderManager 实现

#### 任务 1.4：ProviderManager 核心
- [ ] 实现 Provider 类（dataclass）
- [ ] 实现 ProviderRegistry 类
- [ ] 实现 ProviderManager 类
- [ ] 实现注册/注销逻辑
- [ ] 实现查询方法

**交付物：**
- `app/core/provider_manager.py`
- `tests/unit/test_provider_manager.py`

#### 任务 1.5：健康检查
- [ ] 实现健康检查接口
- [ ] 实现批量健康检查
- [ ] 实现健康状态缓存
- [ ] 实现健康历史记录

**交付物：**
- 健康检查 API 端点
- 健康状态表

#### 任务 1.6：配置加载
- [ ] 实现配置文件加载
- [ ] 实现环境变量加载
- [ ] 实现配置验证
- [ ] 实现配置热更新
- [ ] 编写配置示例文件

**交付物：**
- `app/core/config_manager.py`
- `config/providers.example.yaml`
- `tests/unit/test_config_manager.py`

---

### Week 2: 配额监控器实现

#### 任务 2.1：QuotaMonitor 核心
- [ ] 实现 QuotaMonitor 类
- [ ] 实现配额查询接口
- [ ] 实现配额缓存机制
- [ ] 实现配额使用率计算

**交付物：**
- `app/core/quota_monitor.py`
- `tests/unit/test_quota_monitor.py`

#### 任务 2.2：实时配额查询（DeepSeek、Anthropic）
- [ ] 实现 DeepSeek API 调用
- [ ] 实现 Anthropic API 调用
- [ ] 实现响应解析
- [ ] 实现错误处理
- [ ] 实现重试机制

**交付物：**
- `app/api/deepseek/client.py`
- `app/api/anthropic/client.py`

#### 任务 2.3：错误检测（5 小时限额）
- [ ] 实现 429 错误监听
- [ ] 实现 GLM 5 小时限额处理
- [ ] 实现阿里云 5 小时限额处理
- [ ] 实现冷却时间管理
- [ ] 实现自动恢复

**交付物：**
- `app/core/error_handler.py`
- `tests/unit/test_error_handler.py`

#### 任务 2.4：配额预测
- [ ] 实现使用历史收集
- [ ] 实现使用率计算
- [ ] 实现线性回归预测
- [ ] 实现预测结果缓存

**交付物：**
- `app/core/predictor.py`
- `tests/unit/test_predictor.py`

#### 任务 2.5：告警检查
- [ ] 实现告警阈值检查
- [ ] 实现告警优先级
- [ ] 实现告警去重
- [ ] 实现告警历史记录

**交付物：**
- `app/core/alert_checker.py`
- `tests/unit/test_alert_checker.py`

---

### Week 2: 切换引擎实现

#### 任务 2.6：FallbackEngine 核心
- [ ] 实现 FallbackEngine 类
- [ ] 实现切换优先级规则
- [ ] 实现备选提供商筛选
- [ ] 实现切换历史记录

**交付物：**
- `app/core/fallback_engine.py`
- `tests/unit/test_fallback_engine.py`

#### 任务 2.7：优先级计算
- [ ] 实现优先级权重配置
- [ ] 实现配额充足规则（权重 30）
- [ ] 实现套餐等级规则（权重 25）
- [ ] 实现成本最低规则（权重 20）
- [ ] 实现响应时间规则（权重 15）
- [ ] 实现成功率最高规则（权重 10）

**交付物：**
- `app/core/priority_calculator.py`
- `tests/unit/test_priority_calculator.py`

#### 任务 2.8：切换策略实现
- [ ] 实现降级策略
- [ ] 实现成本优化策略
- [ ] 实现性能优先策略
- [ ] 实现负载均衡策略
- [ ] 实现策略选择器

**交付物：**
- `app/core/strategies/degrade.py`
- `app/core/strategies/cost_optimize.py`
- `app/core/strategies/performance_first.py`
- `app/core/strategies/load_balance.py`
- `tests/unit/test_strategies/`

#### 任务 2.9：切换触发条件
- [ ] 实现配额阈值触发
- [ ] 实现 429 错误触发
- [ ] 实现配额过期触发
- [ ] 实现手动触发

**交付物：**
- `app/core/fallback_triggers.py`
- `tests/unit/test_fallback_triggers.py`

---

### Week 2: API 集成

#### 任务 2.10：DeepSeek API 集成
- [ ] 实现 /v1/usage 端点
- [ ] 实现 /v1/chat/completions 端点
- [ ] 实现请求签名
- [ ] 实现响应解析
- [ ] 实现错误处理

**交付物：**
- `app/api/deepseek/client.py`
- `tests/integration/test_deepseek_api.py`

#### 任务 2.11：Anthropic API 集成
- [ ] 实现 /v1/messages 端点
- [ ] 实现流式响应处理
- [ ] 提取 usage 信息
- [ ] 实现 token 计数

**交付物：- `app/api/anthropic/client.py`
- `tests/integration/test_anthropic_api.py`

#### 任务 2.12：GLM API 集成（错误检测）
- [ ] 实现请求拦截
- [ ] 实现 429 错误检测
- [ ] 实现错误统计
- [ ] 实现冷却管理

**交付物：**
- `app/api/glm/wrapper.py`
- `tests/integration/test_glm_wrapper.py`

#### 任务 2.13：阿里云 API 集成（错误检测）
- [ ] 实现请求拦截
- [ ] 实现 429 错误检测
- [ ] 实现错误统计
- [ ] 实现冷却管理

**交付物：**
- `app/api/aliyun/wrapper.py`
- `tests/integration/test_aliyun_wrapper.py`

---

### Week 2: 单元测试和集成测试

#### 任务 2.14：单元测试
- [ ] ProviderManager 测试（6 个测试）
- [ ] QuotaMonitor 测试（10 个测试）
- [ ] FallbackEngine 测试（13 个测试）
- [ ] PriorityCalculator 测试（5 个测试）
- [ ] 策略测试（4 个测试）
- [ ] 配置管理测试（5 个测试）

**交付物：**
- `tests/unit/test_provider_manager.py`
- `tests/unit/test_quota_monitor.py`
- `tests/unit/test_fallback_engine.py`
- `tests/unit/test_priority_calculator.py`
- `tests/unit/test_strategies/`
- `tests/unit/test_config_manager.py`

**测试覆盖率目标：** ≥ 80%

#### 任务 2.15：集成测试
- [ ] 完整的配额监控和切换流程测试
- [ ] 5 小时限额配额耗尽测试
- [ ] 多提供商按优先级切换测试
- [ ] 告警发送和接收测试
- [ ] 配置热更新和验证测试

**交付物：**
- `tests/integration/test_full_quota_workflow.py`
- `tests/integration/test_5hour_limit.py`
- `tests/integration/test_multi_provider_fallback.py`
- `tests/integration/test_alert_sending.py`
- `tests/integration/test_config_reload.py`

---

## 🚀 开发环境

### 技术栈
- **语言**：Python 3.11+
- **框架**：FastAPI 0.104+
- **数据库**：PostgreSQL 15+
- **ORM**：SQLAlchemy 2.0+
- **缓存**：Redis 7.0+
- **任务队列**：Celery 5.3+
- **测试**：pytest + pytest-asyncio
- **迁移**：Alembic

### 开发工具
- **IDE**：VS Code / PyCharm
- **版本控制**：Git
- **API 测试**：pytest + httpx
- **性能测试**：locust

---

## 📁 项目结构

```
llm-quota-fallback/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── models/                  # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── provider.py
│   │   ├── quota.py
│   │   ├── alert.py
│   │   └── fallback.py
│   ├── core/                    # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── provider_manager.py
│   │   ├── quota_monitor.py
│   │   ├── fallback_engine.py
│   │   ├── priority_calculator.py
│   │   ├── fallback_triggers.py
│   │   ├── alert_checker.py
│   │   └── error_handler.py
│   │   ├── strategies/
│   │   │   ├── __init__.py
│   │   ├── degrade.py
│   │   ├── cost_optimize.py
│   │   ├── performance_first.py
│   │   └── load_balance.py
│   ├── api/                     # API 集成
│   │   ├── __init__.py
│   │   ├── deepseek/
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── wrappers.py
│   │   ├── anthropic/
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── wrappers.py
│   │   ├── glm/
│   │   │   ├── __init__.py
│   │   │   └── wrappers.py
│   │   └── aliyun/
│   │       ├── __init__.py
│   │       └── wrappers.py
│   ├── config/                  # 配置管理
│   │   ├── __init__.py
│   │   └── config_manager.py
│   ├── notifications/            # 通知模块
│   │   ├── __init__.py
│   │   ├── email/
│   │   │   └── notifier.py
│   │   ├── webhook/
│   │   │   └── notifier.py
│   │   └── feishu/
│   │       └── notifier.py
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── security.py       # 密钥加密/解密
│       └── logger.py
├── alembic/                     # 数据库迁移
│   ├── versions/
│   │   └── 001_initial_schema.py
│   └── env.py
├── config/                       # 配置文件
│   ├── providers.example.yaml
│   └── auto_fallback.yaml
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_provider_manager.py
│   │   ├── test_quota_monitor.py
│   │   ├── test_fallback_engine.py
│   │   ├── test_priority_calculator.py
│   │   ├── test_strategies/
│   │   ├── test_config_manager.py
│   │   └── conftest.py
│   └── integration/
│       ├── test_full_quota_workflow.py
│       ├── test_5hour_limit.py
│       ├── test_multi_provider_fallback.py
│       test_alert_sending.py
│       └── test_config_reload.py
├── scripts/
│   ├── seed_data.py            # 种子数据
│   └── migrate_db.py            # 数据库迁移
└── requirements.txt
```

---

## ✅ Phase 1 验收标准

### 功能验收
- [ ] 数据模型和数据库迁移完成
- [ ] ProviderManager 实现并测试通过
- [ ] QuotaMonitor 实现并测试通过
- [ ] 支持 2 个支持实时查询的提供商（DeepSeek、Anthropic）
- [ ] 支持 2 个不支持实时查询的提供商（GLM、阿里云）
- [ ] FallbackEngine 实现并测试通过
- [ ] ConfigManager 实现并测试通过

### 测试验收
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试用例数 ≥ 15
- [ ] 所有测试通过

### 性能验收
- [ ] 配额查询：< 500ms
- [ ] 切换决策：< 100ms
- [ ] 总体切换时间：< 10s

### 文档验收
- [ ] API 文档完整
- [ ] 开发文档完整
- [ ] 部署文档完整

---

## 🚀 开始开发

**状态**：🚀 Phase 1 开发启动  
**开始时间**：2026-02-22 09:20 GMT+8

---

**Phase 1 开发正式开始！** 🚀
