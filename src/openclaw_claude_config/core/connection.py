"""
网络工具模块
"""

import ssl
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from ..core.exceptions import (
    ConnectionError,
)
from ..utils.logger import get_logger


class ConnectionValidator:
    """LLM连接验证器 - 安全版本"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 1

    def test_connection(
        self,
        base_url: str,
        api_key: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        verify_ssl: bool = True,
    ) -> Dict[str, Any]:
        """测试LLM API连接（安全版本）

        Args:
            base_url: API基础URL
            api_key: API密钥
            model: 模型名称（可选）
            provider: 提供商名称（可选）
            verify_ssl: 是否验证SSL证书

        Returns:
            连接测试结果
        """
        result = {
            "success": False,
            "message": "",
            "error_type": None,
            "details": None,
            "latency_ms": 0,
        }

        # 重试机制
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                self.logger.debug(f"尝试连接 {base_url} (第{attempt + 1}次)")

                # 构建测试请求
                test_url = self._build_test_url(base_url, provider)
                req = self._build_request(test_url, api_key, model)

                # 创建SSL上下文
                ssl_context = self._create_ssl_context(verify_ssl)

                # 发送请求
                with urllib.request.urlopen(
                    req, timeout=self.timeout, context=ssl_context
                ) as response:
                    latency_ms = int((time.time() - start_time) * 1000)
                    result["latency_ms"] = latency_ms

                    if response.status == 200:
                        result["success"] = True
                        result["message"] = f"连接成功! 延迟: {latency_ms}ms"

                        # 尝试解析可用模型
                        try:
                            resp_body = response.read().decode("utf-8")
                            resp_json = json.loads(resp_body)
                            if "data" in resp_json and isinstance(
                                resp_json["data"], list
                            ):
                                result[
                                    "message"
                                ] += f", 可用模型: {len(resp_json['data'])}个"
                        except Exception as e:
                            self.logger.debug(f"解析响应失败: {e}")

                        break
                    else:
                        raise ConnectionError(f"HTTP {response.status}", "unknown")

            except urllib.error.HTTPError as e:
                latency_ms = int((time.time() - start_time) * 1000)
                result["latency_ms"] = latency_ms

                error = self._handle_http_error(e)
                result.update(error)

                # 认证错误不重试
                if error["error_type"] in ["auth", "model"]:
                    break

            except urllib.error.URLError as e:
                latency_ms = int((time.time() - start_time) * 1000)
                result["latency_ms"] = latency_ms

                error = self._handle_url_error(e)
                result.update(error)

                # 网络错误重试
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"网络错误，{self.retry_delay}秒后重试...")
                    time.sleep(self.retry_delay)

            except Exception as e:
                latency_ms = int((time.time() - start_time) * 1000)
                result["latency_ms"] = latency_ms
                result["error_type"] = "unknown"
                result["message"] = f"未知错误: {str(e)}"
                result["details"] = str(e)
                self.logger.error(f"连接测试异常: {e}", exc_info=True)

        return result

    def _build_test_url(self, base_url: str, provider: Optional[str]) -> str:
        """构建测试URL"""
        test_url = base_url.rstrip("/")
        if not test_url.endswith("/v1"):
            test_url += "/v1"

        # 根据provider选择测试端点
        if provider == "anthropic" or "/anthropic" in base_url:
            return f"{test_url}/models"
        elif provider == "openai" or "/openai" in base_url:
            return f"{test_url}/models"
        else:
            return f"{test_url}/chat/completions"

    def _build_request(self, url: str, api_key: str, model: Optional[str]):
        """构建HTTP请求"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "OpenClaw-Claude-Config/2.0",
        }

        if "chat/completions" in url:
            data = json.dumps(
                {
                    "model": model or "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1,
                }
            ).encode("utf-8")
            return urllib.request.Request(
                url, data=data, headers=headers, method="POST"
            )
        else:
            return urllib.request.Request(url, headers=headers, method="GET")

    def _create_ssl_context(self, verify_ssl: bool) -> ssl.SSLContext:
        """创建SSL上下文"""
        if verify_ssl:
            # 使用默认的SSL上下文，验证证书
            return ssl.create_default_context()
        else:
            # 仅在明确要求时跳过验证
            self.logger.warning("SSL证书验证已禁用，连接可能不安全")
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context

    def _handle_http_error(self, error: urllib.error.HTTPError) -> Dict[str, Any]:
        """处理HTTP错误"""
        if error.code == 401:
            return {
                "error_type": "auth",
                "message": "认证失败: API Key无效或已过期",
                "details": "HTTP 401 - 请检查API Key是否正确",
            }
        elif error.code == 403:
            return {
                "error_type": "auth",
                "message": "权限不足: 无法访问该资源",
                "details": "HTTP 403 - 请检查账户权限或配额",
            }
        elif error.code == 404:
            return {
                "error_type": "model",
                "message": "模型不存在: 指定的模型ID无效",
                "details": "HTTP 404 - 请检查模型ID是否正确",
            }
        elif error.code == 429:
            return {
                "error_type": "rate_limit",
                "message": "请求过于频繁: 已触发速率限制",
                "details": "HTTP 429 - 请稍后再试或升级套餐",
            }
        elif error.code >= 500:
            return {
                "error_type": "server",
                "message": f"服务器错误: {error.code}",
                "details": f"HTTP {error.code} - 服务端出现问题，请稍后重试",
            }
        else:
            return {
                "error_type": "unknown",
                "message": f"HTTP错误: {error.code}",
                "details": str(error),
            }

    def _handle_url_error(self, error: urllib.error.URLError) -> Dict[str, Any]:
        """处理URL错误"""
        error_str = str(error.reason) if hasattr(error, "reason") else str(error)

        if (
            "Name or service not known" in error_str
            or "getaddrinfo failed" in error_str
        ):
            return {
                "error_type": "network",
                "message": "网络错误: 无法解析服务器地址",
                "details": "DNS解析失败 - 请检查Base URL是否正确",
            }
        elif "Connection refused" in error_str or "Connection timed out" in error_str:
            return {
                "error_type": "network",
                "message": "网络错误: 无法连接到服务器",
                "details": "连接失败 - 请检查网络连接或服务器状态",
            }
        elif "SSL" in error_str or "certificate" in error_str:
            return {
                "error_type": "network",
                "message": "SSL证书错误",
                "details": f"证书验证失败 - {error_str}",
            }
        else:
            return {
                "error_type": "network",
                "message": "网络错误",
                "details": error_str,
            }

    @staticmethod
    def print_result(result: Dict[str, Any]):
        """打印验证结果"""
        if result["success"]:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
            if result["details"]:
                print(f"   详细信息: {result['details']}")
            if result["error_type"]:
                print(f"   错误类型: {result['error_type']}")
