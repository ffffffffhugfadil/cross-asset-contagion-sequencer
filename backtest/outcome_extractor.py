# backtest/outcome_extractor.py
from typing import List, Optional

def find_stress_onset_index(returns: List[float], threshold: float = -0.05, window: int = 6) -> Optional[int]:
    for w in [3, 6, 12, 24]:
        for i in range(w, len(returns)):
            if sum(returns[i-w:i]) <= threshold:
                return i
    return None

def compute_actual_order(targets, source_returns: List[float], event_date: str) -> List[str]:
    """
    Hybrid: gabungan max drawdown magnitude + peak timing.
    Khusus untuk event dengan 2 target, pakai max drawdown saja.
    """
    # Jika hanya 2 target, pakai max drawdown (lebih stabil)
    if len(targets) <= 2:
        results = []
        for target in targets:
            if len(target.returns) == 0:
                continue
            max_dd = min(target.returns)
            results.append((target.symbol, max_dd))
        results.sort(key=lambda x: x[1])  # most negative first
        return [r[0] for r in results]
    
    # Untuk 3+ target, pakai hybrid
    results = []
    for target in targets:
        if len(target.returns) == 0:
            continue
        
        max_dd = min(target.returns)
        min_idx = target.returns.index(max_dd)
        
        mag_score = abs(max_dd) / 0.5
        mag_score = min(1.0, mag_score)
        timing_score = 1 - (min_idx / len(target.returns))
        
        # 70% magnitude, 30% timing
        score = mag_score * 0.7 + timing_score * 0.3
        results.append((target.symbol, score))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in results]
