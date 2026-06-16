"""
strategy/signal_generator.py
============================
Generates actionable trading signals from contagion predictions.
"""

from typing import List, Dict


def generate_signal(impact_score: float, sequence_position: int, confidence: float) -> str:
    if confidence < 0.5:
        return 'WATCH'
    if impact_score > 0.7 and sequence_position <= 2:
        return 'EXIT_NOW'
    if impact_score > 0.4:
        return 'REDUCE'
    if impact_score > 0.2 or sequence_position <= 4:
        return 'WATCH'
    return 'HOLD'


def generate_all_signals(predictions: List[Dict], confidence_threshold: float = 0.4) -> List[Dict]:
    signals = []
    for pred in predictions:
        symbol = pred.get('symbol')
        impact = pred.get('impact_score', 0)
        position = pred.get('sequence_position', 99)
        confidence = pred.get('confidence', 0)
        
        if confidence < confidence_threshold:
            signal = 'WATCH'
        else:
            signal = generate_signal(impact, position, confidence)
        
        signals.append({'symbol': symbol, 'signal': signal, 'impact_score': impact, 'confidence': confidence})
    return signals


def get_signal_priority(signal: str) -> int:
    priorities = {'EXIT_NOW': 4, 'REDUCE': 3, 'WATCH': 2, 'HOLD': 1}
    return priorities.get(signal, 1)


def aggregate_portfolio_signal(signals: List[Dict]) -> Dict:
    if not signals:
        return {'highest_priority_signal': 'HOLD', 'assets_to_exit': [], 'assets_to_reduce': [], 'assets_to_watch': []}
    
    assets_to_exit = [s['symbol'] for s in signals if s['signal'] == 'EXIT_NOW']
    assets_to_reduce = [s['symbol'] for s in signals if s['signal'] == 'REDUCE']
    assets_to_watch = [s['symbol'] for s in signals if s['signal'] == 'WATCH']
    
    if assets_to_exit:
        highest = 'EXIT_NOW'
    elif assets_to_reduce:
        highest = 'REDUCE'
    elif assets_to_watch:
        highest = 'WATCH'
    else:
        highest = 'HOLD'
    
    return {'highest_priority_signal': highest, 'assets_to_exit': assets_to_exit, 
            'assets_to_reduce': assets_to_reduce, 'assets_to_watch': assets_to_watch}
