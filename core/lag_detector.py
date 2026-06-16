"""
core/lag_detector.py
====================
Cross-correlation lag detection between source and target assets.

Identifies the optimal lag (in hours) where target best correlates
with source, enabling prediction of contagion spread timing.
"""

from typing import List, Tuple, Optional
import numpy as np


def cross_correlation(
    source_returns: List[float],
    target_returns: List[float],
    max_lag: int = 48,
    normalize: bool = True,
) -> List[float]:
    """
    Compute cross-correlation between source and target at various lags.
    
    Args:
        source_returns: Source asset returns (oldest first)
        target_returns: Target asset returns (oldest first)
        max_lag: Maximum lag to consider (hours)
        normalize: If True, return correlation coefficients
    
    Returns:
        List of correlation values for lags 0 to max_lag
        Positive lag means target lags behind source
    """
    if len(source_returns) < max_lag + 1 or len(target_returns) < max_lag + 1:
        return [0.0] * (max_lag + 1)
    
    src = np.array(source_returns, dtype=float)
    tgt = np.array(target_returns, dtype=float)
    
    correlations = []
    
    for lag in range(max_lag + 1):
        if lag == 0:
            # No shift
            src_aligned = src
            tgt_aligned = tgt
        else:
            # Shift: source lags behind target? Wait, careful.
            # We want: if target lags source by lag hours,
            # then target[lag:] correlates with source[:-lag]
            if len(src) <= lag or len(tgt) <= lag:
                correlations.append(0.0)
                continue
            src_aligned = src[:-lag] if lag > 0 else src
            tgt_aligned = tgt[lag:] if lag > 0 else tgt
        
        min_len = min(len(src_aligned), len(tgt_aligned))
        if min_len < 3:
            correlations.append(0.0)
            continue
        
        src_aligned = src_aligned[:min_len]
        tgt_aligned = tgt_aligned[:min_len]
        
        std_src = src_aligned.std()
        std_tgt = tgt_aligned.std()
        
        if std_src == 0 or std_tgt == 0:
            correlations.append(0.0)
        else:
            corr = np.corrcoef(src_aligned, tgt_aligned)[0, 1]
            correlations.append(float(corr) if normalize else float(corr * std_src * std_tgt))
    
    return correlations


def find_optimal_lag(
    source_returns: List[float],
    target_returns: List[float],
    max_lag: int = 48,
    min_correlation: float = 0.1,
) -> Tuple[int, float]:
    """
    Find the lag that maximizes correlation between source and target.
    
    Args:
        source_returns: Source asset returns
        target_returns: Target asset returns
        max_lag: Maximum lag to search (hours)
        min_correlation: Minimum correlation to consider valid
    
    Returns:
        Tuple of (optimal_lag_hours, correlation_at_lag)
        Returns (0, 0.0) if no significant correlation found
    """
    correlations = cross_correlation(source_returns, target_returns, max_lag)
    
    best_lag = 0
    best_corr = correlations[0] if correlations else 0.0
    
    for lag, corr in enumerate(correlations):
        if corr > best_corr:
            best_corr = corr
            best_lag = lag
    
    if best_corr < min_correlation:
        return 0, 0.0
    
    return best_lag, best_corr


def lag_confidence(
    source_returns: List[float],
    target_returns: List[float],
    optimal_lag: int,
    max_lag: int = 48,
) -> float:
    """
    Calculate confidence in the detected lag.
    
    Higher confidence when:
    - Optimal lag is significantly better than lag 0
    - Correlation peak is sharp (not flat)
    
    Returns:
        Confidence score between 0.0 and 1.0
    """
    correlations = cross_correlation(source_returns, target_returns, max_lag)
    
    if not correlations:
        return 0.0
    
    r_at_zero = correlations[0] if len(correlations) > 0 else 0.0
    r_at_lag = correlations[optimal_lag] if optimal_lag < len(correlations) else 0.0
    
    # Improvement over zero lag
    improvement = r_at_lag - abs(r_at_zero)
    
    # Sharpness: difference between peak and neighbors
    sharpness = 0.0
    if optimal_lag > 0 and optimal_lag < len(correlations) - 1:
        left = correlations[optimal_lag - 1]
        right = correlations[optimal_lag + 1]
        sharpness = r_at_lag - max(left, right)
    
    confidence = min(1.0, max(0.0, improvement * 2 + sharpness + abs(r_at_lag)))
    
    return confidence


def detect_lag_pattern(
    source_returns: List[float],
    target_returns_list: List[Tuple[str, List[float]]],
    max_lag: int = 48,
) -> List[Tuple[str, int, float, float]]:
    """
    Detect lag patterns for multiple targets against a single source.
    
    Args:
        source_returns: Source asset returns
        target_returns_list: List of (symbol, returns) tuples
        max_lag: Maximum lag to consider
    
    Returns:
        List of (symbol, lag_hours, correlation, confidence) sorted by lag
    """
    results = []
    
    for symbol, tgt_returns in target_returns_list:
        lag, corr = find_optimal_lag(source_returns, tgt_returns, max_lag)
        conf = lag_confidence(source_returns, tgt_returns, lag, max_lag)
        
        if corr > 0.1:  # Only include meaningful correlations
            results.append((symbol, lag, corr, conf))
    
    # Sort by lag (assets that react first come first)
    results.sort(key=lambda x: x[1])
    
    return results
