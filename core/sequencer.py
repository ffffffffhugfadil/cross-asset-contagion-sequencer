"""
core/sequencer.py
=================
Cross-Asset Contagion Sequencer — Main Pipeline.

Integrates all core modules:
- stress_detector.py  → detect stress onset + onset_idx
- lag_detector.py     → windowed lag detection around onset
- correlation.py      → correlation matrix
- scorer.py           → confidence scoring

Key fix: uses find_optimal_lag_windowed() which focuses lag detection
on the crash window around onset_idx, preventing bulk-data noise
from masking the contagion signal.

Usage:
    from core.sequencer import ContagionSequencer, AssetReturn
    sequencer = ContagionSequencer()
    result = sequencer.run(source, targets)
    print(result.to_dict())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from core.stress_detector import detect_stress_with_onset
from core.lag_detector import find_optimal_lag_windowed, lag_confidence
from core.correlation import correlation_matrix
from core.scorer import calculate_confidence_score, confidence_level

# ===== CMC INTEGRATION =====
try:
    from data.fetcher_cmc import (
        get_macro_regime,
        get_btc_correlation,
        get_btc_etf_demand,
        get_altcoin_breakouts,
    )
    CMC_AVAILABLE = True
except ImportError:
    CMC_AVAILABLE = False


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class AssetReturn:
    """Normalised hourly price return for one asset."""
    symbol: str
    returns: list[float]
    timestamps: list[str]
    derivatives_oi: Optional[float] = None
    funding_rate: Optional[float] = None


@dataclass
class LagResult:
    target_symbol: str
    lag_hours: float
    correlation_at_lag: float
    confidence: float


@dataclass
class ContagionNode:
    symbol: str
    sequence_position: int
    estimated_lag_hours: float
    impact_score: float
    signal: str
    correlation_at_lag: float
    confidence: float


@dataclass
class SequencerOutput:
    contagion_detected: bool
    source_asset: str
    stress_severity: str
    contagion_sequence: list[ContagionNode]
    overall_confidence: str
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

def _impact_score(
    lag_hours: float,
    correlation: float,
    stress_magnitude: float,
    derivatives_oi: Optional[float],
    funding_rate: Optional[float],
) -> float:
    base = correlation * stress_magnitude * 10
    lag_decay = max(0.7, 1.0 - (lag_hours / 100))
    oi_amp = 1.0
    if derivatives_oi and derivatives_oi > 0:
        oi_amp = min(1.5, 1.0 + derivatives_oi / 2_000_000_000)
    funding_damp = 1.0
    if funding_rate is not None and funding_rate < -0.001:
        funding_damp = 0.85
    return min(1.0, max(0.0, base * lag_decay * oi_amp * funding_damp))


def _signal_from_impact(position: int, impact: float) -> str:
    if position == 1 and impact > 0.6:
        return "EXIT_NOW"
    if position <= 2 and impact > 0.4:
        return "REDUCE"
    if position <= 4 or impact > 0.2:
        return "WATCH"
    return "HOLD"


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


# ===== CMC VALIDATION FUNCTION =====
def _get_cmc_context() -> dict:
    """Fetch CMC macro context for validation."""
    if not CMC_AVAILABLE:
        return {"available": False}
    
    try:
        macro = get_macro_regime()
        corr = get_btc_correlation()
        etf = get_btc_etf_demand()        # ← TAMBAH
        breakouts = get_altcoin_breakouts()  # ← TAMBAH
        return {
            "available": True,
            "macro": macro,
            "correlation": corr,
            "etf": etf,
            "breakouts": breakouts,
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Main Sequencer
# ---------------------------------------------------------------------------

class ContagionSequencer:

    def run(
        self,
        source: AssetReturn,
        targets: list[AssetReturn],
        stress_threshold: float = -0.05,
        lookback_hours: int = 6,
        max_lag_hours: int = 48,
        min_correlation: float = 0.1,
    ) -> SequencerOutput:

        data_flags: list[str] = []
        cmc_context = {}

        # ------------------------------------------------------------------
        # Step 1: Detect stress + get onset_idx
        # ------------------------------------------------------------------
        detected, severity, magnitude, onset_idx = detect_stress_with_onset(
            returns=source.returns,
            lookback_hours=lookback_hours,
            threshold=stress_threshold,
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

        # ------------------------------------------------------------------
        # Step 1b: CMC Validation (enhance confidence)
        # ------------------------------------------------------------------
        if CMC_AVAILABLE:
            cmc_context = _get_cmc_context()
            if cmc_context.get("available"):
                macro = cmc_context.get("macro", {})
                corr = cmc_context.get("correlation", {})
                etf = cmc_context.get("etf", {})
                breakouts = cmc_context.get("breakouts", {})
                
                # 1. Macro Regime
                if macro and macro.get('regime') == 'RISK_OFF':
                    confidence_boost = 0.9
                    data_flags.append("CMC: Risk-off regime confirmed")
                elif macro and macro.get('regime') == 'RISK_ON':
                    confidence_boost = 1.0
                    data_flags.append("CMC: Risk-on regime confirmed")
                else:
                    confidence_boost = 0.95
                
                # 2. BTC Correlation (DXY)
                dxy = corr.get('btc_vs_dxy', 0) if corr else 0
                if dxy is not None and dxy < -0.4:
                    severity = "HIGH"
                    data_flags.append(f"CMC: DXY divergence detected ({dxy:.2f})")
                
                # 3. ETF Flow
                if etf:
                    outflow = etf.get('etf_flow', {}).get('outflow', 0)
                    if outflow > 100_000_000:
                        confidence_boost *= 0.85
                        data_flags.append(f"CMC: Large ETF outflow detected (${outflow:,.0f})")
                
                # 4. Altcoin Breakouts
                if breakouts:
                    breakout_count = len(breakouts.get('breakout_queue', []))
                    if breakout_count > 5:
                        market_regime = "RISK_ON"
                        data_flags.append(f"CMC: {breakout_count} altcoin breakouts detected")
                
                # Store CMC context for output
                cmc_context["applied"] = True
                cmc_context["confidence_boost"] = confidence_boost

        # ------------------------------------------------------------------
        # Step 2: Validate targets
        # ------------------------------------------------------------------
        valid_targets: list[AssetReturn] = []
        for t in targets:
            if len(t.returns) < max(12, lookback_hours):
                data_flags.append(f"{t.symbol}: insufficient history ({len(t.returns)}h)")
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

        # ------------------------------------------------------------------
        # Step 3: Correlation matrix snapshot
        # ------------------------------------------------------------------
        targets_returns_dict = {t.symbol: t.returns for t in valid_targets}
        corr_mat = correlation_matrix(
            source_returns=source.returns,
            targets_returns=targets_returns_dict,
            window_hours=min(24, len(source.returns)),
        )

        # ------------------------------------------------------------------
        # Step 4: Windowed lag detection — focused on crash window
        # ------------------------------------------------------------------
        lag_results: list[tuple[AssetReturn, LagResult]] = []

        for t in valid_targets:
            # KEY FIX: use windowed lag detection around onset_idx
            lag_hours, corr_at_lag = find_optimal_lag_windowed(
                source_returns=source.returns,
                target_returns=t.returns,
                onset_idx=onset_idx,
                window_before=24,
                window_after=72,
                max_lag=max_lag_hours,
                min_correlation=min_correlation,
            )

            conf = lag_confidence(
                source_returns=source.returns,
                target_returns=t.returns,
                optimal_lag=lag_hours,
                max_lag=max_lag_hours,
            )

            # Blend lag result with current correlation snapshot
            current_corr = corr_mat.get(t.symbol, 0.0)
            blended_corr = corr_at_lag * 0.7 + current_corr * 0.3

            if blended_corr < min_correlation:
                data_flags.append(
                    f"{t.symbol}: correlation below threshold ({blended_corr:.3f})"
                )
                continue

            lag_results.append((
                t,
                LagResult(
                    target_symbol=t.symbol,
                    lag_hours=float(lag_hours),
                    correlation_at_lag=blended_corr,
                    confidence=conf,
                )
            ))

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

        # ------------------------------------------------------------------
        # Step 5: Sort by lag → build sequence
        # ------------------------------------------------------------------
        lag_results.sort(key=lambda x: x[1].lag_hours)

        nodes: list[ContagionNode] = []
        for pos, (asset, lr) in enumerate(lag_results, start=1):
            impact = _impact_score(
                lag_hours=lr.lag_hours,
                correlation=lr.correlation_at_lag,
                stress_magnitude=magnitude,
                derivatives_oi=asset.derivatives_oi,
                funding_rate=asset.funding_rate,
            )
            signal = _signal_from_impact(pos, impact)
            nodes.append(ContagionNode(
                symbol=asset.symbol,
                sequence_position=pos,
                estimated_lag_hours=lr.lag_hours,
                impact_score=impact,
                signal=signal,
                correlation_at_lag=lr.correlation_at_lag,
                confidence=lr.confidence,
            ))

        # ------------------------------------------------------------------
        # Step 6: Confidence scoring
        # ------------------------------------------------------------------
        correlations = [n.correlation_at_lag for n in nodes]
        lags = [int(n.estimated_lag_hours) for n in nodes]

        conf_score = calculate_confidence_score(
            correlations=correlations,
            lags=lags,
            data_quality_flags=data_flags,
            returns_length=len(source.returns),
        )
        conf_label = confidence_level(conf_score)

        # ------------------------------------------------------------------
        # Step 7: Output
        # ------------------------------------------------------------------
        spread_hours = nodes[-1].estimated_lag_hours if nodes else 0.0
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
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json, random, sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    random.seed(42)

    def fake(n, trend=0.0):
        return [trend + random.gauss(0, 0.01) for _ in range(n)]

    # BTC: stress injected at position 80 (middle of 168h window)
    btc = fake(168, 0.001)
    for i in range(6):
        btc[80 + i] = -0.018 - random.uniform(0, 0.01)

    # ETH: lag 3h after onset
    eth = [0.0]*3 + btc[:-3]
    eth = [r + random.gauss(0, 0.005) for r in eth]

    # BNB: lag 7h
    bnb = [0.0]*7 + btc[:-7]
    bnb = [r + random.gauss(0, 0.008) for r in bnb]

    # SOL: lag 14h
    sol = [0.0]*14 + btc[:-14]
    sol = [r + random.gauss(0, 0.012) for r in sol]

    ts = ["2022-11-08T00:00Z"] * 168

    source = AssetReturn("BTC", btc, ts)
    targets = [
        AssetReturn("ETH", eth, ts, derivatives_oi=8_000_000_000, funding_rate=-0.0002),
        AssetReturn("BNB", bnb, ts, derivatives_oi=2_000_000_000, funding_rate=0.0001),
        AssetReturn("SOL", sol, ts, derivatives_oi=500_000_000,   funding_rate=0.0003),
    ]

    seq = ContagionSequencer()
    result = seq.run(source, targets, stress_threshold=-0.05)
    print(json.dumps(result.to_dict(), indent=2))
