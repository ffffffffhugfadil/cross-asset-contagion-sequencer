"""
demo package - Visualization and interactive demo
"""

from .visualizer import ContagionVisualizer
from .demo import run_live_demo, run_backtest_demo, run_auto_demo

__all__ = [
    "ContagionVisualizer",
    "run_live_demo",
    "run_backtest_demo",
    "run_auto_demo",
]
