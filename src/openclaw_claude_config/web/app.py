"""
Web Dashboard for LLM Quota Fallback
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from ..config.provider_manager import ProviderManager
from ..core.fallback_engine import FallbackEngine
from ..core.quota_monitor import QuotaMonitor
from ..core.alert_engine import AlertEngine
from ..utils.logger import get_logger

# 创建 FastAPI 应用
app = FastAPI(
    title="OpenClaw Claude Config - Web Dashboard",
    description="LLM Quota Fallback Dashboard",
    version="2.0.2"
)

logger = get_logger(__name__)

# 初始化组件
provider_manager = ProviderManager()
fallback_engine = FallbackEngine(provider_manager)
quota_monitor = QuotaMonitor(provider_manager)
alert_engine = AlertEngine(provider_manager)

# 设置模板和静态文件
BASE_DIR = Path(__file__).parent.parent.parent
templates_dir = BASE_DIR / "templates"
static_dir = BASE_DIR / "static"

# 如果目录不存在则创建
templates_dir.mkdir(parents=True, exist_ok=True)
static_dir.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(templates_dir))

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard 首页"""
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "Dashboard"
        }
    )


@app.get("/providers", response_class=HTMLResponse)
async def providers_page(request: Request):
    """提供商页面"""
    providers = provider_manager.list_providers()
    available = provider_manager.get_available_providers()

    return templates.TemplateResponse(
        "providers.html",
        {
            "request": request,
            "title": "Providers",
            "providers": providers,
            "available": available
        }
    )


@app.get("/quota", response_class=HTMLResponse)
async def quota_page(request: Request):
    """配额监控页面"""
    providers = provider_manager.list_providers()
    quota_data = {}

    for provider_id, provider in providers.items():
        if provider.get("enabled"):
            quota_info = quota_monitor.query_quota(provider_id)
            if quota_info:
                quota_data[provider_id] = quota_info

    return templates.TemplateResponse(
        "quota.html",
        {
            "request": request,
            "title": "Quota Monitoring",
            "quota_data": quota_data
        }
    )


@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    """告警历史页面"""
    alerts = alert_engine.get_alerts()
    stats = alert_engine.get_alert_stats()

    return templates.TemplateResponse(
        "alerts.html",
        {
            "request": request,
            "title": "Alerts",
            "alerts": alerts,
            "stats": stats
        }
    )


@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    """配置页面"""
    fallback_config = provider_manager.get_fallback_config()
    quota_config = provider_manager.get_quota_monitoring_config()
    notification_config = provider_manager.get_notifications_config()

    return templates.TemplateResponse(
        "config.html",
        {
            "request": request,
            "title": "Configuration",
            "fallback_config": fallback_config,
            "quota_config": quota_config,
            "notification_config": notification_config
        }
    )


@app.get("/api/providers")
async def api_providers():
    """API：获取提供商列表"""
    providers = provider_manager.list_providers()
    available = provider_manager.get_available_providers()
    return {
        "providers": providers,
        "available": available
    }


@app.get("/api/quota")
async def api_quota():
    """API：获取配额数据"""
    providers = provider_manager.list_providers()
    quota_data = {}

    for provider_id, provider in providers.items():
        if provider.get("enabled"):
            quota_info = quota_monitor.query_quota(provider_id)
            if quota_info:
                quota_data[provider_id] = quota_info

    return quota_data


@app.get("/api/alerts")
async def api_alerts():
    """API：获取告警列表"""
    alerts = alert_engine.get_alerts()
    stats = alert_engine.get_alert_stats()
    return {
        "alerts": alerts,
        "stats": stats
    }


@app.get("/api/config")
async def api_config():
    """API：获取配置"""
    return {
        "fallback": provider_manager.get_fallback_config(),
        "quota": provider_manager.get_quota_monitoring_config(),
        "notification": provider_manager.get_notifications_config()
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "2.0.2"
    }


def run_web_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """运行 Web 服务器"""
    import uvicorn
    uvicorn.run(
        "openclaw_claude_config.web.app:app",
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    run_web_server()
