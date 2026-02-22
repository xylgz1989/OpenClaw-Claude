# LLM 配额切换功能 - 简要设计文档

## 📋 文档信息

| 项目 | 内容 |
|------|------|
| **文档版本** | v1.0 |
| **创建日期** | 2026-02-22 |
| **状态** | 设计初稿 |
| **目标项目** | OpenClaw-Claude |

---

## 🎯 设计目标

### 核心目标
设计一个高效、可靠的 LLM 提供商配额监控系统，支持自动切换和智能告警。

### 非功能性需求
- **性能**：配额查询 < 500ms，切换决策 < 100ms，总体切换 < 10s
- **可用性**：系统可用性 > 99.9%
- **扩展性**：支持动态添加新提供商
- **安全性**：API 密钥加密存储，访问控制

---

## 🏗️ 系统架构

### 整体架构

```
┌─────────────────────────────────────────────┐
│          Application Layer                 │
│  (OpenClaw-Claude / Claude Code / etc.)     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         LLM Client SDK                      │
│  - Multi-provider support                  │
│  - Automatic fallback                      │
│  - Request routing                         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│      Provider Manager                       │
│  - Provider registry                      │
│  - Health check                           │
│  - Configuration management               │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌─────▼──────────┐
│  Quota Monitor  │  │  Fallback Engine│
│  - Usage track  │  │  - Priority rules│
│  - Prediction   │  │  - Strategy exec │
│  - Alert check  │  │  - History       │
└─────────────────┘  └────────────────┘
        │
        ↓
┌─────────────────┐
│  Alert Engine   │
│  - Threshold    │
│  - Throttle     │
│  - Notification │
└─────────────────┘
```

### 数据流

```
请求 → Provider Manager → Quota Monitor → (配额不足?)
  → 是: Fallback Engine → Alert Engine → 备选提供商 → 响应
  → 否: 原提供商 → 响应
```

---

## 📦 核心组件设计

### 1. ProviderManager（提供商管理器）

#### 职责
- 管理所有提供商配置
- 提供商注册和发现
- 健康检查
- 配额查询接口统一

#### 接口
```python
class ProviderManager:
    def register(provider: Provider) -> None
    def unregister(provider_id: str) -> None
    def get(provider_id: str) -> Optional[Provider]
    def get_all() -> List[Provider]
    def check_health(provider_id: str) -> bool
    def check_all_health() -> Dict[str, bool]
    def get_quota(provider_id: str) -> QuotaInfo
```

#### 数据结构
```python
@dataclass
class Provider:
    id: str
    name: str
    api_key: str  # 加密存储
    base_url: str
    models:
        default: str
        fallback: str
    quota:
        type: str  # subscription | pay_as_you_go | 5hour_limit
        tier: str  # free | standard | pro | enterprise
        total: Optional[int]
        remaining: Optional[int]
        balance: Optional[float]  # pay_as_you_go
        expiry: Optional[datetime]
        detection_method: str  # api_query | error_429
        reset_time: Optional[str]  # for 5hour_limit
    priority: int
    enabled: bool
```

---

### 2. QuotaMonitor（配额监控器）

#### 职责
- 实时监控配额使用
- 配额使用预测
- 告警触发

#### 接口
```python
class QuotaMonitor:
    def get_quota(provider_id: str) -> QuotaInfo
    def get_all_quotas() -> Dict[str, QuotaInfo]
    def predict_exhaustion(provider_id: str, usage_history: List[Tuple[int, datetime]]) -> datetime
    def check_alerts(provider_id: str) -> Optional[Alert]
    def check_all_alerts() -> List[Alert]
    def handle_429_error(provider_id: str) -> None
    def is_available(provider_id: str) -> bool
```

#### 监控策略

**策略 1：API 查询（支持实时查询的提供商）**

适用于：DeepSeek、Anthropic

```python
def query_quota_via_api(provider_id: str) -> QuotaInfo:
    """通过 API 查询配额"""
    provider = provider_manager.get(provider_id)
    
    # 调用配额查询 API
    response = requests.get(
        f"{provider.base_url}/v1/usage",
        headers={"Authorization": f"Bearer {provider.api_key}"}
    )
    
    quota = QuotaInfo(
        provider_id=provider_id,
        total=response.json()["total"],
        remaining=response.json()["remaining"],
        usage_rate=response.json()["remaining"] / response.json()["total"]
    )
    
    return quota
```

