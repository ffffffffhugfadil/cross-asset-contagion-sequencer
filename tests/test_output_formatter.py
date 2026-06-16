"""
Unit tests for output formatter module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from strategy.output_formatter import format_for_llm, to_json_string, compress_for_agent


class TestOutputFormatter(unittest.TestCase):
    
    def test_format_for_llm_with_contagion(self):
        output = format_for_llm(
            contagion_detected=True,
            source_asset='BTC',
            stress_severity='CRITICAL',
            contagion_sequence=[{'symbol': 'ETH', 'sequence_position': 1, 
                                  'estimated_lag_hours': 2.0, 'impact_score': 0.94,
                                  'signal': 'EXIT_NOW', 'confidence': 0.92,
                                  'correlation_at_lag': 0.89}],
            overall_confidence='HIGH',
            estimated_spread_window_hours=18.0,
            reasoning='Test',
            data_quality_flags=[]
        )
        self.assertTrue(output['contagion_detected'])
        self.assertEqual(output['source_asset'], 'BTC')
    
    def test_format_for_llm_without_contagion(self):
        output = format_for_llm(
            contagion_detected=False,
            source_asset='BTC',
            stress_severity='NONE',
            contagion_sequence=[],
            overall_confidence='LOW',
            estimated_spread_window_hours=0.0,
            reasoning='No stress',
            data_quality_flags=[]
        )
        self.assertFalse(output['contagion_detected'])
    
    def test_to_json_string(self):
        output = format_for_llm(
            contagion_detected=True,
            source_asset='BTC',
            stress_severity='HIGH',
            contagion_sequence=[],
            overall_confidence='HIGH',
            estimated_spread_window_hours=10.0,
            reasoning='Test',
            data_quality_flags=[]
        )
        json_str = to_json_string(output)
        self.assertIsInstance(json_str, str)
    
    def test_compress_for_agent(self):
        output = format_for_llm(
            contagion_detected=True,
            source_asset='BTC',
            stress_severity='CRITICAL',
            contagion_sequence=[],
            overall_confidence='HIGH',
            estimated_spread_window_hours=18.0,
            reasoning='Test',
            data_quality_flags=[]
        )
        compressed = compress_for_agent(output)
        self.assertIn('detected', compressed)


if __name__ == '__main__':
    unittest.main()
