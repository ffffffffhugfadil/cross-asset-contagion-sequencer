"""
Cross-Asset Contagion Sequencer
================================
Core logic: given a stress event in a source asset, predict the
sequence, timing, and impact of contagion spreading to target assets.

This is the primary differentiator from existing CMC Skills.
Existing Skills detect *that* contagion happened.
This Skill predicts *which* assets get hit, *in what order*, and *when*.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional
import numpy as np


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class AssetReturn:
    """Normalised hourly price return for one asset."""
    symbol: str
    returns: list[float]          # ordered oldest → newest
    timestamps: list[str]         # ISO-8601, same length as returns
    derivatives_oi: Optional[float] = None   # open interest USD (latest)
    funding_rate: Optional[float] = None     # latest 8h funding rate


@dataclass
class LagResult:
    """Cross-correlation lag between source and one target asset."""
    target_symbol: str
    lag_hours: float              # positive = target lags source
    correlation_at_lag: float     # pearson r at best lag window
    confidence: float             # 0.0 – 1.0


@dataclass
class ContagionNode:
    """One asset in the predicted contagion sequence."""
    symbol: str
    sequence_position: int        # 1 = first to be hit after source
    estimated_lag_hours: float    # hours after source stress event
    impact_score: float           # 0.0 – 1.0 (expected drawdown severity)
    signal: str                   # EXIT_NOW | REDUCE | WATCH | HOLD
    correlation_at_lag: float
    confidence: float


@dataclass
class SequencerOutput:
    """Full output of the Cross-Asset Contagion Sequencer."""
    contagion_detected: bool
    source_asset: str
    stress_severity: str          # LOW | MEDIUM | HIGH | CRITICAL
    contagion_sequence: list[ContagionNode]
    overall_confidence: str       # LOW | MEDIUM | HIGH
    estimated_spread_window_hours: float
    reasoning: str
    data_quality_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "contagion_detected": self.contagion_detected,
            "source_asset": self.source_asset,
            "stress_severity": self.stress_severity,
            "overall_confidence": self.overall_confidence,
            "estimated_spread_window_hours": self.estimated_spread_window_hours,
            "contagion_sequence": [
                {
                    "symbol": n.symbol,
                    "sequence_position": n.sequence_position,
                    "estimated_lag_hours": round(n.estimated_lag_hours, 1),
                    "impact_score": round(n.impact_score, 3),
                    "signal": n.signal,
                    "correlation_at_lag": round(n.correlation_at_lag, 3),
                    "confidence": round(n.confidence, 3),
                }
                for n in self.contagion_sequence
            ],
            "reasoning": self.reasoning,
            "data_quality_flags": self.data_quality_flags,
        }


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _pearson(a: list[float], b: list[float]) -> float:
    """Safe Pearson correlation. Returns 0.0 on degenerate input."""
    if len(a) != len(b) or len(a) < 3:
        return 0.0
    arr_a = np.array(a, dtype=float)
    arr_b = np.array(b, dtype=float)
    std_a, std_b = arr_a.std(), arr_b.std()
    if std_a == 0 or std_b == 0:
        return 0.0
    return float(np.corrcoef(arr_a, arr_b)[0, 1])


def _compute_lag(
    source_returns: list[float],
    target_returns: list[float],
    max_lag_hours: int = 48,
) -> LagResult:
    """
    Find the lag (in hours) at which the target best correlates with the
    source.  Positive lag means the target moves *after* the source.
    """
    best_r = -999.0
    best_lag = 0

    for lag in range(0, max_lag_hours + 1):
        if lag == 0:
            r = _pearson(source_returns, target_returns)
        else:
            # shift: source[:-lag] vs target[lag:]
            if lag >= len(source_returns):
                break
            r = _pearson(source_returns[:-lag], target_returns[lag:])
        if r > best_r:
            best_r = r
            best_lag = lag

    # Confidence: how much better is best_lag vs lag-0?
    r_at_zero = _pearson(source_returns, target_returns)
    improvement = best_r - abs(r_at_zero)
    confidence = min(1.0, max(0.0, improvement * 2 + abs(best_r)))

    return LagResult(
        target_symbol="",       # filled by caller
        lag_hours=float(best_lag),
        correlation_at_lag=best_r,
        confidence=confidence,
    )


def _detect_stress(
    source: AssetReturn,
    stress_threshold: float = -0.05,
    lookback_hours: int = 6,
) -> tuple[bool, str, float]:
    """
    Check whether the source asset is under acute stress.

    Returns (detected, severity_label, stress_magnitude).
    stress_threshold: e.g. -0.05 means a 5% drop triggers detection.
    """
    recent = source.returns[-lookback_hours:] if len(source.returns) >= lookback_hours else source.returns
    cumulative = sum(recent)

    if cumulative <= stress_threshold * 2:
        return True, "CRITICAL", abs(cumulative)
    if cumulative <= stress_threshold * 1.5:
        return True, "HIGH", abs(cumulative)
    if cumulative <= stress_threshold:
        return True, "MEDIUM", abs(cumulative)
    return False, "NONE", abs(cumulative)


def _impact_score(
    lag_result: LagResult,
    stress_magnitude: float,
    derivatives_oi: Optional[float],
    funding_rate: Optional[float],
) -> float:
    """
    Estimate how severely the target asset will be impacted.

    Factors:
    - Correlation strength at lag
    - Source stress magnitude
    - Target open interest (higher OI = more amplification)
    - Funding rate (negative funding = shorts crowded = bounce risk)
    """
    base = lag_result.correlation_at_lag * stress_magnitude * 10

    # OI amplifier: normalised to [1.0, 1.5]
    oi_amp = 1.0
    if derivatives_oi and derivatives_oi > 0:
        # rough normalisation: $1B OI = 1.5x amplifier
        oi_amp = min(1.5, 1.0 + derivatives_oi / 2_000_000_000)

    # Funding dampener: negative funding → some short pressure → less impact
    funding_damp = 1.0
    if funding_rate is not None and funding_rate < -0.001:
        funding_damp = 0.85

    raw = base * oi_amp * funding_damp
    return min(1.0, max(0.0, raw))


def _signal_from_position(position: int, impact: float) -> str:
    """Map sequence position + impact to an actionable signal."""
    if position == 1 and impact > 0.6:
        return "EXIT_NOW"
    if position <= 2 and impact > 0.4:
        return "REDUCE"
    if position <= 4 or impact > 0.2:
        return "WATCH"
    return "HOLD"


def _overall_confidence(nodes: list[ContagionNode], data_flags: list[str]) -> str:
    if not nodes:
        return "LOW"
    avg_conf = sum(n.confidence for n in nodes) / len(nodes)
    penalty = len(data_flags) * 0.1
    score = avg_conf - penalty
    if score >= 0.65:
        return "HIGH"
    if score >= 0.40:
        return "MEDIUM"
    return "LOW"


def _build_reasoning(
    source: str,
    severity: str,
    nodes: list[ContagionNode],
    spread_hours: float,
    flags: list[str],
) -> str:
    if not nodes:
        return (
            f"No contagion signal detected from {source}. "
            "Stress level is below threshold or correlations are insufficient."
        )

    seq_str = " → ".join(
        f"{n.symbol}(+{n.estimated_lag_hours:.0f}h)" for n in nodes
    )
    flag_str = f" Data gaps: {', '.join(flags)}." if flags else ""

    return (
        f"{source} is showing {severity} stress. "
        f"Historical lag analysis predicts contagion will spread in this sequence: "
        f"{source} → {seq_str}. "
        f"Full spread expected within {spread_hours:.1f} hours.{flag_str} "
        f"Signals are research context only — not execution instructions."
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class ContagionSequencer:
    """
    Main sequencer class.

    Usage
    -----
    sequencer = ContagionSequencer()
    result = sequencer.run(
        source=AssetReturn("BTC", [...], [...]),
        targets=[AssetReturn("ETH", [...], [...]), ...],
        stress_threshold=-0.05,
        lookback_hours=6,
        max_lag_hours=48,
    )
    print(result.to_dict())
    """

    def run(
        self,
        source: AssetReturn,
        targets: list[AssetReturn],
        stress_threshold: float = -0.05,
        lookback_hours: int = 6,
        max_lag_hours: int = 48,
    ) -> SequencerOutput:
        """
        Run the full contagion sequencing pipeline.

        Parameters
        ----------
        source          : AssetReturn for the suspected stress origin
        targets         : list of AssetReturn for assets to sequence
        stress_threshold: cumulative return that triggers detection (negative)
        lookback_hours  : window to measure source stress
        max_lag_hours   : max lag to consider in cross-correlation
        """
        data_flags: list[str] = []

        # 1. Detect stress in source
        detected, severity, magnitude = _detect_stress(
            source, stress_threshold, lookback_hours
        )

        if not detected:
            return SequencerOutput(
                contagion_detected=False,
                source_asset=source.symbol,
                stress_severity="NONE",
                contagion_sequence=[],
                overall_confidence="LOW",
                estimated_spread_window_hours=0.0,
                reasoning=_build_reasoning(source.symbol, "NONE", [], 0.0, []),
                data_quality_flags=[],
            )

        # 2. Validate target data
        valid_targets: list[AssetReturn] = []
        for t in targets:
            if len(t.returns) < 6:
                data_flags.append(f"{t.symbol}: insufficient history")
                continue
            valid_targets.append(t)

        if not valid_targets:
            data_flags.append("No valid targets — cannot sequence.")
            return SequencerOutput(
                contagion_detected=True,
                source_asset=source.symbol,
                stress_severity=severity,
                contagion_sequence=[],
                overall_confidence="LOW",
                estimated_spread_window_hours=0.0,
                reasoning=_build_reasoning(source.symbol, severity, [], 0.0, data_flags),
                data_quality_flags=data_flags,
            )

        # 3. Compute lag for each target
        lag_results: list[tuple[AssetReturn, LagResult]] = []
        for t in valid_targets:
            lag = _compute_lag(source.returns, t.returns, max_lag_hours)
            lag.target_symbol = t.symbol
            lag_results.append((t, lag))

        # 4. Filter: only include assets with positive correlation at lag
        lag_results = [
            (t, lr) for t, lr in lag_results
            if lr.correlation_at_lag > 0.1
        ]

        if not lag_results:
            data_flags.append("No correlated targets found above threshold.")
            return SequencerOutput(
                contagion_detected=True,
                source_asset=source.symbol,
                stress_severity=severity,
                contagion_sequence=[],
                overall_confidence="LOW",
                estimated_spread_window_hours=0.0,
                reasoning=_build_reasoning(source.symbol, severity, [], 0.0, data_flags),
                data_quality_flags=data_flags,
            )

        # 5. Sort by lag (ascending) to build the sequence
        lag_results.sort(key=lambda x: x[1].lag_hours)

        # 6. Build ContagionNode list
        nodes: list[ContagionNode] = []
        for pos, (asset, lr) in enumerate(lag_results, start=1):
            impact = _impact_score(lr, magnitude, asset.derivatives_oi, asset.funding_rate)
            signal = _signal_from_position(pos, impact)
            nodes.append(
                ContagionNode(
                    symbol=asset.symbol,
                    sequence_position=pos,
                    estimated_lag_hours=lr.lag_hours,
                    impact_score=impact,
                    signal=signal,
                    correlation_at_lag=lr.correlation_at_lag,
                    confidence=lr.confidence,
                )
            )

        # 7. Spread window = lag of last node
        spread_hours = nodes[-1].estimated_lag_hours if nodes else 0.0

        # 8. Overall confidence
        conf_label = _overall_confidence(nodes, data_flags)

        # 9. Build reasoning
        reasoning = _build_reasoning(
            source.symbol, severity, nodes, spread_hours, data_flags
        )

        return SequencerOutput(
            contagion_detected=True,
            source_asset=source.symbol,
            stress_severity=severity,
            contagion_sequence=nodes,
            overall_confidence=conf_label,
            estimated_spread_window_hours=spread_hours,
            reasoning=reasoning,
            data_quality_flags=data_flags,
        )


# ---------------------------------------------------------------------------
# Quick smoke test (run directly: python sequencer.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json, random

    random.seed(42)

    def _fake_returns(n: int, trend: float = 0.0) -> list[float]:
        return [trend + random.gauss(0, 0.01) for _ in range(n)]

    # Simulate BTC crash: last 6 hours are strongly negative
    btc_returns = _fake_returns(72, 0.001)
    btc_returns[-6:] = [-0.025, -0.031, -0.018, -0.022, -0.019, -0.027]

    # ETH: high correlation, short lag
    eth_returns = [0.0] * 2 + btc_returns[:-2]
    eth_returns = [r + random.gauss(0, 0.005) for r in eth_returns]

    # BNB: medium correlation, medium lag
    bnb_returns = [0.0] * 6 + btc_returns[:-6]
    bnb_returns = [r + random.gauss(0, 0.008) for r in bnb_returns]

    # CAKE: lower correlation, longer lag
    cake_returns = [0.0] * 12 + btc_returns[:-12]
    cake_returns = [r + random.gauss(0, 0.012) for r in cake_returns]

    source = AssetReturn("BTC", btc_returns, [f"2022-11-{i:02d}T{h:02d}:00Z" for i in range(1,4) for h in range(24)])
    targets = [
        AssetReturn("ETH", eth_returns, [], derivatives_oi=8_000_000_000, funding_rate=-0.0002),
        AssetReturn("BNB", bnb_returns, [], derivatives_oi=2_000_000_000, funding_rate=0.0001),
        AssetReturn("CAKE", cake_returns, [], derivatives_oi=200_000_000, funding_rate=0.0003),
    ]

    sequencer = ContagionSequencer()
    result = sequencer.run(source, targets, stress_threshold=-0.05)

    print(json.dumps(result.to_dict(), indent=2))
