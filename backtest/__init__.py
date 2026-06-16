"""
backtest package - Historical event validation and metrics
"""

from .runner import (
    run_backtest,
    load_event_data,
)

from .metrics import (
    calculate_sequence_accuracy,
    calculate_early_warning_hours,
    calculate_false_positive_rate,
)

__all__ = [
    "run_backtest",
    "load_event_data",
    "calculate_sequence_accuracy",
    "calculate_early_warning_hours",
    "calculate_false_positive_rate",
]
