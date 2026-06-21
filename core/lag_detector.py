"""
core/lag_detector.py
====================
Cross-correlation lag detection between source and target assets.
"""

from typing import List, Tuple
import numpy as np


def cross_correlation(
    source_returns: List[float],
    target_returns: List[float],
    max_lag: int = 48,
) -> List[float]:
    """Compute cross-correlation between source and target at various lags."""
    if len(source_returns) < max_lag + 1 or len(target_returns) < max_lag + 1:
        return [0.0] * (max_lag + 1)
    
    src = np.array(source_returns, dtype=float)
    tgt = np.array(target_returns, dtype=float)
    
    correlations = []
    for lag in range(max_lag + 1):
        if lag == 0:
            src_aligned = src
            tgt_aligned = tgt
        else:
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
            correlations.append(float(corr))
    
    return correlations


def find_optimal_lag(
    source_returns: List[float],
    target_returns: List[float],
    max_lag: int = 48,
    min_correlation: float = 0.1,
) -> Tuple[int, float]:
    """Find lag that maximizes correlation."""
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
    """Calculate confidence in detected lag."""
    correlations = cross_correlation(source_returns, target_returns, max_lag)
    
    if not correlations:
        return 0.0
    
    r_at_zero = correlations[0] if len(correlations) > 0 else 0.0
    r_at_lag = correlations[optimal_lag] if optimal_lag < len(correlations) else 0.0
    
    improvement = r_at_lag - abs(r_at_zero)
    
    sharpness = 0.0
    if optimal_lag > 0 and optimal_lag < len(correlations) - 1:
        left = correlations[optimal_lag - 1]
        right = correlations[optimal_lag + 1]
        sharpness = r_at_lag - max(left, right)
    
    confidence = min(1.0, max(0.0, improvement * 2 + sharpness + abs(r_at_lag)))
    return confidence


def find_optimal_lag_windowed(
    source_returns: list[float],
    target_returns: list[float],
    onset_idx: int,
    window_before: int = 24,
    window_after: int = 72,
    max_lag: int = 48,
    min_correlation: float = 0.05,
    min_improvement: float = 0.02,  # ← FIX: minimal improvement over lag 0
) -> tuple[int, float]:
    """
    Find optimal lag focusing on crash window around onset.
    Prevents bulk-data noise from drowning the stress signal.
    
    FIX: Hanya pilih lag yang memiliki improvement > min_improvement
    dibanding correlation di lag 0.
    """
    total = len(source_returns)
    w_start = max(0, onset_idx - window_before)
    w_end = min(total, onset_idx + window_after)
    
    # Pastikan window cukup besar
    if w_end - w_start < 20:
        w_start = max(0, onset_idx - 48)
        w_end = min(total, onset_idx + 48)
    
    src_win = source_returns[w_start:w_end]
    tgt_win = target_returns[w_start:w_end]
    
    if len(src_win) < 10:
        return 0, 0.0
    
    # Hitung korelasi untuk semua lag
    corrs = cross_correlation(src_win, tgt_win, max_lag)
    
    if not corrs:
        return 0, 0.0
    
    r_at_zero = corrs[0] if len(corrs) > 0 else 0.0
    
    # Cari lag dengan korelasi tertinggi DAN improvement > min_improvement
    best_lag = 0
    best_corr = r_at_zero
    
    for lag, corr in enumerate(corrs):
        # FIX: Hanya pilih jika improvement signifikan
        improvement = corr - r_at_zero
        if corr > best_corr and improvement > min_improvement:
            best_corr = corr
            best_lag = lag
    
    # Kalau tidak ada improvement signifikan, balik ke 0
    if best_corr < min_correlation:
        return 0, 0.0
    
    return best_lag, best_corr


def detect_lag_pattern(
    source_returns: list[float],
    target_returns_list: list[tuple[str, list[float]]],
    max_lag: int = 48,
) -> list[tuple[str, int, float, float]]:
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
