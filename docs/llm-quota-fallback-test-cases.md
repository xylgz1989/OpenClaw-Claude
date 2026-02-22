# LLM 配额切换功能 - 测试用例

## 📋 测试范围

**目标功能**：LLM 订阅套餐限额智能切换  
**测试类型**：单元测试、集成测试、端到端测试  
**总测试用例数**：50+

---

## 🧪 单元测试（35+ 用例）

### 1. 配额监控模块

#### 1.1 配额查询测试

**TC-QUOTA-001：配额查询 - DeepSeek**
```python
def test_quota_query_deepseek():
    """测试 DeepSeek 配额查询功能"""
    monitor = QuotaMonitor()
    quota = monitor.get_quota("deepseek")
    
    assert quota.remaining >= 0
    assert quota.total > 0
    assert quota.type in ["subscription", "pay_as_you_go"]
```

**TC-QUOTA-002：配额查询 - Anthropic**
```python
def test_quota_query_anthropic():
    """测试 Anthropic 配额查询功能"""
    monitor = QuotaMonitor()
    quota = monitor.get_quota("anthropic")
    
    assert quota.remaining >= 0
    assert quota.total > 0
    assert quota.tier in ["free", "standard", "pro", "enterprise"]
```

**TC-QUOTA-003：配额查询 - GLM（错误检测）**
```python
def test_quota_query_glm_error_detection():
    """测试 GLM 通过 429 错误检测配额"""
    monitor = QuotaMonitor()
    
    # 模拟 429 错误
    monitor.handle_429_error("glm")
    
    # 验证提供商被标记为不可用
    assert not monitor.is_available("glm")
    
    # 验证冷却时间
    cooldown_end = monitor.get_cooldown_end("glm")
    assert cooldown_end is not None
```

**TC-QUOTA-004：配额查询 - 阿里云（错误检测）**
```python
def test_quota_query_aliyun_error_detection():
    """测试阿里云通过 429 错误检测配额"""
    monitor = QuotaMonitor()
    
    # 模拟 429 错误
    monitor.handle_429_error("aliyun")
    
    # 验证提供商被禁用 5 小时
    assert not monitor.is_available("aliyun")
    
    # 验证 5 小时后恢复
    monitor.advance_time(hours=5)
    assert monitor.is_available("aliyun")
```

#### 1.2 配额预测测试

**TC-QUOTA-005：配额耗尽时间预测**
```python
def test_quota_exhaustion_prediction():
    """测试配额耗尽时间预测"""
    monitor = QuotaMonitor()
    
    # 设置历史使用数据
    usage_history = [
        (1000, "2026-02-22 08:00:00"),
        (1500, "2026-02-22 09:00:00"),
        (2000, "2026-02-22 10:00:00"),
    ]
    
    # 预测
    exhaustion_time = monitor.predict_exhaustion("deepseek", usage_history)
    
    # 验证预测时间在未来
    assert exhaustion_time > datetime.now()
```

**TC-QUOTA-006：配额使用率计算**
```python
def test_quota_usage_rate_calculation():
    """测试配额使用率计算"""
    monitor = QuotaMonitor()
    
    # 设置配额
    monitor.set_quota("deepseek", total=100000, remaining=85000)
    
    # 计算使用率
    usage_rate = monitor.get_usage_rate("deepseek")
    
    assert usage_rate == 0.85  # 85%
```

#### 1.3 告警触发测试

**TC-QUOTA-007：告警阈值 - 80%**
```python
def test_alert_threshold_80():
    """测试 80% 告警阈值"""
    alert_engine = AlertEngine()
    
    # 设置配置
    alert_engine.config.warning_thresholds = [0.8, 0.9, 0.95]
    
    # 触发告警
    alerts = alert_engine.check_thresholds("deepseek", 0.8)
    
    assert len(alerts) == 1
    assert alerts[0].type == "warning"
    assert alerts[0].threshold == 0.8
```

