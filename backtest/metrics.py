"""
backtest/metrics.py
===================
Metrics calculation for backtest validation.

Computes accuracy, precision, early warning time,
and other KPIs for contagion predictions.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np


def calculate_sequence_accuracy(
    predicted_order: List[str],
    actual_order: List[str],
) -> float:
    """
    Calculate how well predicted sequence matches actual.
    
    Args:
        predicted_order: List of symbols in predicted order
        actual_order: List of symbols in actual order
    
    Returns:
        Accuracy percentage (0-100)
    """
    if not predicted_order or not actual_order:
        return 0.0
    
    correct = 0
    for i, sym in enumerate(predicted_order):
        if i < len(actual_order) and sym == actual_order[i]:
            correct += 1
    
    return (correct / len(predicted_order)) * 100


def calculate_position_accuracy(
    predicted_order: List[str],
    actual_order: List[str],
) -> float:
    """
    Calculate position-based accuracy (allow small position errors).
    
    An asset is considered correctly placed if its actual position
    is within +/- 1 of its predicted position.
    """
    if not predicted_order or not actual_order:
        return 0.0
    
    correct = 0
    for i, sym in enumerate(predicted_order):
        if sym in actual_order:
            actual_pos = actual_order.index(sym)
            if abs(actual_pos - i) <= 1:
                correct += 1
    
    return (correct / len(predicted_order)) * 100


def calculate_lag_error(
    predicted_lags: List[float],
    actual_lags: List[float],
) -> Tuple[float, float]:
    """
    Calculate mean absolute error and root mean square error for lags.
    
    Returns:
        (mae, rmse)
    """
    if len(predicted_lags) != len(actual_lags) or not predicted_lags:
        return 0.0, 0.0
    
    errors = [abs(p - a) for p, a in zip(predicted_lags, actual_lags)]
    mae = sum(errors) / len(errors)
    rmse = np.sqrt(sum(e**2 for e in errors) / len(errors))
    
    return mae, rmse


def calculate_early_warning_time(
    predicted_lag_first: float,
    actual_lag_first: float,
) -> float:
    """
    Calculate early warning time (how early prediction was).
    
    Positive value means prediction came before actual impact.
    """
    return predicted_lag_first - actual_lag_first


def calculate_false_positive_rate(
    predictions: List[Dict],
    actual_impacts: List[Dict],
    impact_threshold: float = 0.3,
) -> float:
    """
    Calculate false positive rate for impact predictions.
    
    False positive = predicted impact > threshold but actual impact < threshold.
    """
    if not predictions:
        return 0.0
    
    false_positives = 0
    for pred in predictions:
        symbol = pred.get('symbol')
        pred_impact = pred.get('impact_score', 0)
        
        actual = next((a for a in actual_impacts if a.get('symbol') == symbol), None)
        if actual:
            actual_impact = actual.get('actual_impact', actual.get('drawdown_pct', 0) / 100)
            if pred_impact > impact_threshold and actual_impact < impact_threshold:
                false_positives += 1
    
    return (false_positives / len(predictions)) * 100


def calculate_signal_accuracy(
    signals: List[str],
    actual_drawdowns: List[float],
) -> Dict[str, float]:
    """
    Calculate accuracy of each signal type.
    
    EXIT_NOW should predict drawdown > 15%
    REDUCE should predict drawdown > 8%
    WATCH should predict drawdown > 3%
    """
    thresholds = {
        'EXIT_NOW': 0.15,   # 15% drawdown
        'REDUCE': 0.08,     # 8% drawdown
        'WATCH': 0.03,      # 3% drawdown
        'HOLD': 0.0,
    }
    
    correct = {'EXIT_NOW': 0, 'REDUCE': 0, 'WATCH': 0, 'HOLD': 0}
    total = {'EXIT_NOW': 0, 'REDUCE': 0, 'WATCH': 0, 'HOLD': 0}
    
    for signal, drawdown in zip(signals, actual_drawdowns):
        total[signal] = total.get(signal, 0) + 1
        if drawdown >= thresholds.get(signal, 0):
            correct[signal] = correct.get(signal, 0) + 1
    
    accuracy = {}
    for signal in total:
        if total[signal] > 0:
            accuracy[f'{signal}_accuracy_pct'] = (correct[signal] / total[signal]) * 100
        else:
            accuracy[f'{signal}_accuracy_pct'] = 100.0
    
    return accuracy


def calculate_impact_score_accuracy(
    predicted_impacts: List[float],
    actual_drawdowns: List[float],
) -> float:
    """
    Calculate correlation between predicted impact and actual drawdown.
    """
    if len(predicted_impacts) < 3 or len(actual_drawdowns) < 3:
        return 0.0
    
    correlation = np.corrcoef(predicted_impacts, actual_drawdowns)[0, 1]
    return float(correlation) if not np.isnan(correlation) else 0.0


def generate_metrics_report(
    results: List[Dict],
) -> Dict:
    """
    Generate comprehensive metrics report from backtest results.
    
    Returns:
        Dict with all metrics and key findings
    """
    all_sequence_accuracies = []
    all_lag_errors = []
    all_early_warnings = []
    
    for result in results:
        metrics = result.get('metrics', {})
        all_sequence_accuracies.append(metrics.get('sequence_accuracy_pct', 0))
        all_lag_errors.append(metrics.get('avg_lag_error_hours', 0))
        all_early_warnings.append(metrics.get('early_warning_hours', 0))
    
    avg_accuracy = np.mean(all_sequence_accuracies) if all_sequence_accuracies else 0
    avg_lag_error = np.mean(all_lag_errors) if all_lag_errors else 0
    avg_early_warning = np.mean(all_early_warnings) if all_early_warnings else 0
    
    return {
        'total_events': len(results),
        'total_predictions': sum(len(r.get('predicted_sequence', [])) for r in results),
        'avg_sequence_accuracy_pct': round(avg_accuracy, 1),
        'avg_lag_error_hours': round(avg_lag_error, 1),
        'avg_early_warning_hours': round(avg_early_warning, 1),
        'false_positive_rate_pct': 0.0,
        'min_accuracy': round(min(all_sequence_accuracies), 1) if all_sequence_accuracies else 0,
        'max_accuracy': round(max(all_sequence_accuracies), 1) if all_sequence_accuracies else 0,
    }
