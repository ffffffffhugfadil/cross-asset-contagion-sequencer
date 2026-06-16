"""
Unit tests for correlation module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
from core.correlation import (
    pearson_correlation,
    rolling_correlation,
    correlation_matrix,
    correlation_trend,
    is_contagion_correlation,
)


class TestCorrelation(unittest.TestCase):
    
    # =========================================================
    # pearson_correlation() tests
    # =========================================================
    
    def test_pearson_correlation_perfect_positive(self):
        """Test perfect positive correlation (r = 1.0)"""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        result = pearson_correlation(x, y)
        self.assertAlmostEqual(result, 1.0, places=5)
    
    def test_pearson_correlation_perfect_negative(self):
        """Test perfect negative correlation (r = -1.0)"""
        x = [1, 2, 3, 4, 5]
        y = [10, 8, 6, 4, 2]
        result = pearson_correlation(x, y)
        self.assertAlmostEqual(result, -1.0, places=5)
    
    def test_pearson_correlation_zero(self):
        """Test zero correlation"""
        x = [1, 2, 3, 4, 5]
        y = [1, 2, 1, 2, 1]
        result = pearson_correlation(x, y)
        # Zero correlation should be close to 0
        self.assertAlmostEqual(result, 0.0, places=1)
    
    def test_pearson_correlation_insufficient_data(self):
        """Test with insufficient data points (< 3)"""
        x = [1, 2]
        y = [2, 4]
        result = pearson_correlation(x, y)
        self.assertEqual(result, 0.0)
    
    def test_pearson_correlation_single_element(self):
        """Test with single element"""
        x = [1.0]
        y = [2.0]
        result = pearson_correlation(x, y)
        self.assertEqual(result, 0.0)
    
    def test_pearson_correlation_zero_variance_x(self):
        """Test with zero variance in x (constant series)"""
        x = [1, 1, 1, 1, 1]
        y = [2, 4, 6, 8, 10]
        result = pearson_correlation(x, y)
        self.assertEqual(result, 0.0)
    
    def test_pearson_correlation_zero_variance_y(self):
        """Test with zero variance in y (constant series)"""
        x = [1, 2, 3, 4, 5]
        y = [3, 3, 3, 3, 3]
        result = pearson_correlation(x, y)
        self.assertEqual(result, 0.0)
    
    def test_pearson_correlation_with_negative_values(self):
        """Test correlation with negative values"""
        x = [-5, -4, -3, -2, -1]
        y = [-10, -8, -6, -4, -2]
        result = pearson_correlation(x, y)
        self.assertAlmostEqual(result, 1.0, places=5)
    
    def test_pearson_correlation_with_mixed_sign(self):
        """Test correlation with mixed positive/negative"""
        x = [-2, -1, 0, 1, 2]
        y = [4, 1, 0, 1, 4]
        result = pearson_correlation(x, y)
        # This is a parabolic relationship, correlation should be >= 0
        self.assertGreaterEqual(result, 0.0)
    
    def test_pearson_correlation_with_large_values(self):
        """Test correlation with large numerical values"""
        x = [1e6, 2e6, 3e6, 4e6, 5e6]
        y = [2e6, 4e6, 6e6, 8e6, 10e6]
        result = pearson_correlation(x, y)
        self.assertAlmostEqual(result, 1.0, places=5)
    
    def test_pearson_correlation_with_small_values(self):
        """Test correlation with very small values"""
        x = [1e-6, 2e-6, 3e-6, 4e-6, 5e-6]
        y = [2e-6, 4e-6, 6e-6, 8e-6, 10e-6]
        result = pearson_correlation(x, y)
        self.assertAlmostEqual(result, 1.0, places=5)
    
    def test_pearson_correlation_with_decimal_values(self):
        """Test correlation with decimal values"""
        x = [0.1, 0.2, 0.3, 0.4, 0.5]
        y = [0.2, 0.4, 0.6, 0.8, 1.0]
        result = pearson_correlation(x, y)
        self.assertAlmostEqual(result, 1.0, places=5)
    
    def test_pearson_correlation_symmetry(self):
        """Test that correlation is symmetric"""
        x = [1, 2, 3, 4, 5]
        y = [5, 4, 3, 2, 1]
        r1 = pearson_correlation(x, y)
        r2 = pearson_correlation(y, x)
        self.assertAlmostEqual(r1, r2, places=5)
    
    def test_pearson_correlation_highly_correlated(self):
        """Test highly correlated but not perfect"""
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1, 9.1, 10.1]
        result = pearson_correlation(x, y)
        self.assertGreater(result, 0.99)
    
    def test_pearson_correlation_weak_positive(self):
        """Test weak positive correlation"""
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        result = pearson_correlation(x, y)
        self.assertGreater(result, 0.9)
    
    # =========================================================
    # rolling_correlation() tests
    # =========================================================
    
    def test_rolling_correlation_basic(self):
        """Test basic rolling correlation calculation"""
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        
        results = rolling_correlation(x, y, window_hours=5, step_hours=1)
        
        self.assertTrue(len(results) > 0)
        for r in results:
            self.assertIn('window_start_index', r)
            self.assertIn('window_end_index', r)
            self.assertIn('correlation', r)
            self.assertAlmostEqual(r['correlation'], 1.0, places=5)
    
    def test_rolling_correlation_step_2(self):
        """Test rolling correlation with step=2"""
        x = list(range(20))
        y = list(range(20))
        results = rolling_correlation(x, y, window_hours=10, step_hours=2)
        
        self.assertTrue(len(results) > 0)
        for r in results:
            self.assertAlmostEqual(r['correlation'], 1.0, places=5)
    
    def test_rolling_correlation_insufficient_data(self):
        """Test rolling correlation with insufficient data"""
        x = [1, 2, 3]
        y = [2, 4, 6]
        results = rolling_correlation(x, y, window_hours=5)
        self.assertEqual(results, [])
    
    def test_rolling_correlation_window_equal_data(self):
        """Test when window equals data length"""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        results = rolling_correlation(x, y, window_hours=5, step_hours=1)
        self.assertEqual(len(results), 1)
    
    def test_rolling_correlation_window_larger_than_data(self):
        """Test when window is larger than data"""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        results = rolling_correlation(x, y, window_hours=10)
        self.assertEqual(results, [])
    
    def test_rolling_correlation_negative_correlation(self):
        """Test rolling correlation with negative correlation"""
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        
        results = rolling_correlation(x, y, window_hours=5, step_hours=5)
        for r in results:
            self.assertLessEqual(r['correlation'], -0.9)
    
    def test_rolling_correlation_random_data(self):
        """Test rolling correlation with random data"""
        np.random.seed(42)
        x = np.random.randn(50).tolist()
        y = np.random.randn(50).tolist()
        
        results = rolling_correlation(x, y, window_hours=10, step_hours=5)
        self.assertTrue(len(results) > 0)
    
    # =========================================================
    # correlation_matrix() tests
    # =========================================================
    
    def test_correlation_matrix_basic(self):
        """Test correlation matrix generation"""
        source_returns = [0.01, -0.005, 0.02, -0.01, 0.005]
        targets_returns = {
            'ETH': [0.008, -0.004, 0.018, -0.008, 0.004],
            'BNB': [0.006, -0.003, 0.015, -0.006, 0.003],
        }
        
        result = correlation_matrix(source_returns, targets_returns, window_hours=5)
        
        self.assertIn('ETH', result)
        self.assertIn('BNB', result)
        self.assertGreater(result['ETH'], 0.9)
        self.assertGreater(result['BNB'], 0.9)
    
    def test_correlation_matrix_empty_targets(self):
        """Test correlation matrix with empty targets"""
        source = [1, 2, 3, 4, 5]
        result = correlation_matrix(source, {}, window_hours=3)
        self.assertEqual(result, {})
    
    def test_correlation_matrix_insufficient_window(self):
        """Test correlation matrix with window larger than data"""
        source = [1, 2, 3]
        targets = {'ETH': [1, 2, 3]}
        result = correlation_matrix(source, targets, window_hours=10)
        self.assertEqual(result, {})
    
    def test_correlation_matrix_target_insufficient_data(self):
        """Test when target has insufficient data"""
        source = [1, 2, 3, 4, 5]
        targets = {'ETH': [1, 2]}
        result = correlation_matrix(source, targets, window_hours=3)
        self.assertEqual(result['ETH'], 0.0)
    
    def test_correlation_matrix_multiple_targets(self):
        """Test correlation matrix with many targets"""
        source = [0.01, -0.005, 0.02, -0.01, 0.005, 0.01, -0.005, 0.02]
        targets = {
            'ETH': [0.008, -0.004, 0.018, -0.008, 0.004, 0.008, -0.004, 0.018],
            'BNB': [0.006, -0.003, 0.015, -0.006, 0.003, 0.006, -0.003, 0.015],
            'CAKE': [0.004, -0.002, 0.010, -0.004, 0.002, 0.004, -0.002, 0.010],
            'LINK': [0.003, -0.001, 0.008, -0.003, 0.001, 0.003, -0.001, 0.008],
        }
        
        result = correlation_matrix(source, targets, window_hours=8)
        
        self.assertEqual(len(result), 4)
        for symbol, corr in result.items():
            self.assertGreater(corr, 0.9)
    
    # =========================================================
    # correlation_trend() tests
    # =========================================================
    
    def test_correlation_trend_increasing(self):
        """Test detection of increasing correlation trend"""
        source = [0.01, -0.005, 0.02, -0.01, 0.005, 0.01, -0.005, 0.02, 0.015, -0.008]
        target = [0.005, -0.002, 0.01, -0.005, 0.008, 0.009, -0.004, 0.018, 0.014, -0.007]
        
        trend = correlation_trend(source, target, window_hours=4, lookback_windows=2)
        self.assertIn(trend, ['increasing', 'stable'])
    
    def test_correlation_trend_decreasing(self):
        """Test detection of decreasing correlation trend"""
        source = [0.01, -0.005, 0.02, -0.01, 0.005, 0.01, -0.005, 0.02]
        target = [0.009, -0.004, 0.018, -0.008, 0.003, 0.005, -0.008, 0.010]
        
        trend = correlation_trend(source, target, window_hours=4, lookback_windows=2)
        self.assertIn(trend, ['decreasing', 'stable'])
    
    def test_correlation_trend_stable(self):
        """Test stable correlation detection"""
        source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        target = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        
        trend = correlation_trend(source, target, window_hours=4, lookback_windows=3)
        self.assertEqual(trend, 'stable')
    
    def test_correlation_trend_insufficient_data(self):
        """Test with insufficient data for trend detection"""
        source = [1, 2, 3, 4]
        target = [2, 4, 6, 8]
        
        trend = correlation_trend(source, target, window_hours=4, lookback_windows=3)
        self.assertEqual(trend, 'stable')
    
    # =========================================================
    # is_contagion_correlation() tests
    # =========================================================
    
    def test_is_contagion_correlation_true(self):
        """Test strong correlation triggers contagion flag"""
        self.assertTrue(is_contagion_correlation(0.85, threshold=0.6))
        self.assertTrue(is_contagion_correlation(0.75, threshold=0.6))
        self.assertTrue(is_contagion_correlation(1.0, threshold=0.6))
    
    def test_is_contagion_correlation_false(self):
        """Test weak correlation does not trigger contagion flag"""
        self.assertFalse(is_contagion_correlation(0.35, threshold=0.6))
        self.assertFalse(is_contagion_correlation(0.1, threshold=0.6))
        self.assertFalse(is_contagion_correlation(0.0, threshold=0.6))
        self.assertFalse(is_contagion_correlation(-0.5, threshold=0.6))
    
    def test_is_contagion_correlation_boundary(self):
        """Test at exact threshold"""
        self.assertTrue(is_contagion_correlation(0.6, threshold=0.6))
        self.assertFalse(is_contagion_correlation(0.59, threshold=0.6))
    
    def test_is_contagion_correlation_custom_threshold(self):
        """Test with custom threshold values"""
        self.assertTrue(is_contagion_correlation(0.5, threshold=0.5))
        self.assertFalse(is_contagion_correlation(0.49, threshold=0.5))
        self.assertTrue(is_contagion_correlation(0.8, threshold=0.7))
        self.assertFalse(is_contagion_correlation(0.65, threshold=0.7))


if __name__ == '__main__':
    unittest.main()