**TC-QUOTA-008：告警阈值 - 90%**
```python
def test_alert_threshold_90():
    """测试 90% 告警阈值"""
    alert_engine = AlertEngine()
    
    # 设置配置
    alert_engine.config.warning_thresholds = [0.8, 0.9, 0.95]
    
    # 触发告警
    alerts = alert_engine.check_thresholds("deepseek", 0.9)
    
    assert len(alerts) == 2  # 80% 和 90%
    assert alerts[1].type == "critical"
```

**TC-QUOTA-009：告警阈值 - 95%**
```python
def test_alert_threshold_95():
    """测试 95% 告警阈值"""
    alert_engine = AlertEngine()
    
    # 设置配置
    alert_engine.config.warning_thresholds = [0.8, 0.9, 0.95]
    
    # 触发告警
    alerts = alert_engine.check_thresholds("deepseek", 0.95)
    
    assert len(alerts) == 3  # 80%, 90%, 95%
    assert alerts[2].type == "critical"
```

**TC-QUOTA-010：告警节流**
```python
def test_alert_throttling():
    """测试告警节流"""
    alert_engine = AlertEngine()
    
    # 配置：每 5 分钟最多 1 次
    alert_engine.config.throttle = {
        "max_per_hour": 12,
        "cooldown": 300  # seconds
    }
    
    # 第一次发送
    assert alert_engine.can_send_alert("deepseek")
    alert_engine.send_alert("deepseek", "Test alert")
    
    # 冷却期内不应发送
    assert not alert_engine.can_send_alert("deepseek")
    
    # 冷却期后可以发送
    alert_engine.advance_time(seconds=301)
    assert alert_engine.can_send_alert("deepseek")
```

### 2. 切换引擎模块

#### 2.1 切换优先级测试

**TC-FALLBACK-001：优先级 - 配额充足**
```python
def test_fallback_priority_balance():
    """测试优先级规则：配额充足"""
    fallback_engine = FallbackEngine()
    
    providers = [
        {"id": "deepseek", "remaining": 50000, "tier": "standard"},
        {"id": "anthropic", "remaining": 100000, "tier": "pro"},
        {"id": "glm", "remaining": 150000, "tier": "free"},
    ]
    
    # 选择最佳备选
    best = fallback_engine.select_best_provider(providers)
    
    # GLM 配额最多，应优先选择
    assert best["id"] == "glm"
```

**TC-FALLBACK-002：优先级 - 套餐等级**
```python
def test_fallback_priority_tier():
    """测试优先级规则：套餐等级"""
    fallback_engine = FallbackEngine()
    
    providers = [
        {"id": "deepseek", "remaining": 50000, "tier": "free"},
        {"id": "anthropic", "remaining": 50000, "tier": "standard"},
        {"id": "glm", "remaining": 50000, "tier": "pro"},
    ]
    
    # 选择最佳备选
    best = fallback_engine.select_best_provider(providers)
    
    # GLM Pro 应优先
    assert best["id"] == "glm"
```

**TC-FALLBACK-003：优先级 - 成本最低**
```python
def test_fallback_priority_cost():
    """测试优先级规则：成本最低"""
    fallback_engine = FallbackEngine()
    
    providers = [
        {"id": "deepseek", "remaining": 50000, "input_price": 0.005},
        {"id": "anthropic", "remaining": 50000, "input_price": 0.01},
        {"id": "glm", "remaining": 50000, "input_price": 0.02},
    ]
    
    # 选择最佳备选
    best = fallback_engine.select_best_provider(providers)
    
    # DeepSeek 价格最低
    assert best["id"] == "deepseek"
```

**TC-FALLBACK-004：优先级 - 响应时间最快**
```python
def test_fallback_priority_latency():
    """测试优先级规则：响应时间最快"""
    fallback_engine = FallbackEngine()
    
    providers = [
        {"id": "deepseek", "remaining": 50000, "latency": 500},
        {"id": "anthropic", "remaining": 50000, "latency": 200},
        {"id": "glm", "remaining": 50000, "latency": 300},
    ]
    
    # 选择最佳备选
    best = fallback_engine.select_best_provider(providers)
    
    # Anthropic 延迟最低
    assert best["id"] == "anthropic"
```

