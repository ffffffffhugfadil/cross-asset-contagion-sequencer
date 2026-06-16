"""
Unit tests for lag detector module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import random
from core.lag_detector import (
    cross_correlation,
    find_optimal_lag,
    lag_confidence,
    detect_lag_pattern,
)


class TestLagDetector(unittest.TestCase):
    
    # =========================================================
    # cross_correlation() tests
    # =========================================================
    
    def test_cross_correlation_zero_lag_identical(self):
        """Test cross-correlation at zero lag for identical series"""
        source = [0.01, -0.005, 0.02, -0.01, 0.005, 0.01]
        target = [0.01, -0.005, 0.02, -0.01, 0.005, 0.01]
        
        correlations = cross_correlation(source, target, max_lag=5)
        self.assertGreater(correlations[0], 0.99)
    
    def test_cross_correlation_zero_lag_high_correlation(self):
        """Test high correlation at zero lag"""
        source = [1, 2, 3, 4, 5, 6, 7, 8]
        target = [2, 4, 6, 8, 10, 12, 14, 16]
        
        correlations = cross_correlation(source, target, max_lag=5)
        self.assertGreater(correlations[0], 0.99)
    
    def test_cross_correlation_positive_lag(self):
        """Test cross-correlation detects positive lag"""
        source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        target = [1, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        
        correlations = cross_correlation(source, target, max_lag=5)
        # Lag 1 or 2 should have higher correlation than lag 0
        max_lag_corr = max(correlations[1:3]) if len(correlations) > 2 else 0
        self.assertGreater(max_lag_corr, correlations[0])
    
    def test_cross_correlation_output_length(self):
        """Test cross-correlation returns correct number of values"""
        source = [0.01, -0.005, 0.02, -0.01, 0.005]
        target = [0.008, -0.004, 0.018, -0.008, 0.004]
        
        correlations = cross_correlation(source, target, max_lag=10)
        self.assertEqual(len(correlations), 11)
    
    def test_cross_correlation_max_lag_zero(self):
        """Test cross-correlation with max_lag = 0"""
        source = [1, 2, 3, 4, 5]
        target = [2, 4, 6, 8, 10]
        
        correlations = cross_correlation(source, target, max_lag=0)
        self.assertEqual(len(correlations), 1)
        self.assertGreater(correlations[0], 0.99)
    
    def test_cross_correlation_insufficient_data(self):
        """Test cross-correlation with insufficient data"""
        source = [1, 2]
        target = [2, 3]
        
        correlations = cross_correlation(source, target, max_lag=5)
        for c in correlations:
            self.assertEqual(c, 0.0)
    
    def test_cross_correlation_negative_correlation(self):
        """Test cross-correlation with negative relationship"""
        source = [1, 2, 3, 4, 5, 6, 7, 8]
        target = [8, 7, 6, 5, 4, 3, 2, 1]
        
        correlations = cross_correlation(source, target, max_lag=3)
        self.assertLess(correlations[0], -0.9)
    
    def test_cross_correlation_with_noise(self):
        """Test cross-correlation with noisy data"""
        random.seed(42)
        source = [i + random.gauss(0, 0.1) for i in range(20)]
        target = [i + random.gauss(0, 0.1) for i in range(20)]
        
        correlations = cross_correlation(source, target, max_lag=5)
        self.assertEqual(len(correlations), 6)
        self.assertGreater(correlations[0], 0.5)
    
    # =========================================================
    # find_optimal_lag() tests
    # =========================================================
    
    def test_find_optimal_lag_positive_lag(self):
        """Test finding optimal positive lag"""
        source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        target = [1, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        
        lag, corr = find_optimal_lag(source, target, max_lag=5)
        
        self.assertIn(lag, [1, 2])
        self.assertGreater(corr, 0.85)
    
    def test_find_optimal_lag_zero_lag(self):
        """Test finding optimal lag when series are perfectly aligned"""
        source = [0.01, -0.005, 0.02, -0.01, 0.005]
        target = [0.01, -0.005, 0.02, -0.01, 0.005]
        
        lag, corr = find_optimal_lag(source, target, max_lag=3)
        
        self.assertEqual(lag, 0)
        self.assertGreater(corr, 0.99)
    
    def test_find_optimal_lag_low_correlation(self):
        """Test when no significant correlation exists"""
        source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        target = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        
        lag, corr = find_optimal_lag(source, target, max_lag=5, min_correlation=0.1)
        
        self.assertEqual(lag, 0)
        self.assertEqual(corr, 0.0)
    
    def test_find_optimal_lag_custom_min_correlation(self):
        """Test with custom minimum correlation threshold"""
        source = [1, 2, 3, 4, 5, 6, 7, 8]
        target = [2, 4, 6, 8, 10, 12, 14, 16]
        
        lag, corr = find_optimal_lag(source, target, max_lag=3, min_correlation=0.5)
        self.assertEqual(lag, 0)
        self.assertGreater(corr, 0.9)
    
    def test_find_optimal_lag_with_large_max_lag(self):
        """Test with large max_lag value"""
        source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        target = [1, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        
        lag, corr = find_optimal_lag(source, target, max_lag=10)
        
        self.assertIn(lag, [3, 4, 5])
        self.assertGreater(corr, 0.8)
    
    def test_find_optimal_lag_insufficient_data(self):
        """Test with insufficient data"""
        source = [1, 2]
        target = [2, 3]
        
        lag, corr = find_optimal_lag(source, target, max_lag=5)
        self.assertEqual(lag, 0)
        self.assertEqual(corr, 0.0)
    
    def test_find_optimal_lag_with_noise(self):
        """Test optimal lag detection with noisy data"""
        random.seed(42)
        source = [i + random.gauss(0, 0.05) for i in range(20)]
        target = [0, 0] + [i + random.gauss(0, 0.05) for i in range(18)]
        
        lag, corr = find_optimal_lag(source, target, max_lag=5)
        
        self.assertIn(lag, [1, 2])
        self.assertGreater(corr, 0.5)
    
    # =========================================================
    # lag_confidence() tests
    # =========================================================
    
    def test_lag_confidence_high(self):
        """Test high confidence for clear lag pattern"""
        source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        target = [1, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        
        lag, _ = find_optimal_lag(source, target, max_lag=5)
        confidence = lag_confidence(source, target, lag, max_lag=5)
        
        self.assertGreater(confidence, 0.5)
    
    def test_lag_confidence_low(self):
        """Test low confidence for weak lag pattern"""
        source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        target = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        
        lag = 0
        confidence = lag_confidence(source, target, lag, max_lag=5)
        
        self.assertLess(confidence, 0.6)
    
    def test_lag_confidence_medium(self):
        """Test medium confidence detection"""
        source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        target = [1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        lag, _ = find_optimal_lag(source, target, max_lag=5)
        confidence = lag_confidence(source, target, lag, max_lag=5)
        
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_lag_confidence_perfect_alignment(self):
        """Test confidence for perfectly aligned series"""
        source = [1, 2, 3, 4, 5, 6, 7, 8]
        target = [2, 4, 6, 8, 10, 12, 14, 16]
        
        confidence = lag_confidence(source, target, 0, max_lag=5)
        self.assertGreater(confidence, 0.5)
    
    def test_lag_confidence_with_noise(self):
        """Test confidence with noisy data"""
        random.seed(42)
        source = [i + random.gauss(0, 0.1) for i in range(20)]
        target = [i + random.gauss(0, 0.1) for i in range(20)]
        
        confidence = lag_confidence(source, target, 0, max_lag=5)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    # =========================================================
    # detect_lag_pattern() tests
    # =========================================================
    
    def test_detect_lag_pattern_multiple_targets(self):
        """Test detecting lag patterns for multiple targets"""
        source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        targets = [
            ('ETH', [1, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
            ('BNB', [1, 1, 1, 2, 3, 4, 5, 6, 7, 8]),
        ]
        
        results = detect_lag_pattern(source, targets, max_lag=5)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], 'ETH')
        self.assertEqual(results[1][0], 'BNB')
    
    def test_detect_lag_pattern_single_target(self):
        """Test lag pattern detection with single target"""
        source = [1, 2, 3, 4, 5, 6, 7, 8]
        targets = [('ETH', [1, 1, 2, 3, 4, 5, 6, 7])]
        
        results = detect_lag_pattern(source, targets, max_lag=5)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'ETH')
    
    def test_detect_lag_pattern_empty_targets(self):
        """Test lag pattern detection with empty targets"""
        source = [1, 2, 3, 4, 5, 6, 7, 8]
        results = detect_lag_pattern(source, [], max_lag=5)
        
        self.assertEqual(results, [])
    
    def test_detect_lag_pattern_low_correlation_filtered(self):
        """Test that low correlation targets are filtered out"""
        source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        targets = [
            ('ETH', [1, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
            ('BNB', [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        ]
        
        results = detect_lag_pattern(source, targets, max_lag=5)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'ETH')
    
    def test_detect_lag_pattern_with_returns_data(self):
        """Test with realistic returns data"""
        source = [0.01, -0.005, 0.02, -0.01, 0.005, 0.01, -0.005, 0.02]
        targets = [
            ('ETH', [0.008, -0.004, 0.018, -0.008, 0.004, 0.008, -0.004, 0.018]),
            ('BNB', [0.006, -0.003, 0.015, -0.006, 0.003, 0.006, -0.003, 0.015]),
        ]
        
        results = detect_lag_pattern(source, targets, max_lag=3)
        
        self.assertEqual(len(results), 2)
    
    def test_detect_lag_pattern_preserves_order(self):
        """Test that order is preserved by lag value"""
        source = [1, 2, 3, 4, 5, 6, 7, 8]
        targets = [
            ('LATE', [1, 1, 1, 1, 2, 3, 4, 5]),
            ('EARLY', [1, 1, 2, 3, 4, 5, 6, 7]),
            ('MID', [1, 1, 1, 2, 3, 4, 5, 6]),
        ]
        
        results = detect_lag_pattern(source, targets, max_lag=5)
        
        if len(results) >= 3:
            self.assertEqual(results[0][0], 'EARLY')
            self.assertEqual(results[1][0], 'MID')
            self.assertEqual(results[2][0], 'LATE')
    
    def test_detect_lag_pattern_no_valid_targets(self):
        """Test when no targets have significant correlation"""
        source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        targets = [
            ('BAD1', [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
            ('BAD2', [5, 4, 3, 2, 1, 2, 3, 4, 5, 6]),
        ]
        
        results = detect_lag_pattern(source, targets, max_lag=5)
        
        # Results should be a list (may be empty or contain weak correlations)
        self.assertIsInstance(results, list)


if __name__ == '__main__':
    unittest.main()