**策略 2：错误检测（不支持实时查询的提供商）**

适用于：GLM、阿里云、Kimi、MiniMax

```python
def monitor_quota_via_error_detection(provider_id: str):
    """通过错误检测监控配额"""
    provider = provider_manager.get(provider_id)
    
    if provider.quota.detection_method != "error_429":
        return
    
    # 监听 429 错误
    # 记录最后 429 错误时间
    # 计算距离 429 错误的时间
    # 如果超过 5 小时，标记为可用
```

---

### 3. FallbackEngine（切换引擎）

#### 职责
- 执行切换策略
- 选择最佳备选
- 管理切换历史

#### 接口
```python
class FallbackEngine:
    def should_fallback(quota: QuotaInfo) -> bool
    def should_fallback_on_error(error: HTTPError) -> bool
    def select_best_provider(providers: List[Provider]) -> Optional[Provider]
    def select_with_strategy(providers: List[Provider], current_provider: str, strategy: str) -> Optional[Provider]
    def fallback(from_provider: str, to_provider: str, reason: str) -> FallbackResult
    def get_fallback_history() -> List[FallbackEvent]
```

#### 切换优先级规则

```python
def calculate_priority(provider: Provider) -> float:
    """计算提供商优先级分数"""
    score = 0
    
    # 规则 1：配额充足（权重：30）
    if provider.quota.remaining > 100000:
        score += 30
    elif provider.quota.remaining > 50000:
        score += 20
    elif provider.quota.remaining > 20000:
        score += 10
    
    # 规则 2：套餐等级（权重：25）
    tier_scores = {"enterprise": 25, "pro": 20, "standard": 15, "free": 10}
    score += tier_scores.get(provider.quota.tier, 0)
    
    # 规则 3：成本（权重：20）
    # 成本越低，分数越高
    if hasattr(provider, 'input_price'):
        cost_score = max(0, 20 - provider.input_price * 1000)
        score += cost_score
    
    # 规则 4：响应时间（权重：15）
    # 延迟越低，分数越高
    if hasattr(provider, 'latency'):
        latency_score = max(0, 15 - provider.latency / 100)
        score += latency_score
    
    # 规则 5：成功率（权重：10）
    # 成功率越高，分数越高
    if hasattr(provider, 'success_rate'):
        success_score = provider.success_rate * 10
        score += success_score
    
    return score
```

#### 切换策略实现

**策略 1：降级策略**
```python
def strategy_degrade(providers: List[Provider], current: Provider) -> Optional[Provider]:
    """降级策略：从高性能切换到低性能"""
    current_tier_score = {
        "enterprise": 4,
        "pro": 3,
        "standard": 2,
        "free": 1
    }.get(current.quota.tier, 0)
    
    # 选择下一级别的提供商
    for provider in providers:
        provider_tier_score = {
            "enterprise": 4,
            "pro": 3,
            "standard": 2,
            "free": 1
        }.get(provider.quota.tier, 0)
        
        if provider_tier_score < current_tier_score and provider.quota.remaining > 0:
            return provider
    
    return None
```

**策略 2：成本优化策略**
```python
def strategy_cost_optimize(providers: List[Provider]) -> Optional[Provider]:
    """成本优化策略：选择价格最低的"""
    valid_providers = [p for p in providers if p.quota.remaining > 0]
    
    if not valid_providers:
        return None
    
    # 按 input_price 排序
    return min(valid_providers, key=lambda p: p.input_price)
```

**策略 3：性能优先策略**
```python
def strategy_performance_first(providers: List[Provider]) -> Optional[Provider]:
    """性能优先策略：选择延迟最低的"""
    valid_providers = [p for p in providers if p.quota.remaining > 0]
    
    if not valid_providers:
        return None
    
    # 按 latency 排序
    return min(valid_providers, key=lambda p: p.latency)
```

**策略 4：负载均衡策略**
```python
def strategy_load_balance(providers: List[Provider]) -> Optional[Provider]:
    """负载均衡策略：选择请求最少的"""
    valid_providers = [p for p in providers if p.quota.remaining > 0]
    
    if not valid_providers:
        return None
    
    # 按 requests 排序
    return min(valid_providers, key=lambda p: getattr(p, 'requests', 0))
```

---

### 4. AlertEngine（告警引擎）

#### 职责
- 管理告警规则
- 发送通知
- 节流控制