**TC-FALLBACK-005：优先级 - 成功率最高**
```python
def test_fallback_priority_success_rate():
    """测试优先级规则：成功率最高"""
    fallback_engine = FallbackEngine()
    
    providers = [
        {"id": "deepseek", "remaining": 50000, "success_rate": 0.95},
        {"id": "anthropic", "remaining": 50000, "success_rate": 0.98},
        {"id": "glm", "remaining": 50000, "success_rate": 0.97},
    ]
    
    # 选择最佳备选
    best = fallback_engine.select_best_provider(providers)
    
    # Anthropic 成功率最高
    assert best["id"] == "anthropic"
```

#### 2.2 切换策略测试

**TC-FALLBACK-006：切换策略 - 降级**
```python
def test_fallback_strategy_degrade():
    """测试降级策略"""
    fallback_engine = FallbackEngine()
    fallback_engine.config.strategy = "degrade"
    
    providers = [
        {"id": "anthropic", "tier": "pro", "remaining": 0},
        {"id": "glm", "tier": "standard", "remaining": 100000},
        {"id": "deepseek", "tier": "free", "remaining": 50000},
    ]
    
    # 选择降级备选
    best = fallback_engine.select_with_strategy(providers, "anthropic")
    
    # 应选择 Standard 级别的 GLM
    assert best["id"] == "glm"
    assert best["tier"] == "standard"
```

**TC-FALLBACK-007：切换策略 - 成本优化**
```python
def test_fallback_strategy_cost_optimize():
    """测试成本优化策略"""
    fallback_engine = FallbackEngine()
    fallback_engine.config.strategy = "cost_optimize"
    
    providers = [
        {"id": "anthropic", "input_price": 0.03, "remaining": 0},
        {"id": "glm", "input_price": 0.02, "remaining": 100000},
        {"id": "deepseek", "input_price": 0.005, "remaining": 50000},
    ]
    
    # 选择成本最低的
    best = fallback_engine.select_with_strategy(providers, "anthropic")
    
    # DeepSeek 价格最低
    assert best["id"] == "deepseek"
```

**TC-FALLBACK-008：切换策略 - 性能优先**
```python
def test_fallback_strategy_performance_first():
    """测试性能优先策略"""
    fallback_engine = FallbackEngine()
    fallback_engine.config.strategy = "performance_first"
    
    providers = [
        {"id": "anthropic", "latency": 100, "remaining": 0},
        {"id": "glm", "latency": 300, "remaining": 100000},
        {"id": "deepseek", "latency": 500, "remaining": 50000},
    ]
    
    # 选择性能最好的
    best = fallback_engine.select_with_strategy(providers, "anthropic")
    
    # GLM 性能第二好（ Anthropic 无配额）
    assert best["id"] == "glm"
```

**TC-FALLBACK-009：切换策略 - 负载均衡**
```python
def test_fallback_strategy_load_balance():
    """测试负载均衡策略"""
    fallback_engine = FallbackEngine()
    fallback_engine.config.strategy = "load_balance"
    
    providers = [
        {"id": "deepseek", "requests": 100, "remaining": 50000},
        {"id": "glm", "requests": 50, "remaining": 100000},
        {"id": "anthropic", "requests": 200, "remaining": 150000},
    ]
    
    # 选择负载最低的
    best = fallback_engine.select_with_strategy(providers, None)
    
    # GLM 负载最低
    assert best["id"] == "glm"
```

#### 2.3 切换触发测试

**TC-FALLBACK-010：触发条件 - 配额使用率 ≥ 90%**
```python
def test_fallback_trigger_quota_threshold():
    """测试配额阈值触发切换"""
    fallback_engine = FallbackEngine()
    
    # 当前提供商配额 90%
    current_quota = {"provider": "deepseek", "remaining": 10000, "total": 100000}
    
    # 应该触发切换
    assert fallback_engine.should_fallback(current_quota)
```

