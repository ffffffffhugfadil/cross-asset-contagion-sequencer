"""
core/scorer.py
==============
Confidence scoring for contagion predictions.

Evaluates data quality, correlation strength, lag consistency,
and overall prediction reliability.
"""

from typing import List, Dict, Optional
import numpy as np


def calculate_confidence_score(
    correlations: List[float],
    lags: List[int],
    data_quality_flags: List[str],
    returns_length: int,
    min_required_returns: int = 72,
) -> float:
    """
    Calculate overall confidence score for contagion prediction.
    
    Args:
        correlations: Correlation coefficients for each target
        lags: Detected lag hours for each target
        data_quality_flags: List of data quality issues
        returns_length: Number of return data points available
        min_required_returns: Minimum returns needed for high confidence
    
    Returns:
        Confidence score between 0.0 and 1.0
    """
    score = 1.0
    
    # Factor 1: Data sufficiency
    if returns_length < min_required_returns:
        score -= (min_required_returns - returns_length) / min_required_returns * 0.3
    
    # Factor 2: Average correlation strength
    if correlations:
        avg_corr = sum(correlations) / len(correlations)
        if avg_corr < 0.3:
            score -= 0.2
        elif avg_corr < 0.5:
            score -= 0.1
        elif avg_corr > 0.7:
            score += 0.1
    else:
        score -= 0.3
    
    # Factor 3: Lag consistency (low variance = good)
    if len(lags) >= 2:
        lag_std = np.std(lags)
        if lag_std > 10:
            score -= 0.15
        elif lag_std > 5:
            score -= 0.08
    
    # Factor 4: Data quality flags penalty
    score -= len(data_quality_flags) * 0.1
    
    return max(0.0, min(1.0, score))


def confidence_level(score: float) -> str:
    """
    Convert numeric confidence score to label.
    
    Returns:
        'HIGH', 'MEDIUM', or 'LOW'
    """
    if score >= 0.65:
        return 'HIGH'
    elif score >= 0.40:
        return 'MEDIUM'
    else:
        return 'LOW'


def score_correlation_quality(
    correlation: float,
    returns_length: int,
) -> float:
    """
    Score the quality of a single correlation.
    
    Returns:
        Quality score between 0.0 and 1.0
    """
    # Base score from correlation strength
    base = max(0.0, min(1.0, (correlation + 1) / 2))
    
    # Boost for longer history
    history_boost = min(0.2, returns_length / 500)
    
    return min(1.0, base + history_boost)


def score_lag_prediction(
    predicted_lag: int,
    actual_lag: int,
    max_allowed_error: int = 3,
) -> float:
    """
    Score accuracy of lag prediction.
    
    Args:
        predicted_lag: Predicted lag in hours
        actual_lag: Actual lag in hours
        max_allowed_error: Maximum error before score becomes 0
    
    Returns:
        Accuracy score between 0.0 and 1.0
    """
    error = abs(predicted_lag - actual_lag)
    
    if error == 0:
        return 1.0
    elif error <= max_allowed_error:
        return 1.0 - (error / max_allowed_error) * 0.5
    else:
        return 0.0


def aggregate_sequence_confidence(
    predictions: List[Dict],
    min_targets: int = 3,
) -> Dict[str, float]:
    """
    Aggregate confidence across entire sequence prediction.
    
    Returns:
        Dict with overall_score, data_sufficiency, correlation_quality, lag_reliability
    """
    if not predictions or len(predictions) < min_targets:
        return {
            'overall_score': 0.0,
            'data_sufficiency': 0.0,
            'correlation_quality': 0.0,
            'lag_reliability': 0.0,
        }
    
    # Data sufficiency
    min_returns = min(p.get('returns_length', 0) for p in predictions)
    data_sufficiency = min(1.0, min_returns / 72)
    
    # Correlation quality
    correlations = [p.get('correlation', 0) for p in predictions]
    correlation_quality = sum(correlations) / len(correlations)
    
    # Lag reliability (inverse of variance)
    lags = [p.get('lag', 0) for p in predictions]
    if len(lags) > 1:
        lag_variance = np.var(lags)
        lag_reliability = max(0.0, 1.0 - (lag_variance / 50))
    else:
        lag_reliability = 0.5
    
    overall = (data_sufficiency * 0.3 + 
               correlation_quality * 0.5 + 
               lag_reliability * 0.2)
    
    return {
        'overall_score': overall,
        'data_sufficiency': data_sufficiency,
        'correlation_quality': correlation_quality,
        'lag_reliability': lag_reliability,
    }
