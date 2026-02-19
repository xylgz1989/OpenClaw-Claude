"""
模型信息定义
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict


class PricingTier(Enum):
    """定价层级"""

    FREE = "免费版"
    STANDARD = "标准版"
    PRO = "专业版"
    ENTERPRISE = "企业版"
    PAY_PER_USE = "按量付费"
    LITE = "Lite版"
    MAX = "Max版"


@dataclass
class ModelInfo:
    """模型信息"""

    id: str
    name: str
    provider: str
    description: str
    pricing_tiers: List[PricingTier]
    context_length: int
    features: List[str]
    api_endpoint: str
    docs_url: str
    release_date: str
    parameters: str
    api_pricing: Dict[str, float] = field(default_factory=dict)
    is_anthropic_compatible: bool = True


class ModelRegistry:
    """模型注册表"""

    def __init__(self):
        self._models = {}
        self._register_builtin_models()

    def _register_builtin_models(self):
        """注册内置模型"""
        # 国内模型
        self.register_category(
            "china",
            {
                "qwen": {
                    "name": "通义千问",
                    "models": [
                        ModelInfo(
                            id="qwen/qwen3.5-plus",
                            name="Qwen 3.5-Plus",
                            provider="aliyun",
                            description="阿里最强开源模型，397B总参数/17B激活",
                            pricing_tiers=[
                                PricingTier.PAY_PER_USE,
                                PricingTier.ENTERPRISE,
                            ],
                            context_length=1000000,
                            features=[
                                "超长上下文1M",
                                "多模态",
                                "代码生成",
                                "201种语言",
                            ],
                            api_endpoint="https://dashscope.aliyuncs.com/api/v1",
                            docs_url="https://help.aliyun.com/dashscope",
                            release_date="2026-02-16",
                            parameters="397B/17B",
                            api_pricing={"input_per_1m": 0.8, "output_per_1m": 2.4},
                            is_anthropic_compatible=True,
                        ),
                    ],
                },
                "glm": {
                    "name": "智谱清言",
                    "models": [
                        ModelInfo(
                            id="zhipu/glm-5",
                            name="GLM-5",
                            provider="zhipu",
                            description="智谱最强旗舰，开源SOTA，编程能力接近Claude Opus 4.5",
                            pricing_tiers=[
                                PricingTier.PAY_PER_USE,
                                PricingTier.LITE,
                                PricingTier.PRO,
                                PricingTier.MAX,
                            ],
                            context_length=200000,
                            features=["开源SOTA", "编程能力顶尖", "Agent能力"],
                            api_endpoint="https://api.z.ai/api/coding/paas/v4",
                            docs_url="https://www.bigmodel.cn",
                            release_date="2026-02-12",
                            parameters="745B",
                            api_pricing={"input_per_1m": 2.0, "output_per_1m": 6.0},
                            is_anthropic_compatible=True,
                        ),
                    ],
                },
                "deepseek": {
                    "name": "DeepSeek",
                    "models": [
                        ModelInfo(
                            id="deepseek/deepseek-v4",
                            name="DeepSeek-V4",
                            provider="deepseek",
                            description="下一代旗舰模型，上下文100万token",
                            pricing_tiers=[PricingTier.PAY_PER_USE, PricingTier.FREE],
                            context_length=1000000,
                            features=["超长上下文1M", "代码能力顶尖", "低成本"],
                            api_endpoint="https://api.deepseek.com/v1",
                            docs_url="https://platform.deepseek.com/docs",
                            release_date="2026-03-31(预计)",
                            parameters="未公开",
                            api_pricing={"input_per_1m": 0.5, "output_per_1m": 2.0},
                            is_anthropic_compatible=True,
                        ),
                    ],
                },
                "kimi": {
                    "name": "Kimi",
                    "models": [
                        ModelInfo(
                            id="moonshot/kimi-k2.5",
                            name="Kimi K2.5",
                            provider="moonshot",
                            description="最强编程模型，原生多模态，总参数1T",
                            pricing_tiers=[
                                PricingTier.PAY_PER_USE,
                                PricingTier.FREE,
                                PricingTier.STANDARD,
                                PricingTier.PRO,
                            ],
                            context_length=256000,
                            features=["原生多模态", "超长上下文256K", "100 Tokens/s"],
                            api_endpoint="https://api.moonshot.cn/v1",
                            docs_url="https://platform.moonshot.cn/docs",
                            release_date="2026-01-30",
                            parameters="1T/32B MoE",
                            api_pricing={"input_per_1m": 0.6, "output_per_1m": 3.0},
                            is_anthropic_compatible=True,
                        ),
                    ],
                },
                "minimax": {
                    "name": "MiniMax",
                    "models": [
                        ModelInfo(
                            id="minimax/m2.5",
                            name="MiniMax M2.5",
                            provider="minimax",
                            description="MiniMax最新旗舰，50 tokens/s",
                            pricing_tiers=[PricingTier.PAY_PER_USE],
                            context_length=256000,
                            features=["高速推理", "低成本"],
                            api_endpoint="https://api.minimaxi.com/anthropic",
                            docs_url="https://www.minimaxi.com",
                            release_date="2026-02-12",
                            parameters="未公开",
                            api_pricing={"input_per_1m": 2.0, "output_per_1m": 16.0},
                            is_anthropic_compatible=True,
                        ),
                    ],
                },
            },
        )

        # 国际模型
        self.register_category(
            "international",
            {
                "anthropic": {
                    "name": "Anthropic",
                    "models": [
                        ModelInfo(
                            id="anthropic/claude-opus-4-5",
                            name="Claude Opus 4.5",
                            provider="anthropic",
                            description="Anthropic最强推理模型",
                            pricing_tiers=[PricingTier.PAY_PER_USE, PricingTier.PRO],
                            context_length=200000,
                            features=["最强推理", "代码能力", "长上下文"],
                            api_endpoint="https://api.anthropic.com/v1",
                            docs_url="https://docs.anthropic.com",
                            release_date="2025",
                            parameters="未公开",
                            api_pricing={"input_per_1m": 15.0, "output_per_1m": 75.0},
                            is_anthropic_compatible=True,
                        ),
                        ModelInfo(
                            id="anthropic/claude-sonnet-4-20250514",
                            name="Claude Sonnet 4",
                            provider="anthropic",
                            description="平衡性能和成本的模型",
                            pricing_tiers=[PricingTier.PAY_PER_USE],
                            context_length=200000,
                            features=["平衡性能", "快速响应", "代码能力"],
                            api_endpoint="https://api.anthropic.com/v1",
                            docs_url="https://docs.anthropic.com",
                            release_date="2025",
                            parameters="未公开",
                            api_pricing={"input_per_1m": 3.0, "output_per_1m": 15.0},
                            is_anthropic_compatible=True,
                        ),
                    ],
                },
            },
        )

    def register_category(self, category: str, providers: Dict):
        """注册模型类别"""
        self._models[category] = providers

    def get_models(self, category: str = "all") -> Dict[str, Dict]:
        """获取模型"""
        if category == "all":
            return self._models
        return self._models.get(category, {})

    def get_model_info(self, model_id: str) -> ModelInfo:
        """获取特定模型信息"""
        for category_providers in self._models.values():
            for provider_info in category_providers.values():
                for model in provider_info.get("models", []):
                    if model.id == model_id:
                        return model
        return None

    def list_models(self, category: str = "all") -> List[ModelInfo]:
        """列出所有模型"""
        models = []
        if category == "all":
            categories = self._models.keys()
        else:
            categories = [category]

        for cat in categories:
            for provider_info in self._models.get(cat, {}).values():
                models.extend(provider_info.get("models", []))

        return models