**TC-FALLBACK-011：触发条件 - 配额耗尽（429）**
```python
def test_fallback_trigger_quota_exhausted():
    """测试配额耗尽触发切换"""
    fallback_engine = FallbackEngine()
    
    # 模拟 429 错误
    error = HTTPError(429, "Too Many Requests")
    
    # 应该触发切换
    assert fallback_engine.should_fallback_on_error(error)
```

**TC-FALLBACK-012：触发条件 - 配额即将过期**
```python
def test_fallback_trigger_quota_expiry():
    """测试配额即将过期触发切换"""
    fallback_engine = FallbackEngine()
    
    # 当前提供商配额 1 小时后过期
    current_quota = {
        "provider": "deepseek",
        "remaining": 50000,
        "expiry": datetime.now() + timedelta(hours=1)
    }
    
    # 应该触发切换
    assert fallback_engine.should_fallback(current_quota)
```

**TC-FALLBACK-013：手动触发切换**
```python
def test_fallback_manual_trigger():
    """测试手动触发切换"""
    fallback_engine = FallbackEngine()
    
    # 手动触发
    result = fallback_engine.fallback("deepseek", "aliyun", reason="manual")
    
    assert result.success
    assert result.from_provider == "deepseek"
    assert result.to_provider == "aliyun"
    assert result.reason == "manual"
```

### 3. 提供商管理模块

#### 3.1 提供商注册测试

**TC-PROVIDER-001：注册提供商**
```python
def test_register_provider():
    """测试注册提供商"""
    manager = ProviderManager()
    
    provider = {
        "id": "deepseek",
        "name": "DeepSeek",
        "api_key": "sk-xxx",
        "base_url": "https://api.deepseek.com/v1"
    }
    
    manager.register(provider)
    
    # 验证注册成功
    assert manager.is_registered("deepseek")
    assert manager.get("deepseek") == provider
```

**TC-PROVIDER-002：注册重复提供商**
```python
def test_register_duplicate_provider():
    """测试注册重复提供商"""
    manager = ProviderManager()
    
    provider = {
        "id": "deepseek",
        "name": "DeepSeek",
        "api_key": "sk-xxx",
        "base_url": "https://api.deepseek.com/v1"
    }
    
    # 第一次注册
    manager.register(provider)
    
    # 第二次注册应抛出异常
    with pytest.raises(ProviderAlreadyRegisteredError):
        manager.register(provider)
```

**TC-PROVIDER-003：注销提供商**
```python
def test_unregister_provider():
    """测试注销提供商"""
    manager = ProviderManager()
    
    # 注册提供商
    provider = {
        "id": "deepseek",
        "name": "DeepSeek",
        "api_key": "sk-xxx",
        "base_url": "https://api.deepseek.com/v1"
    }
    manager.register(provider)
    
    # 注销
    manager.unregister("deepseek")
    
    # 验证注销成功
    assert not manager.is_registered("deepseek")
```

#### 3.2 健康检查测试

**TC-PROVIDER-004：健康检查 - 成功**
```python
def test_health_check_success():
    """测试健康检查成功"""
    manager = ProviderManager()
    
    # 健康检查
    is_healthy = manager.check_health("deepseek")
    
    assert is_healthy
```

**TC-PROVIDER-005：健康检查 - 失败**
```python
def test_health_check_failure():
    """测试健康检查失败"""
    manager = ProviderManager()
    
    # 模拟连接失败
    with patch('requests.get') as mock_get:
        mock_get.side_effect = ConnectionError()
        
        # 健康检查
        is_healthy = manager.check_health("deepseek")
        
        assert not is_healthy
```

**TC-PROVIDER-006：批量健康检查**
```python
def test_batch_health_check():
    """测试批量健康检查"""
    manager = ProviderManager()
    
    # 注册多个提供商
    for i in range(5):
        manager.register({
            "id": f"provider-{i}",
            "name": f"Provider {i}",
            "api_key": f"sk-xxx-{i}",
            "base_url": f"https://api-{i}.com/v1"
        })
    
    # 批量健康检查
    results = manager.check_all_health()
    
    assert len(results) == 5
```

