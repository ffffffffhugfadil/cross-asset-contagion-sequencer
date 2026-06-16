"""
data/preprocessor.py
====================
Convert raw Binance/CMC data to AssetReturn dataclass format
that the sequencer expects.

Usage:
    from data.preprocessor import build_asset_returns, prepare_sequencer_input
    
    source, targets = prepare_sequencer_input(
        source_symbol="BTC",
        target_symbols=["ETH", "BNB", "CAKE"],
        hours=72
    )
    
    result = sequencer.run(source, targets)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional, Tuple
from core.sequencer import AssetReturn
from data.fetcher_binance import get_returns_with_timestamps, BINANCE_SYMBOLS

def build_asset_returns(
    symbol: str,
    hours: int = 72,
    derivatives_oi: Optional[float] = None,
    funding_rate: Optional[float] = None,
) -> Optional[AssetReturn]:
    """
    Fetch historical returns from Binance and wrap in AssetReturn dataclass.
    
    Args:
        symbol: Token symbol (BTC, ETH, BNB, etc.)
        hours: Number of hourly returns to fetch (minimum 24, recommended 72)
        derivatives_oi: Optional open interest (USD) for impact amplification
        funding_rate: Optional funding rate for dampening effect
    
    Returns:
        AssetReturn object ready for sequencer, or None if fetch fails
    """
    if symbol not in BINANCE_SYMBOLS:
        print(f"[Preprocessor] Symbol {symbol} not supported. Available: {list(BINANCE_SYMBOLS.keys())}")
        return None
    
    returns, timestamps = get_returns_with_timestamps(symbol, hours=hours)
    
    if not returns or len(returns) < 24:
        print(f"[Preprocessor] Insufficient returns for {symbol}: got {len(returns)} hours")
        return None
    
    return AssetReturn(
        symbol=symbol,
        returns=returns,
        timestamps=timestamps,
        derivatives_oi=derivatives_oi,
        funding_rate=funding_rate,
    )


def prepare_sequencer_input(
    source_symbol: str = "BTC",
    target_symbols: List[str] = None,
    hours: int = 72,
    include_derivatives: bool = False,
) -> Tuple[Optional[AssetReturn], List[AssetReturn]]:
    """
    Prepare complete input for ContagionSequencer.run()
    
    Args:
        source_symbol: The asset where stress is detected (default: BTC)
        target_symbols: List of assets to sequence (default: ETH, BNB, CAKE, LINK, ADA)
        hours: Hours of historical returns to fetch (recommended: 72)
        include_derivatives: If True, attempt to fetch OI/funding from CMC (requires API key)
    
    Returns:
        (source_asset, list_of_target_assets)
        Returns (None, []) if source fetch fails
    """
    if target_symbols is None:
        target_symbols = ["ETH", "BNB", "CAKE", "LINK", "ADA"]
    
    # Fetch source
    source = build_asset_returns(source_symbol, hours=hours)
    if source is None:
        print(f"[Preprocessor] Failed to fetch source: {source_symbol}")
        return None, []
    
    # Fetch targets (without derivatives first)
    targets = []
    for sym in target_symbols:
        target = build_asset_returns(sym, hours=hours)
        if target:
            targets.append(target)
        else:
            print(f"[Preprocessor] Skipping {sym} - insufficient data")
    
    # Optional: add derivatives from CMC
    if include_derivatives:
        try:
            from data.fetcher import CMCFetcher
            fetcher = CMCFetcher()
            deriv_data = fetcher.get_derivatives_metrics([source_symbol] + target_symbols)
            
            # Attach to source
            if source_symbol in deriv_data:
                source.derivatives_oi = deriv_data[source_symbol].get("open_interest_usd")
                source.funding_rate = deriv_data[source_symbol].get("funding_rate")
            
            # Attach to targets
            for target in targets:
                if target.symbol in deriv_data:
                    target.derivatives_oi = deriv_data[target.symbol].get("open_interest_usd")
                    target.funding_rate = deriv_data[target.symbol].get("funding_rate")
        except Exception as e:
            print(f"[Preprocessor] Could not add derivatives data: {e}")
    
    return source, targets


def quick_test():
    """Quick test to verify preprocessor works."""
    from core.sequencer import ContagionSequencer
    
    print("=== Testing Preprocessor + Sequencer ===\n")
    
    # Prepare input
    source, targets = prepare_sequencer_input(
        source_symbol="BTC",
        target_symbols=["ETH", "BNB"],
        hours=48,
        include_derivatives=False  # Set to True if you have CMC API key
    )
    
    if source is None or not targets:
        print("Failed to prepare input - check Binance API connection")
        return
    
    print(f"Source: {source.symbol} ({len(source.returns)} hourly returns)")
    for t in targets:
        print(f"Target: {t.symbol} ({len(t.returns)} returns)")
    
    # Run sequencer with a simulated stress (last 6 hours cumulative drop)
    # In real usage, you'd detect actual stress from price data
    import numpy as np
    
    # Check if last 6 hours show stress
    if len(source.returns) >= 6:
        recent_stress = sum(source.returns[-6:])
        print(f"\nRecent 6h stress for {source.symbol}: {recent_stress*100:.2f}%")
        
        if recent_stress < -0.005:  
            threshold = -0.005
        else:
            threshold = -0.01  
        
        print(f"Using stress threshold: {threshold*100}%")
        
        sequencer = ContagionSequencer()
        result = sequencer.run(source, targets, stress_threshold=threshold)
        
        print(f"\n=== Sequencer Output ===")
        print(f"Contagion detected: {result.contagion_detected}")
        if result.contagion_detected:
            print(f"Stress severity: {result.stress_severity}")
            print(f"Overall confidence: {result.overall_confidence}")
            print(f"Spread window: {result.estimated_spread_window_hours:.1f} hours")
            print(f"\nPredicted sequence:")
            for node in result.contagion_sequence:
                print(f"  {node.symbol} → +{node.estimated_lag_hours:.0f}h | signal: {node.signal} | impact: {node.impact_score:.2f}")
    else:
        print(f"\nInsufficient data for stress detection (need 6+ hours, got {len(source.returns)})")


if __name__ == "__main__":
    quick_test()