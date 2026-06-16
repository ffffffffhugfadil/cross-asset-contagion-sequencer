"""
core/stress_detector.py
=======================
Detects acute stress events in source assets.

Identifies when an asset experiences abnormal drawdown
that could trigger cross-asset contagion.
"""

from typing import List, Tuple, Optional
import numpy as np


def detect_stress(
    returns: List[float],
    lookback_hours: int = 6,
    threshold: float = -0.05,
    volatility_scaled: bool = True,
) -> Tuple[bool, str, float]:
    """
    Detect if an asset is under acute stress.
    
    Args:
        returns: Hourly returns (oldest first)
        lookback_hours: Window to check for stress (hours)
        threshold: Cumulative return threshold (e.g., -0.05 = -5%)
        volatility_scaled: If True, scale threshold by recent volatility
    
    Returns:
        Tuple of (detected, severity, magnitude)
        Severity: 'CRITICAL', 'HIGH', 'MEDIUM', or 'NONE'
        Magnitude: absolute cumulative return
    """
    if len(returns) < lookback_hours:
        return False, 'NONE', 0.0
    
    recent = returns[-lookback_hours:]
    cumulative = sum(recent)
    magnitude = abs(cumulative)
    
    # Adjust threshold based on volatility if requested
    adjusted_threshold = threshold
    if volatility_scaled and len(returns) >= 24:
        recent_volatility = np.std(returns[-24:])
        # More volatile assets get wider threshold
        volatility_multiplier = 1.0 + recent_volatility * 2
        adjusted_threshold = threshold * volatility_multiplier
    
    if cumulative <= adjusted_threshold * 2:
        return True, 'CRITICAL', magnitude
    elif cumulative <= adjusted_threshold * 1.5:
        return True, 'HIGH', magnitude
    elif cumulative <= adjusted_threshold:
        return True, 'MEDIUM', magnitude
    
    return False, 'NONE', magnitude


def calculate_stress_magnitude(
    returns: List[float],
    lookback_hours: int = 6,
) -> float:
    """
    Calculate the magnitude of recent stress.
    
    Returns:
        Positive float representing drawdown magnitude
    """
    if len(returns) < lookback_hours:
        return 0.0
    
    recent = returns[-lookback_hours:]
    cumulative = sum(recent)
    
    return abs(cumulative)


def is_stress_escalating(
    returns: List[float],
    windows: List[int] = [3, 6, 12],
) -> bool:
    """
    Check if stress is escalating over multiple windows.
    
    Returns:
        True if later windows show larger drawdown than earlier ones
    """
    if len(returns) < max(windows):
        return False
    
    drawdowns = []
    for window in windows:
        if len(returns) >= window:
            recent = returns[-window:]
            drawdowns.append(abs(sum(recent)))
    
    if len(drawdowns) < 2:
        return False
    
    # Check if each subsequent window has larger drawdown
    for i in range(1, len(drawdowns)):
        if drawdowns[i] <= drawdowns[i-1]:
            return False
    
    return True


def get_stress_velocity(
    returns: List[float],
    lookback_hours: int = 6,
) -> float:
    """
    Calculate the velocity of stress (rate of decline).
    
    Returns:
        Average hourly return during stress window (negative for declines)
    """
    if len(returns) < lookback_hours:
        return 0.0
    
    recent = returns[-lookback_hours:]
    return sum(recent) / lookback_hours


def identify_stress_peak(
    prices: List[float],
    lookback_hours: int = 24,
) -> Tuple[int, float]:
    """
    Identify the peak price and its index within lookback window.
    
    Returns:
        Tuple of (index_from_end, peak_price)
    """
    if len(prices) < lookback_hours:
        recent = prices
    else:
        recent = prices[-lookback_hours:]
    
    peak_index = recent.index(max(recent))
    peak_price = recent[peak_index]
    
    # Return distance from end
    distance_from_end = len(recent) - 1 - peak_index
    
    return distance_from_end, peak_price