### 4. 配置管理测试

#### 4.1 配置加载测试

**TC-CONFIG-001：加载配置文件**
```python
def test_load_config():
    """测试加载配置文件"""
    config_manager = ConfigManager()
    
    # 加载配置
    config = config_manager.load("config.yaml")
    
    # 验证配置结构
    assert "llm_providers" in config
    assert "auto_fallback" in config
    assert "alerts" in config
```

**TC-CONFIG-002：配置验证 - 有效**
```python
def test_validate_config_valid():
    """测试配置验证 - 有效配置"""
    config_manager = ConfigManager()
    
    config = {
        "llm_providers": {
            "deepseek": {
                "name": "DeepSeek",
                "api_key": "sk-xxx",
                "base_url": "https://api.deepseek.com/v1"
            }
        }
    }
    
    # 验证
    errors = config_manager.validate(config)
    
    assert len(errors) == 0
```

**TC-CONFIG-003：配置验证 - 缺少必需字段**
```python
def test_validate_config_missing_required():
    """测试配置验证 - 缺少必需字段"""
    config_manager = ConfigManager()
    
    config = {
        "llm_providers": {
            "deepseek": {
                "name": "DeepSeek"
                # 缺少 api_key 和 base_url
            }
        }
    }
    
    # 验证
    errors = config_manager.validate(config)
    
    assert len(errors) > 0
    assert any("api_key" in str(e) for e in errors)
    assert any("base_url" in str(e) for e in errors)
```

**TC-CONFIG-004：配置验证 - 端点 URL 格式错误**
```python
def test_validate_config_invalid_url():
    """测试配置验证 - 端点 URL 格式错误"""
    config_manager = ConfigManager()
    
    config = {
        "llm_providers": {
            "deepseek": {
                "name": "DeepSeek",
                "api_key": "sk-xxx",
                "base_url": "not-a-valid-url"
            }
        }
    }
    
    # 验证
    errors = config_manager.validate(config)
    
    assert len(errors) > 0
    assert any("base_url" in str(e) and "valid" in str(e) for e in errors)
```

#### 4.2 配置热更新测试

**TC-CONFIG-005：配置热更新**
```python
def test_config_hot_reload():
    """测试配置热更新"""
    config_manager = ConfigManager()
    
    # 加载初始配置
    config = config_manager.load("config.yaml")
    initial_providers = list(config["llm_providers"].keys())
    
    # 修改配置文件
    with open("config.yaml", "w") as f:
        yaml.dump({
            "llm_providers": {
                "new_provider": {
                    "name": "New Provider",
                    "api_key": "sk-yyy",
                    "base_url": "https://api-new.com/v1"
                }
            }
        }, f)
    
    # 热更新
    config_manager.reload()
    
    # 验证新配置
    new_config = config_manager.get_config()
    assert "new_provider" in new_config["llm_providers"]
```

### 5. 通知模块测试

#### 5.1 邮件通知测试

**TC-NOTIFY-001：发送邮件通知**
```python
def test_send_email_notification():
    """测试发送邮件通知"""
    notifier = EmailNotifier()
    
    alert = Alert(
        id="alert-001",
        provider="deepseek",
        type="warning",
        message="Quota usage: 90%"
    )
    
    # 发送邮件
    result = notifier.send(alert)
    
    assert result.success
    assert result.channel == "email"
```

**TC-NOTIFY-002：邮件模板渲染**
```python
def test_email_template_rendering():
    """测试邮件模板渲染"""
    notifier = EmailNotifier()
    
    alert = Alert(
        id="alert-001",
        provider="deepseek",
        type="warning",
        message="Quota usage: 90%"
    )
    
    # 渲染模板
    html = notifier.render_template(alert)
    
    # 验证模板内容
    assert "DeepSeek" in html
    assert "90%" in html
    assert "warning" in html.lower()
```

