# LLM 配额切换功能 - Phase 3 开发计划

## 📋 Phase 3 开发概述

**开发周期**：1 周  
**开始日期**：2026-02-22  
**状态**：📋 规划中  
**前置条件**：Phase 2 完成

---

## 🎯 Phase 3 目标

### 主要目标
1. 完善用户界面
2. 实现 CLI 命令行工具
3. 实现高级配置功能
4. 完善错误处理和日志
5. 性能优化

---

## 📁 任务分解

### Week 3: 用户体验（4 个任务）

#### 任务 3.1：可视化界面完善
- [ ] 实现实时数据刷新
- [ ] 实现深色模式
- [ ] 实现响应式设计
- [ ] 实现数据可视化增强

**交付物：**
- `app/dashboard/api/config.py`（实时配置 API）
- `app/dashboard/components/`（增强的组件）

#### 任务 3.2：CLI 命令行工具完善
- [ ] 实现 `llm-config status` 命令
- [ ] 实现 `llm-config switch` 命令
- [ ] 实现 `llm-config history` 命令
- [ ] 实现 `llm-config validate` 命令
- [ ] 实现 `llm-config reset` 命令

**交付物：**
- `cli/llm-config`（可执行文件）
- `tests/integration/test_cli_tool.py`

#### 任务 3.3：高级配置功能
- [ ] 实现配置导入/导出
- [ ] 实现配置版本控制
- [ ] 实现配置备份和恢复
- [ ] 实现配置验证和测试

**交付物：**
- `app/core/config_exporter.py`
- `app/core/config_versioner.py`
- `app/core/config_validator.py`
- `app/api/config/`
- `tests/unit/test_config_exporter.py`

#### 任务 3.4：错误处理和日志
- [ ] 完善全局错误处理器
- [ ] 实现结构化日志记录
- [ ] 实现错误分类和等级
- [ ] 实现错误告警集成

**交付物：**
- `app/core/error_handler.py`（增强版）
- `app/core/logger.py`（增强版）
- `app/core/error_classifier.py`（新增）
- `app/api/logging/`（新增）

---

### Week 3: 集成测试（3 个任务）

#### 任务 3.5：用户流程测试
- [ ] 新用户引导流程
- [ ] 提供商配置流程
- [ ] 告警设置流程
- [ ] 配额监控流程

**交付物：**
- `tests/e2e/test_user_onboarding.py`
- `tests/e2e/test_provider_setup.py`
- `tests/e2e/test_alert_setup.py`
- `tests/e2e/test_quota_monitoring.py`

#### 任务 3.6：性能测试
- [ ] 并发请求测试
- [ ] 大量数据测试
- [ ] 长时间运行测试
- [ ] 内存泄漏测试
- [ ] 响应时间测试

**交付物：**
- `tests/performance/load_test.py`
- `tests/performance/stress_test.py`
- `tests/performance/memory_test.py`

#### 任务 3.7：故障恢复测试
- [ ] 提供商故障切换测试
- [ ] 网络故障恢复测试
- [ ] 数据库故障恢复测试
- [ ] 配置损坏恢复测试
- [ ] 状态一致性测试

**交付物：**
- `tests/resilience/provider_failover.py`
- `tests/resilience/network_recovery.py`
- `tests/resilience/db_recovery.py`
- `tests/resilience/state_consistency.py`

---

## 🗂️ 用户体验设计

### Web Dashboard

#### 页面结构

```
/
├── Dashboard（主页）
│   ├── Provider Cards（提供商卡片）
│   │   ├── DeepSeek
│   │   ├── GLM
│   │   ├── Aliyun
│   │   ├── Anthropic
│   ├── Quota Progress（配额进度条）
│   │   ├── 总配额进度条
│   │   └── 各提供商进度条
│   ├── Usage Trend（使用趋势）
│   │   ├── 折线图（7 天）
│   │   └── 柱状图
│   ├── Alert History（告警历史）
│   │   └── 告警列表（分页）
│   └── System Status（系统状态）
│       ├── 系统健康度
│       ├── API 连接状态
│       ├── 数据库状态
│       └── 任务队列状态
```

#### 组件设计

