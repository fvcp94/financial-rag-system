"""Utility functions for the Financial RAG System with OpenRouter support."""

import os
import yaml
import tiktoken
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}


def get_api_key(service: str = "openrouter") -> str:
    """Retrieve API key from environment variables."""
    key_mapping = {
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY"
    }
    
    key_name = key_mapping.get(service.lower())
    if not key_name:
        raise ValueError(f"Unknown service: {service}")
    
    api_key = os.getenv(key_name)
    if not api_key:
        raise ValueError(f"{key_name} not found in environment variables. Get a FREE key at https://openrouter.ai/keys")
    
    return api_key


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text for a given model."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))


def estimate_cost(prompt_tokens: int, completion_tokens: int, model: str = "meta-llama/llama-3.2-3b-instruct:free") -> float:
    """
    Estimate API call cost based on token usage.
    
    Note: OpenRouter free models have $0.00 cost!
    """
    # Free models on OpenRouter
    if ":free" in model or "free" in model.lower():
        return 0.0
    
    # Pricing for paid models (USD per 1K tokens)
    pricing = {
        "gpt-4-turbo-preview": {"prompt": 0.01, "completion": 0.03},
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    }
    
    model_pricing = pricing.get(model, {"prompt": 0.0, "completion": 0.0})
    
    prompt_cost = (prompt_tokens / 1000) * model_pricing["prompt"]
    completion_cost = (completion_tokens / 1000) * model_pricing["completion"]
    
    return prompt_cost + completion_cost


def format_sources(sources: List[Dict[str, Any]]) -> str:
    """Format source documents for display."""
    formatted = []
    for idx, source in enumerate(sources, 1):
        metadata = source.get("metadata", {})
        content = source.get("content", "")[:200]
        
        formatted.append(
            f"\n**Source {idx}:**\n"
            f"- Document: {metadata.get('source', 'Unknown')}\n"
            f"- Page: {metadata.get('page', 'N/A')}\n"
            f"- Company: {metadata.get('company', 'N/A')}\n"
            f"- Preview: {content}...\n"
        )
    
    return "\n".join(formatted)


def create_timestamp() -> str:
    """Create formatted timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_dir(directory: str) -> None:
    """Ensure directory exists, create if it doesn't."""
    Path(directory).mkdir(parents=True, exist_ok=True)


class CostTracker:
    """Track API costs across queries."""
    
    def __init__(self, daily_limit: float = 0.0):  # Default $0 for free models
        self.daily_limit = daily_limit
        self.total_cost = 0.0
        self.query_count = 0
        self.costs_history = []
        self.reset_date = datetime.now().date()
    
    def add_cost(self, cost: float, query: str = "") -> None:
        """Add cost for a query."""
        current_date = datetime.now().date()
        
        # Reset if new day
        if current_date != self.reset_date:
            self.reset()
            self.reset_date = current_date
        
        self.total_cost += cost
        self.query_count += 1
        self.costs_history.append({
            "timestamp": create_timestamp(),
            "cost": cost,
            "query": query,
            "cumulative": self.total_cost
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary."""
        return {
            "total_cost": self.total_cost,
            "query_count": self.query_count,
            "average_cost_per_query": self.total_cost / max(self.query_count, 1),
            "daily_limit": self.daily_limit,
            "remaining_budget": "Unlimited (FREE!)" if self.daily_limit == 0 else max(0, self.daily_limit - self.total_cost),
            "utilization_pct": (self.total_cost / self.daily_limit) * 100 if self.daily_limit > 0 else 0,
            "is_free": self.daily_limit == 0
        }
    
    def reset(self) -> None:
        """Reset daily counters."""
        logger.info(f"Resetting cost tracker. Previous total: ${self.total_cost:.4f}")
        self.total_cost = 0.0
        self.query_count = 0
        self.costs_history = []


def validate_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize filter parameters."""
    valid_filters = {}
    
    if "company" in filters and isinstance(filters["company"], str):
        valid_filters["company"] = filters["company"].strip()
    
    if "year" in filters and isinstance(filters["year"], int):
        if 2020 <= filters["year"] <= 2030:
            valid_filters["year"] = filters["year"]
    
    if "quarter" in filters and filters["quarter"] in ["Q1", "Q2", "Q3", "Q4"]:
        valid_filters["quarter"] = filters["quarter"]
    
    return valid_filters


# Configure logger
logger.add(
    "logs/financial_rag_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