#### 5.2 Webhook 通知测试

**TC-NOTIFY-003：发送 Webhook 通知**
```python
def test_send_webhook_notification():
    """测试发送 Webhook 通知"""
    notifier = WebhookNotifier()
    
    alert = Alert(
        id="alert-001",
        provider="deepseek",
        type="warning",
        message="Quota usage: 90%"
    )
    
    # 发送 Webhook
    result = notifier.send(alert)
    
    assert result.success
    assert result.channel == "webhook"
```

**TC-NOTIFY-004：Webhook 重试**
```python
def test_webhook_retry():
    """测试 Webhook 重试"""
    notifier = WebhookNotifier()
    notifier.config.max_retries = 3
    
    alert = Alert(
        id="alert-001",
        provider="deepseek",
        type="warning",
        message="Quota usage: 90%"
    )
    
    # 模拟第一次失败
    with patch('requests.post') as mock_post:
        mock_post.side_effect = [ConnectionError(), Response(200)]
        
        # 发送 Webhook（应重试）
        result = notifier.send(alert)
        
        # 应该成功
        assert result.success
        assert mock_post.call_count == 2  # 失败 1 次，重试 1 次
```

#### 5.3 Feishu 通知测试

**TC-NOTIFY-005：发送 Feishu 通知**
```python
def test_send_feishu_notification():
    """测试发送 Feishu 通知"""
    notifier = FeishuNotifier()
    
    alert = Alert(
        id="alert-001",
        provider="deepseek",
        type="warning",
        message="Quota usage: 90%"
    )
    
    # 发送 Feishu 通知
    result = notifier.send(alert)
    
    assert result.success
    assert result.channel == "feishu"
```

---

## 🔗 集成测试（15+ 用例）

### IT-001：完整的配额监控和切换流程

```python
def test_full_quota_monitoring_and_fallback():
    """测试完整的配额监控和切换流程"""
    # 初始化
    provider_manager = ProviderManager()
    quota_monitor = QuotaMonitor()
    fallback_engine = FallbackEngine()
    
    # 注册提供商
    provider_manager.register(deepseek_provider)
    provider_manager.register(glm_provider)
    provider_manager.register(aliyun_provider)
    
    # 模拟 DeepSeek 配额耗尽
    quota_monitor.set_quota("deepseek", total=100000, remaining=0)
    
    # 触发告警
    alert = quota_monitor.check_alerts("deepseek")
    assert alert is not None
    
    # 触发切换
    fallback_result = fallback_engine.fallback("deepseek")
    assert fallback_result.success
    assert fallback_result.to_provider in ["glm", "aliyun"]
```

### IT-002：5小时限额配额耗尽和切换

```python
def test_5hour_limit_quota_exhaustion_and_fallback():
    """测试 5 小时限额配额耗尽和切换"""
    provider_manager = ProviderManager()
    fallback_engine = FallbackEngine()
    
    # 注册 GLM（5小时限额）
    provider_manager.register(glm_provider)
    provider_manager.register(deepseek_provider)
    
    # 模拟 429 错误
    fallback_engine.handle_429_error("glm")
    
    # 验证 GLM 被禁用
    assert not provider_manager.is_available("glm")
    
    # 切换到 DeepSeek
    result = fallback_engine.fallback("glm", "deepseek", reason="429_error")
    assert result.success
    
    # 验证 5 小时后恢复
    fallback_engine.advance_time(hours=5)
    assert provider_manager.is_available("glm")
```

### IT-003：多提供商按优先级切换

```python
def test_multi_provider_priority_fallback():
    """测试多提供商按优先级切换"""
    provider_manager = ProviderManager()
    fallback_engine = FallbackEngine()
    
    # 注册多个提供商
    for provider in [deepseek_provider, glm_provider, aliyun_provider, anthropic_provider]:
        provider_manager.register(provider)
    
    # 模拟 DeepSeek 配额耗尽
    quota_monitor.set_quota("deepseek", total=100000, remaining=0)
    
    # 按优先级选择备选
    best = fallback_engine.select_best_provider(
        provider_manager.get_all_available_providers()
    )
    
    # 验证选择了最佳备选
    assert best is not None
    assert best["id"] != "deepseek"
```