#### 接口
```python
class AlertEngine:
    def check_thresholds(provider_id: str, usage_rate: float) -> List[Alert]
    def can_send_alert(provider_id: str) -> bool
    def send_alert(alert: Alert, channels: List[str]) -> bool
    def get_alert_history() -> List[Alert]
```

#### 告警规则

```python
@dataclass
class AlertRule:
    threshold: float  # 0.8, 0.9, 0.95
    severity: str  # warning, critical
    channels: List[str]  # email, webhook, feishu
    cooldown: int  # seconds
```

#### 节流机制

```python
class AlertThrottler:
    def __init__(self, max_per_hour: int = 5, cooldown: int = 300):
        self.max_per_hour = max_per_hour
        self.cooldown = cooldown
        self.last_sent = {}  # provider_id -> datetime
    
    def can_send(self, provider_id: str) -> bool:
        """检查是否可以发送告警"""
        now = datetime.now()
        last = self.last_sent.get(provider_id, datetime.min)
        
        # 冷却期内不能发送
        if (now - last).total_seconds() < self.cooldown:
            return False
        
        # 检查 1 小时内发送次数
        hour_ago = now - timedelta(hours=1)
        recent_count = len([
            t for t in self.last_sent.values()
            if t > hour_ago
        ])
        
        if recent_count >= self.max_per_hour:
            return False
        
        return True
    
    def record_sent(self, provider_id: str):
        """记录发送时间"""
        self.last_sent[provider_id] = datetime.now()
```

---

## 🗄️ 数据存储设计

### 数据库表

#### providers（提供商表）
```sql
CREATE TABLE providers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    base_url VARCHAR(255) NOT NULL,
    tier VARCHAR(20),
    total_quota BIGINT,
    remaining_quota BIGINT,
    balance DECIMAL(10, 2),
    expiry DATETIME,
    priority INT,
    enabled BOOLEAN DEFAULT TRUE,
    last_health_check DATETIME,
    health_status VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### quota_usage（配额使用记录表）
```sql
CREATE TABLE quota_usage (
    id SERIAL PRIMARY KEY,
    provider_id VARCHAR(50) NOT NULL,
    tokens_used BIGINT NOT NULL,
    cost DECIMAL(10, 4),
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers(id)
);
```

#### fallback_events（切换事件表）
```sql
CREATE TABLE fallback_events (
    id SERIAL PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    from_provider VARCHAR(50) NOT NULL,
    to_provider VARCHAR(50) NOT NULL,
    reason VARCHAR(100),
    success BOOLEAN,
    error TEXT,
    FOREIGN KEY (from_provider) REFERENCES providers(id),
    FOREIGN KEY (to_provider) REFERENCES providers(id)
);
```

#### alerts（告警表）
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    provider_id VARCHAR(50) NOT NULL,
    type VARCHAR(20) NOT NULL,
    threshold FLOAT,
    message TEXT,
    status VARCHAR(20),
    sent_at DATETIME,
    FOREIGN KEY (provider_id) REFERENCES providers(id)
);
```

---

## 🔐 安全设计

### API 密钥保护

1. **加密存储**
   - 使用 AES-256 加密存储 API 密钥
   - 密钥存储在环境变量或密钥管理系统

2. **访问控制**
   - 基于角色的权限控制（RBAC）
   - 操作审计日志

3. **日志脱敏**
   - 日志中不记录明文 API 密钥
   - 使用 mask_sensitive_data 工具

### 敏感信息处理

```python
def mask_api_key(api_key: str) -> str:
    """脱敏 API 密钥"""
    if not api_key:
        return "***"
    
    # 只显示前 4 个字符
    return f"{api_key[:4]}...***"
```

---

## 📊 性能优化

### 1. 缓存策略

```python
class QuotaCache:
    """配额信息缓存"""
    def __init__(self, ttl: int = 300):  # 5 分钟
        self.cache = {}
        self.ttl = ttl
    
    def get(self, provider_id: str) -> Optional[QuotaInfo]:
        item = self.cache.get(provider_id)
        if item and (datetime.now() - item['timestamp']).total_seconds() < self.ttl:
            return item['data']
        return None
    
    def set(self, provider_id: str, quota: QuotaInfo):
        self.cache[provider_id] = {
            'data': quota,
            'timestamp': datetime.now()
        }
```

### 2. 异步处理