**1. Dashboard.vue**（主页）
- 功能：主页仪表盘
- 组件：ProviderCards、QuotaProgress、UsageTrend、AlertHistory、SystemStatus
- 刷新：实时数据自动刷新（每 30 秒）

**2. ProviderCard.vue**
- 功能：单个提供商状态卡片
- 显示：提供商名称、配额使用率、套餐等级、健康状态
- 操作：禁用/启用、手动切换

**3. QuotaProgress.vue**
- 功能：配额使用进度条
- 显示：总配额、已用配额、剩余配额
- 动画：平滑过渡动画

**4. AlertHistory.vue**
- 功能：告警历史列表
- 显示：时间、提供商、类型、消息、状态
- 分页：每页 20 条记录

**5. SystemStatus.vue**
- 功能：系统健康状态概览
- 显示：各子系统状态
- 指标：健康度、连接数、任务队列

#### 响应式设计
- 桌设备自适应（移动端优先）
- 支持深色模式
- 支持离线缓存
- 实时 WebSocket 更新

---

### CLI 命令行工具

#### 命令结构

```
llm-config <command> [options]

Commands:
  status      查看当前状态
  switch      手动切换提供商
  history     查看切换历史
  validate    验证配置
  reset       重置为默认配置
  export      导出配置
  import      导入配置
```

#### 命令示例

```bash
# 查看状态
llm-config status

# 手动切换到阿里云
llm-config switch --to aliyun --reason="manual"

# 查看历史
llm-config history --last 10

# 验证配置
llm-config validate

# 导出配置
llm-config export --output config.yaml

# 导入配置
llm-config import --input config.yaml

# 重置配置
llm-config reset
```

#### 命令实现

```python
# cli/llm_config/__main__.py

class LLMConfigCommand:
    def cmd_status(self):
        """查看当前状态"""
    
    def cmd_switch(self, provider: str, reason: str):
        """手动切换提供商"""
    
    def cmd_history(self, count: int = 10):
        """查看切换历史（默认最近 10 条）"""
    
    def cmd_validate(self):
        """验证配置文件"""
    
    def cmd_reset(self):
        """重置为默认配置"""
    
    def cmd_export(self, output: str = None):
        """导出配置到文件"""
    
    def cmd_import(self, input: str):
        """从文件导入配置"""
```

---

## 🔧 高级配置功能

### 配置导入/导出

#### 导出功能
```python
# app/core/config_exporter.py

class ConfigExporter:
    def export_config(config: dict, format: str = "yaml") -> str:
        """导出配置到文件"""
        
    def export_to_file(
        config: dict,
        file_path: str,
        include_secrets: bool = False
    ) -> str:
        """导出配置到指定文件"""
        
    def export_to_string(
        config: dict,
        include_secrets: bool = False
    ) -> str:
        """导出配置为字符串"""
```

#### 导入功能
```python
# app/core/config_importer.py

class ConfigImporter:
    def import_from_file(file_path: str) -> dict:
        """从文件导入配置"""
        
    def import_from_string(content: str) -> dict:
        """从字符串导入配置"""
        
    def validate_imported_config(config: dict) -> List[str]:
        """验证导入的配置"""
        
    def merge_configs(
        current: dict,
        imported: dict,
        strategy: str = "overwrite"  # overwrite | merge | ask
    ) -> dict:
        """合并配置"""
```

### 配置版本控制

```python
# app/core/config_versioner.py

class ConfigVersioner:
    def get_version(self) -> str:
        """获取当前配置版本"""
    
    def increment_version(self) -> str:
        """增加版本号"""
    
    def create_backup(self) -> str:
        """创建当前配置的备份"""
    
    def restore_backup(self, backup_id: str) -> dict:
        """从备份恢复配置"""
    
    def list_backups() -> List[Dict]:
        """列出所有备份"""
    
    def delete_old_backups(keep: int = 10) -> int:
        """删除旧备份（保留最新的 keep 个）"""
```

### 配置验证

```python
# app/core/config_validator.py

class ConfigValidator:
    def validate_structure(config: dict) -> List[str]:
        """验证配置结构"""
    
    def validate_types(config: dict) -> List[str]:
        """验证数据类型"""
    
    def validate_values(config: dict) -> List[str]:
        """验证配置值"""
    
    def validate_dependencies(config: dict) -> List[str]:
        """验证配置依赖关系"""
    
    def is_valid(self) -> bool:
        """验证整个配置"""
```