### IT-004：告警发送和接收

```python
def test_alert_sending_and_receiving():
    """测试告警发送和接收"""
    alert_engine = AlertEngine()
    email_notifier = EmailNotifier()
    
    # 创建告警
    alert = Alert(
        id="alert-001",
        provider="deepseek",
        type="warning",
        message="Quota usage: 90%"
    )
    
    # 发送告警
    email_notifier.send(alert)
    
    # 验证告警状态
    assert alert.status == "sent"
    assert alert.sent_at is not None
```

### IT-005：配置热更新和验证

```python
def test_config_hot_reload_and_validation():
    """测试配置热更新和验证"""
    config_manager = ConfigManager()
    
    # 加载初始配置
    config = config_manager.load("config.yaml")
    initial_providers = list(config["llm_providers"].keys())
    
    # 修改配置文件
    with open("config.yaml", "w") as f:
        yaml.dump(updated_config, f)
    
    # 热更新
    config_manager.reload()
    
    # 验证新配置
    new_config = config_manager.get_config()
    assert "new_provider" in new_config["llm_providers"]
```

---

## 🚀 端到端测试（5+ 用例）

### E2E-001：完整的配额监控和自动切换流程

```python
def test_e2e_quota_monitoring_and_auto_fallback():
    """端到端测试：完整的配额监控和自动切换流程"""
    # 1. 启动系统
    app = LLMProviderSwitcher()
    app.start()
    
    # 2. 配置提供商
    app.add_provider(deepseek_provider)
    app.add_provider(glm_provider)
    app.add_provider(aliyun_provider)
    
    # 3. 模拟 DeepSeek 配额耗尽
    app.set_quota("deepseek", remaining=0)
    
    # 4. 等待告警
    time.sleep(1)
    
    # 5. 验证告警已发送
    alerts = app.get_alerts()
    assert len(alerts) > 0
    
    # 6. 验证自动切换
    current_provider = app.get_current_provider()
    assert current_provider != "deepseek"
    
    # 7. 验证请求成功
    response = app.llm_call("Hello")
    assert response is not None
    
    # 8. 停止系统
    app.stop()
```

### E2E-002：5小时限额的完整流程

```python
def test_e2e_5hour_limit_full_workflow():
    """端到端测试：5小时限额的完整流程"""
    # 1. 启动系统
    app = LLMProviderSwitcher()
    app.start()
    
    # 2. 配置 GLM（5小时限额）
    app.add_provider(glm_provider)
    app.add_provider(deepseek_provider)
    
    # 3. 发送请求直到 429
    for i in range(1000):
        try:
            app.llm_call("Hello")
        except HTTPError as e:
            if e.status == 429:
                break
    
    # 4. 验证自动切换
    current_provider = app.get_current_provider()
    assert current_provider == "deepseek"
    
    # 5. 验证后续请求成功
    response = app.llm_call("Hello")
    assert response is not None
    
    # 6. 模拟 5 小时后
    app.advance_time(hours=5)
    
    # 7. 验证 GLM 恢复
    assert app.is_available("glm")
    
    # 8. 停止系统
    app.stop()
```

### E2E-003：多用户并发请求下的切换

```python
def test_e2e_concurrent_requests_fallback():
    """端到端测试：多用户并发请求下的切换"""
    # 1. 启动系统
    app = LLMProviderSwitcher()
    app.start()
    
    # 2. 配置提供商
    app.add_provider(deepseek_provider)
    app.add_provider(glm_provider)
    
    # 3. 模拟 10 个并发用户
    async def user_request(user_id):
        for i in range(100):
            response = app.llm_call(f"User {user_id}: Hello {i}")
            assert response is not None
    
    # 4. 并发执行
    await asyncio.gather(*[user_request(i) for i in range(10)])
    
    # 5. 验证切换历史
    history = app.get_fallback_history()
    assert len(history) > 0
    
    # 6. 停止系统
    app.stop()
```

