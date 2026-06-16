"""
core/correlation.py
===================
Rolling correlation matrix for multi-asset contagion detection.

Computes pairwise correlations between source asset and targets
over multiple time windows to identify strengthening relationships
that may indicate contagion risk.
"""

from typing import List, Dict, Optional
import numpy as np


def pearson_correlation(x: List[float], y: List[float]) -> float:
    """
    Calculate Pearson correlation coefficient between two series.
    
    Args:
        x: First time series (list of floats)
        y: Second time series (list of floats)
    
    Returns:
        Correlation coefficient between -1 and 1.
        Returns 0.0 if insufficient data or zero variance.
    """
    if len(x) != len(y) or len(x) < 3:
        return 0.0
    
    arr_x = np.array(x, dtype=float)
    arr_y = np.array(y, dtype=float)
    
    std_x = arr_x.std()
    std_y = arr_y.std()
    
    if std_x == 0 or std_y == 0:
        return 0.0
    
    return float(np.corrcoef(arr_x, arr_y)[0, 1])


def rolling_correlation(
    source_returns: List[float],
    target_returns: List[float],
    window_hours: int = 24,
    step_hours: int = 1,
) -> List[Dict]:
    """
    Compute rolling correlation between source and target over time.
    
    Args:
        source_returns: Source asset hourly returns (oldest first)
        target_returns: Target asset hourly returns (oldest first)
        window_hours: Size of rolling window in hours
        step_hours: Step size between windows
    
    Returns:
        List of dicts with 'timestamp_index' and 'correlation'
    """
    if len(source_returns) < window_hours or len(target_returns) < window_hours:
        return []
    
    results = []
    max_start = min(len(source_returns), len(target_returns)) - window_hours
    
    for start in range(0, max_start + 1, step_hours):
        src_window = source_returns[start:start + window_hours]
        tgt_window = target_returns[start:start + window_hours]
        
        corr = pearson_correlation(src_window, tgt_window)
        results.append({
            "window_start_index": start,
            "window_end_index": start + window_hours - 1,
            "correlation": corr,
        })
    
    return results


def correlation_matrix(
    source_returns: List[float],
    targets_returns: Dict[str, List[float]],
    window_hours: int = 24,
) -> Dict[str, float]:
    """
    Compute current correlation between source and each target.
    
    Args:
        source_returns: Source asset hourly returns
        targets_returns: Dict mapping symbol -> returns list
        window_hours: Window size for correlation (uses most recent data)
    
    Returns:
        Dict mapping target symbol -> correlation coefficient
    """
    if len(source_returns) < window_hours:
        return {}
    
    # Use only the most recent window_hours data points
    src_recent = source_returns[-window_hours:]
    
    results = {}
    for symbol, tgt_returns in targets_returns.items():
        if len(tgt_returns) < window_hours:
            results[symbol] = 0.0
            continue
        
        tgt_recent = tgt_returns[-window_hours:]
        results[symbol] = pearson_correlation(src_recent, tgt_recent)
    
    return results


def correlation_trend(
    source_returns: List[float],
    target_returns: List[float],
    window_hours: int = 24,
    lookback_windows: int = 3,
) -> str:
    """
    Determine if correlation between source and target is increasing.
    
    Returns:
        'increasing', 'decreasing', or 'stable'
    """
    rolling_results = rolling_correlation(
        source_returns, target_returns, window_hours, step_hours=window_hours
    )
    
    if len(rolling_results) < 2:
        return 'stable'
    
    recent_corrs = [r['correlation'] for r in rolling_results[-lookback_windows:]]
    
    if len(recent_corrs) >= 2:
        if recent_corrs[-1] > recent_corrs[-2] + 0.05:
            return 'increasing'
        elif recent_corrs[-1] < recent_corrs[-2] - 0.05:
            return 'decreasing'
    
    return 'stable'


def is_contagion_correlation(correlation: float, threshold: float = 0.6) -> bool:
    """
    Check if correlation is strong enough to indicate contagion risk.
    
    Args:
        correlation: Pearson correlation coefficient
        threshold: Minimum correlation to flag as contagion risk
    
    Returns:
        True if correlation exceeds threshold
    """
    return correlation >= threshold
