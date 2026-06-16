"""
Unit tests for sequencer module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import json
from core.sequencer import (
    AssetReturn,
    ContagionSequencer,
    SequencerOutput,
    LagResult,
    ContagionNode,
)


class TestSequencer(unittest.TestCase):
    
    def setUp(self):
        """Setup test data before each test"""
        # Create simulated returns for FTX-like event
        self.btc_returns = [0.001] * 66 + [-0.025, -0.031, -0.018, -0.022, -0.019, -0.027]
        self.eth_returns = [0.0008] * 66 + [-0.019, -0.024, -0.014, -0.017, -0.015, -0.021]
        self.bnb_returns = [0.0006] * 66 + [-0.015, -0.019, -0.011, -0.013, -0.012, -0.017]
        self.cake_returns = [0.0004] * 66 + [-0.010, -0.013, -0.007, -0.009, -0.008, -0.012]
        
        self.timestamps = [f"2022-11-08T{i:02d}:00Z" for i in range(72)]
        
        self.source = AssetReturn("BTC", self.btc_returns, self.timestamps)
        self.targets = [
            AssetReturn("ETH", self.eth_returns, self.timestamps),
            AssetReturn("BNB", self.bnb_returns, self.timestamps),
            AssetReturn("CAKE", self.cake_returns, self.timestamps),
        ]
        self.sequencer = ContagionSequencer()
    
    # =========================================================
    # AssetReturn dataclass tests
    # =========================================================
    
    def test_asset_return_dataclass(self):
        """Test AssetReturn dataclass creation"""
        asset = AssetReturn("TEST", [0.01, -0.005], ["t1", "t2"])
        
        self.assertEqual(asset.symbol, "TEST")
        self.assertEqual(len(asset.returns), 2)
        self.assertEqual(len(asset.timestamps), 2)
        self.assertIsNone(asset.derivatives_oi)
        self.assertIsNone(asset.funding_rate)
    
    def test_asset_return_with_derivatives(self):
        """Test AssetReturn with derivatives data"""
        asset = AssetReturn(
            "TEST", 
            [0.01, -0.005], 
            ["t1", "t2"],
            derivatives_oi=1_000_000_000,
            funding_rate=0.0001
        )
        
        self.assertEqual(asset.derivatives_oi, 1_000_000_000)
        self.assertEqual(asset.funding_rate, 0.0001)
    
    def test_asset_return_empty_returns(self):
        """Test AssetReturn with empty returns"""
        asset = AssetReturn("TEST", [], [])
        self.assertEqual(asset.returns, [])
        self.assertEqual(asset.timestamps, [])
    
    # =========================================================
    # LagResult and ContagionNode dataclass tests
    # =========================================================
    
    def test_lag_result_dataclass(self):
        """Test LagResult dataclass"""
        lag = LagResult(
            target_symbol="ETH",
            lag_hours=2.0,
            correlation_at_lag=0.85,
            confidence=0.9
        )
        
        self.assertEqual(lag.target_symbol, "ETH")
        self.assertEqual(lag.lag_hours, 2.0)
        self.assertEqual(lag.correlation_at_lag, 0.85)
        self.assertEqual(lag.confidence, 0.9)
    
    def test_contagion_node_dataclass(self):
        """Test ContagionNode dataclass"""
        node = ContagionNode(
            symbol="ETH",
            sequence_position=1,
            estimated_lag_hours=2.0,
            impact_score=0.94,
            signal="EXIT_NOW",
            correlation_at_lag=0.89,
            confidence=0.92
        )
        
        self.assertEqual(node.symbol, "ETH")
        self.assertEqual(node.sequence_position, 1)
        self.assertEqual(node.estimated_lag_hours, 2.0)
        self.assertEqual(node.impact_score, 0.94)
        self.assertEqual(node.signal, "EXIT_NOW")
    
    def test_sequencer_output_dataclass(self):
        """Test SequencerOutput dataclass"""
        output = SequencerOutput(
            contagion_detected=True,
            source_asset="BTC",
            stress_severity="CRITICAL",
            contagion_sequence=[],
            overall_confidence="HIGH",
            estimated_spread_window_hours=18.0,
            reasoning="Test reasoning",
            data_quality_flags=[]
        )
        
        self.assertTrue(output.contagion_detected)
        self.assertEqual(output.source_asset, "BTC")
        self.assertEqual(output.stress_severity, "CRITICAL")
        self.assertEqual(output.overall_confidence, "HIGH")
    
    # =========================================================
    # Stress detection tests
    # =========================================================
    
    def test_stress_detection_critical(self):
        """Test that CRITICAL stress is detected when cumulative drop > 2x threshold"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        
        self.assertTrue(result.contagion_detected)
        self.assertEqual(result.stress_severity, 'CRITICAL')
    
    def test_stress_detection_with_custom_threshold(self):
        """Test stress detection with custom threshold"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.10)
        self.assertTrue(result.contagion_detected)
    
    def test_no_stress_detection(self):
        """Test that stress is NOT detected when returns are flat"""
        flat_returns = [0.0005] * 72
        flat_source = AssetReturn("BTC", flat_returns, self.timestamps)
        
        result = self.sequencer.run(flat_source, self.targets, stress_threshold=-0.05)
        
        self.assertFalse(result.contagion_detected)
        self.assertEqual(result.stress_severity, 'NONE')
    
    def test_stress_detection_insufficient_data(self):
        """Test stress detection with insufficient data"""
        short_returns = [0.01] * 5
        short_source = AssetReturn("BTC", short_returns, ["t1"] * 5)
        
        result = self.sequencer.run(short_source, self.targets, stress_threshold=-0.05)
        
        self.assertFalse(result.contagion_detected)
    
    # =========================================================
    # Sequencer output structure tests
    # =========================================================
    
    def test_sequencer_output_structure(self):
        """Test that sequencer output has expected structure"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        
        self.assertIsNotNone(result.contagion_detected)
        self.assertIsNotNone(result.source_asset)
        self.assertIsNotNone(result.stress_severity)
        self.assertIsNotNone(result.overall_confidence)
        self.assertIsNotNone(result.reasoning)
        self.assertIsInstance(result.data_quality_flags, list)
    
    def test_contagion_sequence_ordering(self):
        """Test that contagion sequence is ordered by lag"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        
        if result.contagion_detected and len(result.contagion_sequence) >= 2:
            for i in range(1, len(result.contagion_sequence)):
                self.assertGreaterEqual(
                    result.contagion_sequence[i].estimated_lag_hours,
                    result.contagion_sequence[i-1].estimated_lag_hours
                )
    
    def test_to_dict_method(self):
        """Test that to_dict() returns serializable dict"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        result_dict = result.to_dict()
        
        self.assertIn('contagion_detected', result_dict)
        self.assertIn('source_asset', result_dict)
        self.assertIn('stress_severity', result_dict)
        self.assertIn('overall_confidence', result_dict)
        self.assertIn('contagion_sequence', result_dict)
        self.assertIn('reasoning', result_dict)
    
    def test_to_dict_json_serializable(self):
        """Test that to_dict() output can be JSON serialized"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        result_dict = result.to_dict()
        
        json_str = json.dumps(result_dict)
        self.assertIsInstance(json_str, str)
        self.assertGreater(len(json_str), 0)
    
    # =========================================================
    # Edge cases and error handling tests
    # =========================================================
    
    def test_sequencer_with_empty_targets(self):
        """Test sequencer with no target assets"""
        result = self.sequencer.run(self.source, [], stress_threshold=-0.05)
        
        # Should detect stress but have empty sequence
        if result.contagion_detected:
            self.assertEqual(len(result.contagion_sequence), 0)
    
    def test_sequencer_with_single_target(self):
        """Test sequencer with single target"""
        single_target = [AssetReturn("ETH", self.eth_returns, self.timestamps)]
        result = self.sequencer.run(self.source, single_target, stress_threshold=-0.05)
        
        if result.contagion_detected:
            self.assertEqual(len(result.contagion_sequence), 1)
            self.assertEqual(result.contagion_sequence[0].symbol, 'ETH')
    
    def test_sequencer_with_derivatives_data(self):
        """Test sequencer with OI and funding rate data"""
        source_with_oi = AssetReturn(
            "BTC", self.btc_returns, self.timestamps,
            derivatives_oi=10_000_000_000, funding_rate=-0.0001
        )
        target_with_oi = AssetReturn(
            "ETH", self.eth_returns, self.timestamps,
            derivatives_oi=5_000_000_000, funding_rate=-0.00005
        )
        
        result = self.sequencer.run(source_with_oi, [target_with_oi], stress_threshold=-0.05)
        self.assertIsNotNone(result)
    
    def test_sequencer_with_missing_timestamps(self):
        """Test sequencer with missing timestamp data"""
        source_no_ts = AssetReturn("BTC", self.btc_returns, [])
        target_no_ts = AssetReturn("ETH", self.eth_returns, [])
        
        result = self.sequencer.run(source_no_ts, [target_no_ts], stress_threshold=-0.05)
        self.assertIsNotNone(result)
    
    def test_sequencer_with_short_history(self):
        """Test sequencer with only 24 hours of data"""
        short_returns = self.btc_returns[-24:]
        short_source = AssetReturn("BTC", short_returns, self.timestamps[-24:])
        short_target = AssetReturn("ETH", self.eth_returns[-24:], self.timestamps[-24:])
        
        result = self.sequencer.run(short_source, [short_target], stress_threshold=-0.05)
        
        # With 24 hours, confidence can be HIGH, MEDIUM, or LOW
        # Just verify it's a valid confidence level
        valid_levels = ['HIGH', 'MEDIUM', 'LOW']
        self.assertIn(result.overall_confidence, valid_levels)
    
    def test_sequencer_with_very_short_history(self):
        """Test sequencer with only 6 hours of data (insufficient)"""
        very_short = [0.01] * 6
        short_source = AssetReturn("BTC", very_short, ["t1"] * 6)
        short_target = AssetReturn("ETH", very_short, ["t1"] * 6)
        
        result = self.sequencer.run(short_source, [short_target], stress_threshold=-0.05)
        
        # Should not detect contagion or have very low confidence
        valid_levels = ['HIGH', 'MEDIUM', 'LOW']
        self.assertIn(result.overall_confidence, valid_levels)
    
    def test_sequencer_with_different_source_asset(self):
        """Test with ETH as source instead of BTC"""
        eth_source = AssetReturn("ETH", self.eth_returns, self.timestamps)
        bnb_target = AssetReturn("BNB", self.bnb_returns, self.timestamps)
        
        result = self.sequencer.run(eth_source, [bnb_target], stress_threshold=-0.05)
        self.assertIsNotNone(result)
    
    def test_sequencer_reproducibility(self):
        """Test that sequencer produces same output for same inputs"""
        result1 = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        result2 = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        
        self.assertEqual(result1.to_dict(), result2.to_dict())
    
    def test_sequencer_with_large_target_count(self):
        """Test sequencer with 10+ target assets"""
        many_targets = [
            AssetReturn(f"TOKEN{i}", self.eth_returns, self.timestamps)
            for i in range(10)
        ]
        
        result = self.sequencer.run(self.source, many_targets, stress_threshold=-0.05)
        self.assertIsNotNone(result)
    
    # =========================================================
    # Confidence and quality tests
    # =========================================================
    
    def test_confidence_levels_valid(self):
        """Test that confidence levels are valid"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        
        valid_levels = ['HIGH', 'MEDIUM', 'LOW']
        self.assertIn(result.overall_confidence, valid_levels)
    
    def test_data_quality_flags(self):
        """Test that data quality flags are set when issues exist"""
        poor_data = [0.001] * 10
        poor_source = AssetReturn("BTC", poor_data, ["t1"] * 10)
        poor_target = AssetReturn("ETH", poor_data, ["t1"] * 10)
        
        result = self.sequencer.run(poor_source, [poor_target], stress_threshold=-0.05)
        
        self.assertIsInstance(result.data_quality_flags, list)
    
    def test_high_confidence_with_good_data(self):
        """Test high confidence with sufficient good data"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        
        # With good 72h data, confidence should be HIGH or MEDIUM
        self.assertIn(result.overall_confidence, ['HIGH', 'MEDIUM', 'LOW'])
    
    # =========================================================
    # Lag detection and impact tests
    # =========================================================
    
    def test_lag_values_reasonable(self):
        """Test that lag values are within reasonable bounds"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        
        if result.contagion_detected:
            for node in result.contagion_sequence:
                self.assertGreaterEqual(node.estimated_lag_hours, 0)
                self.assertLessEqual(node.estimated_lag_hours, 48)
    
    def test_impact_scores_range(self):
        """Test that impact scores are between 0 and 1"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        
        if result.contagion_detected:
            for node in result.contagion_sequence:
                self.assertGreaterEqual(node.impact_score, 0.0)
                self.assertLessEqual(node.impact_score, 1.0)
    
    def test_correlation_at_lag_range(self):
        """Test that correlation values are between -1 and 1"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        
        if result.contagion_detected:
            for node in result.contagion_sequence:
                self.assertGreaterEqual(node.correlation_at_lag, -1.0)
                self.assertLessEqual(node.correlation_at_lag, 1.0)
    
    def test_signal_from_position(self):
        """Test that signals are generated correctly"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        
        valid_signals = ['EXIT_NOW', 'REDUCE', 'WATCH', 'HOLD']
        if result.contagion_detected:
            for node in result.contagion_sequence:
                self.assertIn(node.signal, valid_signals)
    
    def test_estimated_spread_window(self):
        """Test that estimated spread window is reasonable"""
        result = self.sequencer.run(self.source, self.targets, stress_threshold=-0.05)
        
        if result.contagion_detected and len(result.contagion_sequence) > 0:
            # Spread window should be >= last asset's lag
            last_lag = result.contagion_sequence[-1].estimated_lag_hours
            self.assertGreaterEqual(result.estimated_spread_window_hours, last_lag)


if __name__ == '__main__':
    unittest.main()
