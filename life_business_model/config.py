"""Configuration for factory.ai AI swarms."""
from dataclasses import dataclass

@dataclass
class Config:
    primary_model: str = "claude-opus-4-8"
    fast_model: str = "claude-haiku-4-5-20251001"
    repo_name: str = "factory.ai"
    affiliate_link: str = "https://twin.so?via=charles-lipshay"
    monthly_mrr_target: float = 25000.0  # factory.ai contributes $25K to $167K total
    automation_target_pct: float = 0.85

CONFIG = Config()
