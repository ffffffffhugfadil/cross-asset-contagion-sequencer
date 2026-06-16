"""
Unit tests for signal generator module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from strategy.signal_generator import (
    generate_signal,
    generate_all_signals,
    get_signal_priority,
    aggregate_portfolio_signal,
)


class TestSignalGenerator(unittest.TestCase):
    
    def test_generate_signal_exit_now(self):
        signal = generate_signal(0.85, 1, 0.9)
        self.assertEqual(signal, 'EXIT_NOW')
    
    def test_generate_signal_reduce(self):
        signal = generate_signal(0.55, 2, 0.8)
        self.assertEqual(signal, 'REDUCE')
    
    def test_generate_signal_watch(self):
        signal = generate_signal(0.30, 3, 0.7)
        self.assertEqual(signal, 'WATCH')
    
    def test_generate_signal_hold(self):
        signal = generate_signal(0.10, 6, 0.6)
        self.assertEqual(signal, 'HOLD')
    
    def test_generate_signal_low_confidence(self):
        signal = generate_signal(0.9, 1, 0.3)
        self.assertEqual(signal, 'WATCH')
    
    def test_generate_all_signals(self):
        predictions = [
            {'symbol': 'ETH', 'impact_score': 0.85, 'sequence_position': 1, 'confidence': 0.9},
            {'symbol': 'BNB', 'impact_score': 0.60, 'sequence_position': 2, 'confidence': 0.8},
        ]
        signals = generate_all_signals(predictions)
        self.assertEqual(len(signals), 2)
        self.assertEqual(signals[0]['signal'], 'EXIT_NOW')
    
    def test_get_signal_priority(self):
        self.assertEqual(get_signal_priority('EXIT_NOW'), 4)
        self.assertEqual(get_signal_priority('REDUCE'), 3)
        self.assertEqual(get_signal_priority('WATCH'), 2)
        self.assertEqual(get_signal_priority('HOLD'), 1)
    
    def test_aggregate_portfolio_signal(self):
        signals = [
            {'symbol': 'ETH', 'signal': 'EXIT_NOW'},
            {'symbol': 'BNB', 'signal': 'REDUCE'},
        ]
        agg = aggregate_portfolio_signal(signals)
        self.assertEqual(agg['highest_priority_signal'], 'EXIT_NOW')


if __name__ == '__main__':
    unittest.main()
