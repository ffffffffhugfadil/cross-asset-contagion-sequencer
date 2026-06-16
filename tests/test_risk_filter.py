"""
Unit tests for risk filter module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from strategy.risk_filter import RiskFilter, is_risk_on_environment


class TestRiskFilter(unittest.TestCase):
    
    def setUp(self):
        self.filter = RiskFilter()
        self.sample_signals = [
            {'symbol': 'ETH', 'signal': 'EXIT_NOW'},
            {'symbol': 'BNB', 'signal': 'REDUCE'},
        ]
    
    def test_filter_by_fear_greed_extreme_fear(self):
        filtered, condition = self.filter.filter_by_fear_greed(
            self.sample_signals, fear_greed_index=20
        )
        self.assertEqual(condition, 'extreme_fear')
    
    def test_filter_by_fear_greed_extreme_greed(self):
        filtered, condition = self.filter.filter_by_fear_greed(
            self.sample_signals, fear_greed_index=95
        )
        self.assertEqual(condition, 'extreme_greed')
    
    def test_filter_by_fear_greed_none(self):
        filtered, condition = self.filter.filter_by_fear_greed(
            self.sample_signals, fear_greed_index=None
        )
        self.assertEqual(condition, 'unknown')
    
    def test_is_risk_on_environment(self):
        self.assertTrue(is_risk_on_environment(60, 45))
        self.assertFalse(is_risk_on_environment(30, 50))


if __name__ == '__main__':
    unittest.main()