---

## 🗄️ 错误处理和日志

### 全局错误处理器

```python
# app/core/error_handler.py

class GlobalErrorHandler:
    def __init__(self):
        self.logger = Logger()
        self.classifier = ErrorClassifier()
        self.alert_engine = AlertEngine()
    
    def handle_exception(
        self,
        e: Exception,
        context: dict = None
    ) -> None:
        """全局异常处理"""
        
    def classify_error(self, e: Exception) -> ErrorInfo:
        """分类错误"""
        
    def log_error(self, e: Exception, level: str = "ERROR"):
        """记录错误日志"""
        
    def send_alert_if_critical(self, e: Exception):
        """如果是严重错误，发送告警"""
```

### 错误分类器

```python
# app/core/error_classifier.py

class ErrorClassifier:
    def classify(self, e: Exception) -> ErrorInfo:
        """分类错误类型"""
        
    ERROR_TYPES = {
        "CONFIG_ERROR": {
            "severity": "warning",
            "can_recover": True,
            "requires_alert": False
        },
        "DATABASE_ERROR": {
            "severity": "critical",
            "can_recover": False,
            "requires_alert": True
        },
        "NETWORK_ERROR": {
            "severity": "warning",
            "can_recover": True,
            "requires_alert": False
        },
        "API_ERROR": {
            "severity": "warning",
            "can_recover": true,
            "requires_alert": False
        },
        "PROVIDER_ERROR": {
            "severity": "critical",
            "can_recover": false,
            "requires_alert": true
        },
        "UNKNOWN_ERROR": {
            "severity": "info",
            "can_recover": False,
            "requires_alert": false
        }
    }
```

### 结构化日志

```python
# app/core/logger.py

class StructuredLogger:
    def __init__(self):
        self.handlers = []
        self.min_level = "INFO"
        
    def add_handler(self, handler: Callable):
        """添加日志处理器"""
        
    def log(self, level: str, message: str, context: dict = None):
        """记录日志"""
        
    def log_structured(
        self,
        level: str,
        message: str,
        context: dict = None,
        error: Exception = None
    ):
        """记录结构化日志"""
        
    def set_level(self, level: str):
        """设置日志级别"""
        
    def get_logs(self, level: str = "INFO", limit: int = 100):
        """获取日志"""
```

---

## 🚀 性能优化

### 1. 缓存策略

```python
# app/core/cache_manager.py

class CacheManager:
    def __init__(self):
        self.redis = RedisClient()
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        
    def set(self, key: str, value: Any, ttl: int = 300):
        """设置缓存"""
        
    def delete(self, key: str) -> bool:
        """删除缓存"""
        
    def clear_all(self) -> int:
        """清空所有缓存"""
```

### 2. 异步处理

```python
# app/core/async_manager.py

class AsyncManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    async def async_quota_query(
        self,
        provider_ids: List[str]
    ) -> Dict[str, QuotaInfo]:
        """异步查询多个提供商的配额"""
        
    async def async_batch_health_check(
        self,
        provider_ids: List[str]
    ) -> Dict[str, bool]:
        """批量健康检查"""
        
    async def async_send_alerts(
        self,
        alerts: List[Alert]
    ) -> Dict[str, bool]:
        """异步发送告警"""
```

### 3. 批量操作

```python
# app/core/batch_operator.py

class BatchOperator:
    def __init__(self):
        self.db = Session()
        
    async def batch_insert_quota_usage(
        self,
        usage_records: List[UsageRecord]
    ) -> int:
        """批量插入配额使用记录"""
        
    async def batch_update_quota_status(
        self,
        provider_id: str,
        updates: Dict
    ) -> int:
        """批量更新配额状态"""
        
    async def batch_get_latest_usage(
        self,
        provider_ids: List[str],
        limit: int = 100
    ) -> Dict[str, List[UsageRecord]]:
        """批量获取最新使用记录"""
```

---

## 🧪 集成测试（Week 3）

### 任务 3.5：用户流程测试

**测试场景：**