```python
import asyncio
from aiohttp import ClientSession

async def async_quota_query(provider_id: str) -> QuotaInfo:
    """异步查询配额"""
    provider = provider_manager.get(provider_id)
    
    async with ClientSession() as session:
        async with session.get(
            f"{provider.base_url}/v1/usage",
            headers={"Authorization": f"Bearer {provider.api_key}"}
        ) as response:
            data = await response.json()
            return QuotaInfo(**data)
```

### 3. 批量操作

```python
def batch_health_check(provider_ids: List[str]) -> Dict[str, bool]:
    """批量健康检查"""
    results = {}
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            provider_id: executor.submit(check_health, provider_id)
            for provider_id in provider_ids
        }
        
        for provider_id, future in futures.items():
            try:
                results[provider_id] = future.result(timeout=10)
            except Exception:
                results[provider_id] = False
    
    return results
```

---

## 🚀 实现计划

### Phase 1: 基础功能（2 周）

**任务：**
1. 实现基础数据模型
2. 实现数据库迁移
3. 实现提供商管理器
4. 实现配额监控器（API 查询）
5. 实现基本的切换引擎
6. 实现配置管理

**交付物：**
- [ ] 数据模型和数据库迁移
- [ ] ProviderManager
- [ ] QuotaMonitor（API 查询）
- [ ] FallbackEngine（基本切换）
- [ ] ConfigManager

### Phase 2: 告警和通知（1 周）

**任务：**
1. 实现告警引擎
2. 实现邮件通知
3. 实现 Webhook 通知
4. 实现 Feishu 通知
5. 实现节流机制

**交付物：**
- [ ] AlertEngine
- [ ] EmailNotifier
- [ ] WebhookNotifier
- [ ] FeishuNotifier
- [ ] AlertThrottler

### Phase 3: 用户体验（1 周）

**任务：**
1. 实现配额可视化
2. 实现 CLI 命令行工具
3. 实现切换历史查询
4. 实现统计报表

**交付物：**
- [ ] Web Dashboard
- [ ] CLI 命令
- [ ] FallbackHistory
- [ ] Statistics

### Phase 4: 优化和测试（1 周）

**任务：**
1. 实现缓存机制
2. 实现异步处理
3. 实现批量操作
4. 完善单元测试
5. 实现集成测试
6. 实现端到端测试

**交付物：**
- [ ] QuotaCache
- [ ] 异步查询接口
- [ ] 单元测试（49+ 用例）
- [ ] 集成测试（5 用例）
- [ ] 端到端测试（5 用例）

---

## ✅ 技术选型

### 后端框架
- **语言**：Python 3.11+
- **框架**：FastAPI
- **数据库**：PostgreSQL
- **ORM**：SQLAlchemy
- **缓存**：Redis
- **任务队列**：Celery

### 前端框架
- **框架**：Vue 3 + TypeScript
- **UI 库**：Element Plus
- **图表库**：ECharts
- **构建工具**：Vite

### 监控和日志
- **监控**：Prometheus + Grafana
- **日志**：ELK Stack
- **追踪**：Jaeger
- **告警**：AlertManager

### 测试框架
- **单元测试**：pytest + pytest-asyncio
- **集成测试**：pytest + pytest-django
- **端到端测试**：Playwright
- **性能测试**：locust
- **覆盖率**：pytest-cov

---

## 📋 验收标准

### 功能验收
- ✅ 支持至少 3 个 LLM 提供商
- ✅ 配额准确率：> 99%
- ✅ 切换成功率：> 99%
- ✅ 告警发送成功率：> 95%

### 性能验收
- ✅ 配额查询：< 500ms
- ✅ 切换决策：< 100ms
- ✅ 总体切换时间：< 10s
- ✅ 系统可用性：> 99.9%

### 质量验收
- ✅ 单元测试覆盖率：≥ 80%
- ✅ 集成测试用例：≥ 15
- ✅ 端到端测试用例：≥ 5
- ✅ 文档完整性：100%

---

## 📚 参考资料

### 相关文档
- 需求文档：`llm-quota-fallback-requirements.md`
- 测试用例：`llm-quota-fallback-test-cases.md`
- API 文档：各提供商官方 API 文档

### 技术文档
- FastAPI 文档：https://fastapi.tiangolo.com/
- SQLAlchemy 文档：https://docs.sqlalchemy.org/
- Celery 文档：https://docs.celeryproject.org/

---

**设计文档完成！**

**下一步：**
1. 评审设计文档
2. 确认技术方案
3. 开始 Phase 1 开发
