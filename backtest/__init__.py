# backtest/__init__.py
"""
Backtest module for Cross-Asset Contagion Sequencer.
"""

from .events_config import EVENTS, get_all_events
from .outcome_extractor import find_stress_onset_index, compute_actual_order

__all__ = [
    'EVENTS',
    'get_all_events',
    'find_stress_onset_index',
    'compute_actual_order',
]
