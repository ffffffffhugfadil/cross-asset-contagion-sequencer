"""
core package - Contagion detection and sequencing logic
"""

from .sequencer import (
    ContagionSequencer,
    AssetReturn,
    LagResult,
    ContagionNode,
    SequencerOutput,
)

__all__ = [
    "ContagionSequencer",
    "AssetReturn",
    "LagResult",
    "ContagionNode",
    "SequencerOutput",
]