### E2E-004：配置更新和系统重启

```python
def test_e2e_config_update_and_restart():
    """端到端测试：配置更新和系统重启"""
    # 1. 启动系统
    app = LLMProviderSwitcher()
    app.start()
    
    # 2. 修改配置文件
    with open("config.yaml", "w") as f:
        yaml.dump(updated_config, f)
    
    # 3. 触发配置热更新
    app.reload_config()
    
    # 4. 验证新配置生效
    providers = app.get_providers()
    assert "new_provider" in providers
    
    # 5. 停止系统
    app.stop()
```

### E2E-005：完整的一天使用场景

```python
def test_e2e_full_day_usage_scenario():
    """端到端测试：完整的一天使用场景"""
    # 1. 启动系统
    app = LLMProviderSwitcher()
    app.start()
    
    # 2. 配置多个提供商
    for provider in [deepseek_provider, glm_provider, aliyun_provider]:
        app.add_provider(provider)
    
    # 3. 模拟一天的使用
    for hour in range(24):
        # 模拟 100 个请求
        for i in range(100):
            try:
                response = app.llm_call(f"Request {hour}-{i}")
                assert response is not None
            except HTTPError as e:
                if e.status == 429:
                    # 等待切换
                    time.sleep(1)
                    response = app.llm_call(f"Request {hour}-{i}")
                    assert response is not None
        
        # 每小时检查告警
        alerts = app.get_alerts()
        print(f"Hour {hour}: {len(alerts)} alerts")
    
    # 4. 验证切换历史
    history = app.get_fallback_history()
    print(f"Total fallbacks: {len(history)}")
    
    # 5. 验证最终统计
    stats = app.get_statistics()
    print(f"Success rate: {stats['success_rate']}")
    print(f"Avg latency: {stats['avg_latency']}ms")
    print(f"Total cost: {stats['total_cost']}")
    
    # 6. 停止系统
    app.stop()
```

---

## 📊 测试覆盖目标

| 模块 | 测试类型 | 用例数 | 覆盖率目标 |
|------|----------|--------|------------|
| **配额监控** | 单元测试 | 10 | ≥ 85% |
| **切换引擎** | 单元测试 | 13 | ≥ 90% |
| **提供商管理** | 单元测试 | 6 | ≥ 85% |
| **配置管理** | 单元测试 | 5 | ≥ 85% |
| **通知模块** | 单元测试 | 5 | ≥ 80% |
| **集成测试** | 集成测试 | 5 | ≥ 80% |
| **端到端测试** | 端到端测试 | 5 | ≥ 75% |
| **总计** | - | 49+ | ≥ 80% |

---

## ✅ 验收标准

### 功能验收
- ✅ 所有单元测试通过（49+ 用例）
- ✅ 所有集成测试通过（5 用例）
- ✅ 所有端到端测试通过（5 用例）
- ✅ 测试覆盖率 ≥ 80%

### 性能验收
- ✅ 配额查询：< 500ms
- ✅ 切换决策：< 100ms
- ✅ 总体切换时间：< 10s
- ✅ 系统可用性：> 99.9%

### 质量验收
- ✅ 无 P0 级 bug
- ✅ 无 P1 级 bug
- ✅ 测试文档完整
- ✅ 代码审查通过

---

## 📝 测试数据准备

### Mock 数据

**提供商配置：**
```python
deepseek_provider = {
    "id": "deepseek",
    "name": "DeepSeek",
    "api_key": "sk-test-deepseek",
    "base_url": "https://api.deepseek.com/v1",
    "quota": {
        "type": "subscription",
        "tier": "standard",
        "total": 100000,
        "remaining": 85000
    }
}

glm_provider = {
    "id": "glm",
    "name": "智谱 GLM",
    "api_key": "0a4dc93068414349aff707a50d50f8be.4NJB9tRIN2eil9k8",
    "base_url": "https