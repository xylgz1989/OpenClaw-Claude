"""
Fallback Engine - Intelligent provider switching
"""

from typing import List, Optional, Dict
from datetime import datetime
import uuid

from ..config.provider_manager import ProviderManager
from ..utils.logger import get_logger


class FallbackReason:
    """Fallback reason enumeration"""
    QUOTA_EXHAUSTED = "quota_exhausted"
    QUOTA_LOW = "quota_low"
    RATE_LIMITED = "rate_limited"
    PROVIDER_ERROR = "provider_error"
    NETWORK_ERROR = "network_error"
    MANUAL = "manual"
    SCHEDULED_MAINTENANCE = "scheduled_maintenance"
    UNKNOWN = "unknown"


class FallbackEngine:
    """Intelligent provider fallback engine"""

    def __init__(self, provider_manager: ProviderManager):
        self.provider_manager = provider_manager
        self.logger = get_logger(self.__class__.__name__)

    def select_provider(
        self,
        preferred_provider_id: Optional[str] = None,
        strategy: str = "balance"
    ) -> Optional[Dict]:
        """Select best provider based on strategy"""
        # Get all available providers
        available_providers = self.provider_manager.list_providers(enabled_only=True)

        if not available_providers:
            self.logger.warning("No available providers")
            return None

        # If preferred provider is specified and available, use it
        if preferred_provider_id:
            if preferred_provider_id in available_providers:
                return available_providers[preferred_provider_id]
            else:
                self.logger.warning(f"Preferred provider {preferred_provider_id} not available")

        # Select based on strategy
        if strategy == "balance":
            return self._select_by_balance(available_providers)
        elif strategy == "tier":
            return self._select_by_tier(available_providers)
        elif strategy == "cost":
            return self._select_by_cost(available_providers)
        elif strategy == "latency":
            return self._select_by_latency(available_providers)
        elif strategy == "success_rate":
            return self._select_by_success_rate(available_providers)
        else:
            self.logger.warning(f"Unknown strategy: {strategy}, using balance")
            return self._select_by_balance(available_providers)

    def _select_by_balance(self, providers: Dict[str, Dict]) -> Optional[Dict]:
        """Select provider by balance (quota + health + tier)"""
        scored_providers = []

        for provider_id, provider in providers.items():
            score = self._calculate_balance_score(provider)
            scored_providers.append((score, provider_id, provider))

        # Sort by score (descending)
        scored_providers.sort(key=lambda x: x[0], reverse=True)

        if scored_providers:
            best_provider_id = scored_providers[0][1]
            return providers[best_provider_id]
        return None

    def _calculate_balance_score(self, provider: Dict) -> float:
        """Calculate balance score for provider"""
        score = 0.0

        # Health score: 30%
        health_score = provider.get("health_score", 1.0)
        score += health_score * 0.30

        # Priority: 10%
        priority = provider.get("priority", 0)
        max_priority = 10.0
        priority_score = min(priority, max_priority) / max_priority
        score += priority_score * 0.10

        # Tier: 20%
        tier = provider.get("tier", "")
        tier_scores = {
            "enterprise": 1.0,
            "pro": 0.8,
            "free": 0.5,
            "": 0.5
        }
        tier_score = tier_scores.get(tier, 0.5)
        score += tier_score * 0.20

        # Check rate limit: -50% if rate limited
        if provider.get("rate_limit_5h", False):
            score -= 0.50

        # Check enabled: 0% if disabled
        if not provider.get("enabled", False):
            score -= 1.0

        return max(0.0, score)

    def _select_by_tier(self, providers: Dict[str, Dict]) -> Optional[Dict]:
        """Select provider by tier (higher tier = better)"""
        tier_order = ["enterprise", "pro", "free"]

        for tier in tier_order:
            for provider_id, provider in providers.items():
                if provider.get("tier") == tier:
                    return provider

        return None

    def _select_by_cost(self, providers: Dict[str, Dict]) -> Optional[Dict]:
        """Select provider by cost (lower cost = better)"""
        cost_providers = [
            (p.get("cost_per_1k_tokens", float('inf')), pid, p)
            for pid, p in providers.items()
            if p.get("cost_per_1k_tokens") and p.get("enabled", False)
        ]

        if cost_providers:
            cost_providers.sort(key=lambda x: x[0])
            return providers[cost_providers[0][1]]
        return None

    def _select_by_latency(self, providers: Dict[str, Dict]) -> Optional[Dict]:
        """Select provider by latency (lower latency = better)"""
        latency_providers = [
            (p.get("avg_latency_ms", float('inf')), pid, p)
            for pid, p in providers.items()
            if p.get("avg_latency_ms", 0) > 0 and p.get("enabled", False)
        ]

        if latency_providers:
            latency_providers.sort(key=lambda x: x[0])
            return providers[latency_providers[0][1]]
        return None

    def _select_by_success_rate(self, providers: Dict[str, Dict]) -> Optional[Dict]:
        """Select provider by success rate (higher success rate = better)"""
        rate_providers = [
            (p.get("success_rate", 0), pid, p)
            for pid, p in providers.items()
            if p.get("success_rate", 0) > 0 and p.get("enabled", False)
        ]

        if rate_providers:
            rate_providers.sort(key=lambda x: x[0], reverse=True)
            return providers[rate_providers[0][1]]
        return None

    def trigger_fallback(
        self,
        from_provider_id: str,
        reason: str = FallbackReason.MANUAL,
        reason_details: str = "",
        strategy: Optional[str] = None,
        to_provider_id: Optional[str] = None
    ) -> Dict:
        """Trigger fallback to another provider"""
        try:
            # Get from provider
            from_provider = self.provider_manager.get_provider(from_provider_id)
            if not from_provider:
                return {
                    "success": False,
                    "error": f"From provider {from_provider_id} not found"
                }

            # Get current strategy
            fallback_config = self.provider_manager.get_fallback_config()
            current_strategy = strategy or fallback_config.get("default_strategy", "balance")

            # Select new provider
            to_provider = self.select_provider(strategy=current_strategy)

            if not to_provider:
                return {
                    "success": False,
                    "error": "No available provider to fallback to"
                }

            # TODO: Perform actual provider switch
            # This would update the active provider in the config
            # For now, just log the action

            event = {
                "id": str(uuid.uuid4()),
                "from_provider_id": from_provider_id,
                "to_provider_id": to_provider["id"],
                "reason": reason,
                "reason_details": reason_details,
                "strategy": current_strategy,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True
            }

            self.logger.info(f"Switching provider: {from_provider_id} -> {to_provider['id']} (reason: {reason})")
            self.logger.info(f"Strategy: {current_strategy}")

            # TODO: Save to database or config
            # For now, just print

            return {
                "success": True,
                "from_provider_id": from_provider_id,
                "to_provider_id": to_provider["id"],
                "reason": reason,
                "strategy": current_strategy
            }

        except Exception as e:
            self.logger.error(f"Error triggering fallback: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_fallback_history(self, limit: int = 100) -> List[Dict]:
        """Get fallback history"""
        # TODO: Implement history retrieval from database
        self.logger.warning("Fallback history not yet implemented")
        return []