1. **新用户引导**
   - 用户首次登录
   - 提供商配置向导
   - 告警设置向导
   - 完成基本配置

2. **提供商配置流程**
   - 添加新提供商
   - 配置 API Key
   - 设置配额监控
   - 测试连接

3. **告警设置流程**
   - 配置邮件接收地址
   - 配置 Webhook URL
   - 设置告警阈值（80%、90%、95%）
   - 测试告警发送

4. **配额监控流程**
   - 查看实时配额
   - 查看使用趋势
   - 设置配额告警

**交付物：**
- `tests/e2e/test_user_onboarding.py`
- `tests/e2e/test_provider_setup.py`
- `tests/e2e/test_alert_setup.py`
- `tests/e2e/test_quota_monitoring.py`

### 任务 3.6：性能测试

**测试场景：**

1. **并发请求测试**
   - 10 个并发用户
   - 每用户 100 个请求
   - 总计 1000 个请求

2. **大数据量测试**
   - 10000 条配额使用记录
   - 100000 条切换事件
   - 50000 条告警记录

3. **长时间运行测试**
   - 运行 24 小时
   - 模拟一天的真实使用场景
   - 监控系统稳定性

4. **内存泄漏测试**
   - 监控内存使用情况
   - 检查内存泄漏
   - 优化内存使用

5. **响应时间测试**
   - 单个请求响应时间 < 2s
   - 切换决策时间 < 100ms
- P95 响应时间 < 500ms
- P99 响应时间 < 200ms

**交付物：**
- `tests/performance/load_test.py`
- `tests/performance/stress_test.py`
- `tests/performance/memory_test.py`
- `tests/performance/latency_test.py`

### 任务 3.7：故障恢复测试

**测试场景：**

1. **提供商故障切换**
   - 模拟 DeepSeek 服务故障
   - 验证自动切换到备用提供商
   - 测试切换透明性

2. **网络故障恢复**
   - 模拟网络中断 30 秒
   - 验证系统自动重试
   - 验证连接恢复

3. **数据库故障恢复**
   - 模拟数据库连接断开
   - 验证自动重连
   - 验证数据完整性

4. **状态一致性测试**
   - 模拟配置文件损坏
   - 验证自动恢复
   - 验证状态一致性

**交付物：**
- `tests/resilience/provider_failover.py`
- `tests/resilience/network_recovery.py`
- `tests/resilience/db_recovery.py`
- `tests/resilience/state_consistency.py`

---

## ✅ Phase 3 验收标准

### 功能验收
- [ ] Web Dashboard 功能完整
- [ ] CLI 命令行工具易用
- [ ] 高级配置功能完整
- [ ] 错误处理健壮
- [ ] 日志系统完善

### 测试验收
- [ ] 单元测试覆盖率 ≥ 85%
- [ ] 集成测试用例数 ≥ 20
- [ ] 性能测试全部通过

### 性能验收
- [ ] 配额查询：< 500ms
- [ ] 切换决策：< 100ms
- [ ] 总体切换时间：< 10s
- [ ] 系统可用性：> 99.9%

### 用户体验验收
- [ ] Web Dashboard 界面美观易用
- [ ] CLI 命令清晰明确
- [ ] 配置文档完整
- [ ] 错误提示友好

---

## 📊 Phase 3 开发时间线

```
Week 3: [░░░░░░░░░░░] 0%
         周一├├├├├├├├├├├├  ├─├├├├├├├
         周二├├├├├├├├├  ├─├├├├├├├
         周三├├├├├├├├  ├─├├├├├├├
         周四├├├├├├├├
         周五├├├├├├├├  ├─├├├├├├├├
```

**关键里程碑：**
- ✅ Week 1: 基础设施
- ✅ Week 2: 告警和通知
- ✅ Week 3: 用户体验
```

---

## 🚀 Phase 3 开发准备就绪！

**前置条件：** ✅ Phase 2 完成  
**技术栈：** Python 3.11+, FastAPI, PostgreSQL, Redis, Vue 3, Element Plus  
**开发工具：** VS Code, pytest, Playwright  
**测试框架：** pytest + pytest-asyncio + Playwright

**开发环境：** ✅ 已搭建  
**测试环境：** ✅ 已配置

**可以开始 Phase 3 开发！** 🚀
