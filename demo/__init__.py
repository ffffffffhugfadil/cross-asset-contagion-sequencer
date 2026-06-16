"""
demo package - Visualization and interactive demo
"""

from .visualizer import (
    plot_contagion_sequence,
    plot_correlation_heatmap,
    plot_impact_scores,
)

from .demo import (
    run_interactive_demo,
    run_historical_demo,
)

__all__ = [
    "plot_contagion_sequence",
    "plot_correlation_heatmap",
    "plot_impact_scores",
    "run_interactive_demo",
    "run_historical_demo",
]
