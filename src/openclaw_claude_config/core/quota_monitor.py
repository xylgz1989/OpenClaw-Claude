"""
Quota Monitor - Monitor provider quota usage
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
import requests

from ..config.provider_manager import ProviderManager
from ..utils.logger import get_logger


class QuotaMonitor:
    """Monitor provider quota usage"""

    def __init__(self, provider_manager: ProviderManager):
        self.provider_manager = provider_manager
        self.logger = get_logger(self.__class__.__name__)

    def query_quota(self, provider_id: str) -> Optional[Dict]:
        """Query quota from provider API"""
        provider = self.provider_manager.get_provider(provider_id)
        if not provider:
            self.logger.error(f"Provider {provider_id} not found")
            return None

        # Check provider type
        provider_type = provider.get("type", "")
        api_endpoint = provider.get("api_endpoint", "")
        api_key = provider.get("api_key", "")

        if not api_endpoint or not api_key:
            self.logger.error(f"Provider {provider_id} missing API endpoint or API key")
            return None

        # Query based on provider type
        if provider_type == "deepseek":
            return self._query_deepseek_quota(provider)
        elif provider_type == "anthropic":
            return self._query_anthropic_quota(provider)
        elif provider_type in ["zhipu", "glm", "aliyun", "kimi", "minimax"]:
            # For providers without quota API, return None
            self.logger.info(f"Provider {provider_id} ({provider_type}) does not support real-time quota query")
            return None
        else:
            self.logger.warning(f"Unknown provider type: {provider_type}")
            return None

    def _query_deepseek_quota(self, provider: Dict) -> Optional[Dict]:
        """Query DeepSeek quota from API"""
        try:
            api_endpoint = provider["api_endpoint"]
            api_key = provider["api_key"]

            url = f"{api_endpoint}/usage"

            headers = {
                'Authorization': f"Bearer {api_key}",
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                quota_info = {
                    "provider_id": provider["id"],
                    "limit": data.get('limit'),
                    "used": data.get('used', 0),
                    "remaining": data.get('remaining'),
                    "input_tokens": data.get('input_tokens', 0),
                    "output_tokens": data.get('output_tokens', 0),
                    "last_updated": datetime.utcnow().isoformat(),
                    "source": "api"
                }

                self.logger.info(f"DeepSeek quota queried for {provider['id']}")
                return quota_info

            else:
                self.logger.error(f"DeepSeek API error: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Error querying DeepSeek quota: {e}")
            return None

    def _query_anthropic_quota(self, provider: Dict) -> Optional[Dict]:
        """Query Anthropic quota from usage records"""
        try:
            # Anthropic doesn't have a quota API
            # We need to query from database or usage records
            # For now, return None

            self.logger.info(f"Anthropic quota query not yet implemented (requires database)")
            return None

        except Exception as e:
            self.logger.error(f"Error querying Anthropic quota: {e}")
            return None

    def check_quota_alerts(self, provider_id: str, quota_info: Dict) -> List[Dict]:
        """Check if quota alerts should be triggered"""
        alerts = []

        if not quota_info or not quota_info.get("limit"):
            return alerts

        used = quota_info.get("used", 0)
        limit = quota_info["limit"]

        if limit == 0:
            return alerts

        usage_percentage = (used / limit) * 100

        # Warning alert at 80%
        if usage_percentage >= 80 and usage_percentage < 90:
            alerts.append({
                'level': 'warning',
                'reason': 'quota_low',
                'message': f'Quota usage is {usage_percentage:.1f}%',
                'provider_id': provider_id,
                'quota_used_percentage': usage_percentage,
                'quota_remaining': quota_info.get('remaining'),
            })

        # Critical alert at 90%
        if usage_percentage >= 90 and usage_percentage < 95:
            alerts.append({
                'level': 'critical',
                'reason': 'quota_critical',
                'message': f'Quota usage is {usage_percentage:.1f}%',
                'provider_id': provider_id,
                'quota_used_percentage': usage_percentage,
                'quota_remaining': quota_info.get('remaining'),
            })

        # Exhausted alert at 95%+
        if usage_percentage >= 95:
            alerts.append({
                'level': 'critical',
                'reason': 'quota_exhausted',
                'message': f'Quota usage is {usage_percentage:.1f}%',
                'provider_id': provider_id,
                'quota_used_percentage': usage_percentage,
                'quota_remaining': quota_info.get('remaining'),
            })

        return alerts

    def predict_quota_exhaustion(self, provider_id: str) -> Optional[datetime]:
        """Predict when quota will be exhausted based on usage trend"""
        # TODO: Implement prediction based on usage history
        # This would require database access

        self.logger.warning("Quota exhaustion prediction not yet implemented")
        return None

    def query_all_quotas(self) -> Dict[str, Optional[Dict]]:
        """Query quota for all providers"""
        providers = self.provider_manager.list_providers(enabled_only=True)
        quotas = {}

        for provider_id, provider in providers.items():
            quota_info = self.query_quota(provider_id)
            if quota_info:
                quotas[provider_id] = quota_info
                # Check alerts
                alerts = self.check_quota_alerts(provider_id, quota_info)
                if alerts:
                    self.logger.info(f"Provider {provider_id} has {len(alerts)} alerts")

        return quotas

    def get_quota_status(self, provider_id: Optional[str] = None) -> Dict:
        """Get quota status"""
        if provider_id:
            quota_info = self.query_quota(provider_id)
            if quota_info:
                used = quota_info.get('used', 0)
                limit = quota_info.get('limit')
                remaining = quota_info.get('remaining', 0)
                usage_percentage = (used / limit * 100) if limit else 0

                alerts = self.check_quota_alerts(provider_id, quota_info)

                return {
                    'provider_id': provider_id,
                    'limit': limit,
                    'used': used,
                    'remaining': remaining,
                    'usage_percentage': usage_percentage,
                    'alerts': alerts,
                    'last_updated': quota_info.get('last_updated')
                }
            else:
                return {
                    'provider_id': provider_id,
                    'status': 'unknown',
                    'error': 'Quota info not available'
                }
        else:
            # Get all providers
            all_quotas = self.query_all_quotas()
            return {
                'providers': all_quotas,
                'total_providers': len(all_quotas),
                'providers_with_quota': len([q for q in all_quotas.values() if q and q.get('limit')])
            }

    def check_all_providers(self) -> Dict[str, Dict]:
        """Check all providers for quota issues"""
        providers = self.provider_manager.list_providers(enabled_only=True)
        results = {}

        for provider_id, provider in providers.items():
            quota_info = self.query_quota(provider_id)
            if quota_info:
                alerts = self.check_quota_alerts(provider_id, quota_info)

                if alerts:
                    results[provider_id] = {
                        'has_alerts': True,
                        'alerts': alerts,
                        'quota_info': quota_info
                    }
                else:
                    results[provider_id] = {
                        'has_alerts': False,
                        'alerts': [],
                        'quota_info': quota_info
                    }
            else:
                results[provider_id] = {
                    'status': 'no_quota_info',
                    'alerts': []
                }

        return results
