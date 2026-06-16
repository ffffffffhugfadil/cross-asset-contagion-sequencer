"""
strategy package - Signal generation and output formatting
"""

from .signal_generator import (
    generate_signal,
    generate_all_signals,
    get_signal_priority,
    aggregate_portfolio_signal,
)

from .risk_filter import (
    RiskFilter,
    is_risk_on_environment,
)

from .output_formatter import (
    format_for_llm,
    format_as_markdown,
    to_json_string,
    compress_for_agent,
)

__all__ = [
    "generate_signal",
    "generate_all_signals",
    "get_signal_priority",
    "aggregate_portfolio_signal",
    "RiskFilter",
    "is_risk_on_environment",
    "format_for_llm",
    "format_as_markdown",
    "to_json_string",
    "compress_for_agent",
]
