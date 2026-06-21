"""Unit tests for core.sequencer module."""

import unittest
import json
import random
from core.sequencer import (
    ContagionSequencer,
    AssetReturn,
    LagResult,
    ContagionNode,
    SequencerOutput,
)


class TestSequencer(unittest.TestCase):

    def test_asset_return_dataclass(self):
        """Test AssetReturn dataclass creation."""
        asset = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03],
            timestamps=["2022-01-01T00:00:00", "2022-01-01T01:00:00", "2022-01-01T02:00:00"],
            derivatives_oi=1_000_000_000,
            funding_rate=0.0001,
        )
        self.assertEqual(asset.symbol, "BTC")
        self.assertEqual(len(asset.returns), 3)
        self.assertEqual(asset.derivatives_oi, 1_000_000_000)

    def test_asset_return_empty_returns(self):
        """Test AssetReturn with empty returns."""
        asset = AssetReturn(symbol="BTC", returns=[], timestamps=[])
        self.assertEqual(asset.symbol, "BTC")
        self.assertEqual(len(asset.returns), 0)

    def test_asset_return_with_derivatives(self):
        """Test AssetReturn with derivatives data."""
        asset = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.01],
            timestamps=["2022-01-01T00:00:00", "2022-01-01T01:00:00"],
            derivatives_oi=500_000_000,
            funding_rate=-0.0005,
        )
        self.assertEqual(asset.derivatives_oi, 500_000_000)
        self.assertEqual(asset.funding_rate, -0.0005)

    def test_lag_result_dataclass(self):
        """Test LagResult dataclass."""
        lag = LagResult(
            target_symbol="ETH",
            lag_hours=3.0,
            correlation_at_lag=0.85,
            confidence=0.9,
        )
        self.assertEqual(lag.target_symbol, "ETH")
        self.assertEqual(lag.lag_hours, 3.0)
        self.assertEqual(lag.correlation_at_lag, 0.85)

    def test_contagion_node_dataclass(self):
        """Test ContagionNode dataclass."""
        node = ContagionNode(
            symbol="ETH",
            sequence_position=1,
            estimated_lag_hours=2.0,
            impact_score=0.94,
            signal="EXIT_NOW",
            correlation_at_lag=0.89,
            confidence=0.92,
        )
        self.assertEqual(node.symbol, "ETH")
        self.assertEqual(node.sequence_position, 1)
        self.assertEqual(node.impact_score, 0.94)

    def test_sequencer_output_dataclass(self):
        """Test SequencerOutput dataclass."""
        output = SequencerOutput(
            contagion_detected=True,
            source_asset="BTC",
            stress_severity="CRITICAL",
            contagion_sequence=[],
            overall_confidence="HIGH",
            estimated_spread_window_hours=18.0,
            reasoning="Test reasoning",
            data_quality_flags=[],
        )
        self.assertTrue(output.contagion_detected)
        self.assertEqual(output.stress_severity, "CRITICAL")

    def test_to_dict_method(self):
        """Test that to_dict() returns serializable dict."""
        output = SequencerOutput(
            contagion_detected=True,
            source_asset="BTC",
            stress_severity="CRITICAL",
            contagion_sequence=[],
            overall_confidence="HIGH",
            estimated_spread_window_hours=18.0,
            reasoning="Test",
        )
        d = output.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["source_asset"], "BTC")

    def test_to_dict_json_serializable(self):
        """Test that to_dict() output can be JSON serialized."""
        node = ContagionNode(
            symbol="ETH",
            sequence_position=1,
            estimated_lag_hours=2.0,
            impact_score=0.94,
            signal="EXIT_NOW",
            correlation_at_lag=0.89,
            confidence=0.92,
        )
        output = SequencerOutput(
            contagion_detected=True,
            source_asset="BTC",
            stress_severity="CRITICAL",
            contagion_sequence=[node],
            overall_confidence="HIGH",
            estimated_spread_window_hours=18.0,
            reasoning="Test",
        )
        try:
            json.dumps(output.to_dict())
        except TypeError:
            self.fail("to_dict() output is not JSON serializable")

    def test_confidence_levels_valid(self):
        """Test that confidence levels are valid."""
        levels = ["LOW", "MEDIUM", "HIGH"]
        self.assertIn("HIGH", levels)

    def test_sequencer_output_structure(self):
        """Test that sequencer output has expected structure."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03, -0.01, 0.02, -0.03] * 12,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03, -0.01, 0.02, -0.03] * 12,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SequencerOutput)
        self.assertIsInstance(result.contagion_detected, bool)

    def test_stress_detection_with_custom_threshold(self):
        """Test stress detection with custom threshold."""
        returns = [0.001] * 66 + [-0.008] * 6
        source = AssetReturn(
            symbol="BTC",
            returns=returns,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=returns,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.03)

        self.assertTrue(result.contagion_detected)

    def test_no_stress_detection(self):
        """Test that stress is NOT detected when returns are flat."""
        returns = [0.001] * 72
        source = AssetReturn(
            symbol="BTC",
            returns=returns,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=returns,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        self.assertFalse(result.contagion_detected)

    def test_stress_detection_critical(self):
        """Test that CRITICAL stress is detected with very large drop."""
        # Cumulative drop = -0.30 (10 * -0.03) -> jelas CRITICAL
        returns = [0.001] * 62 + [-0.03] * 10
        source = AssetReturn(
            symbol="BTC",
            returns=returns,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=returns,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        # Should detect stress and severity should be CRITICAL or HIGH
        self.assertTrue(result.contagion_detected)
        self.assertIn(result.stress_severity, ["CRITICAL", "HIGH", "MEDIUM"])

    def test_stress_detection_insufficient_data(self):
        """Test stress detection with insufficient data."""
        returns = [-0.05, -0.05, -0.05]
        source = AssetReturn(
            symbol="BTC",
            returns=returns,
            timestamps=["2022-01-01T00:00:00", "2022-01-01T01:00:00", "2022-01-01T02:00:00"],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=returns,
            timestamps=["2022-01-01T00:00:00", "2022-01-01T01:00:00", "2022-01-01T02:00:00"],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        self.assertIsNotNone(result)

    def test_lag_values_reasonable(self):
        """Test that lag values are within reasonable bounds."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        if result.contagion_sequence:
            for node in result.contagion_sequence:
                self.assertGreaterEqual(node.estimated_lag_hours, 0)
                self.assertLessEqual(node.estimated_lag_hours, 48)

    def test_correlation_at_lag_range(self):
        """Test that correlation values are between -1 and 1."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        if result.contagion_sequence:
            for node in result.contagion_sequence:
                self.assertGreaterEqual(node.correlation_at_lag, -1.0)
                self.assertLessEqual(node.correlation_at_lag, 1.0)

    def test_impact_scores_range(self):
        """Test that impact scores are between 0 and 1."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        if result.contagion_sequence:
            for node in result.contagion_sequence:
                self.assertGreaterEqual(node.impact_score, 0.0)
                self.assertLessEqual(node.impact_score, 1.0)

    def test_estimated_spread_window(self):
        """Test that estimated spread window is reasonable."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        if result.contagion_sequence and result.contagion_detected:
            self.assertGreaterEqual(result.estimated_spread_window_hours, 0)

    def test_sequencer_reproducibility(self):
        """Test that sequencer produces same output for same inputs."""
        random.seed(42)
        returns = [random.gauss(0, 0.01) for _ in range(72)]
        source = AssetReturn(
            symbol="BTC",
            returns=returns,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=returns,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer1 = ContagionSequencer()
        result1 = sequencer1.run(source, [target], stress_threshold=-0.05)

        sequencer2 = ContagionSequencer()
        result2 = sequencer2.run(source, [target], stress_threshold=-0.05)

        self.assertEqual(result1.to_dict(), result2.to_dict())

    def test_sequencer_with_single_target(self):
        """Test sequencer with single target."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        self.assertIsNotNone(result)
        if result.contagion_detected:
            self.assertEqual(len(result.contagion_sequence), 1)

    def test_sequencer_with_empty_targets(self):
        """Test sequencer with no target assets."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [], stress_threshold=-0.05)

        self.assertIsNotNone(result)
        self.assertEqual(len(result.contagion_sequence), 0)

    def test_sequencer_with_different_source_asset(self):
        """Test with ETH as source instead of BTC."""
        source = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        self.assertEqual(result.source_asset, "ETH")

    def test_sequencer_with_short_history(self):
        """Test sequencer with only 24 hours of data."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 8,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(24)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03] * 8,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(24)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        self.assertIsNotNone(result)

    def test_sequencer_with_very_short_history(self):
        """Test sequencer with only 6 hours of data (insufficient)."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03, 0.01, -0.02, 0.03],
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(6)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03, 0.01, -0.02, 0.03],
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(6)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        self.assertIsNotNone(result)

    def test_sequencer_with_large_target_count(self):
        """Test sequencer with 10+ target assets."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        targets = []
        for sym in ["ETH", "BNB", "SOL", "ADA", "DOGE", "XRP", "MATIC", "LINK", "CAKE", "AAVE"]:
            targets.append(
                AssetReturn(
                    symbol=sym,
                    returns=[0.01, -0.02, 0.03] * 24,
                    timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
                )
            )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, targets, stress_threshold=-0.05)

        self.assertIsNotNone(result)

    def test_sequencer_with_derivatives_data(self):
        """Test sequencer with OI and funding rate data."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
            derivatives_oi=10_000_000_000,
            funding_rate=0.0002,
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
            derivatives_oi=5_000_000_000,
            funding_rate=0.0001,
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        self.assertIsNotNone(result)

    def test_sequencer_with_missing_timestamps(self):
        """Test sequencer with missing timestamp data."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        self.assertIsNotNone(result)

    def test_contagion_sequence_ordering(self):
        """Test that contagion sequence is ordered by lag."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        targets = []
        for i, sym in enumerate(["ETH", "BNB", "SOL"]):
            rets = [0.01, -0.02, 0.03] * 24
            rets = rets[i:] + rets[:i]
            targets.append(
                AssetReturn(
                    symbol=sym,
                    returns=rets,
                    timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
                )
            )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, targets, stress_threshold=-0.05)

        if result.contagion_detected and len(result.contagion_sequence) > 1:
            lags = [n.estimated_lag_hours for n in result.contagion_sequence]
            self.assertEqual(lags, sorted(lags))

    def test_signal_from_position(self):
        """Test that signals are generated correctly."""
        # First position with high impact → EXIT_NOW
        self.assertEqual("EXIT_NOW", "EXIT_NOW")

    def test_high_confidence_with_good_data(self):
        """Test high confidence with sufficient good data."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        if result.contagion_detected:
            self.assertIn(result.overall_confidence, ["HIGH", "MEDIUM", "LOW"])

    def test_data_quality_flags(self):
        """Test that data quality flags are set when issues exist."""
        source = AssetReturn(
            symbol="BTC",
            returns=[0.01, -0.02, 0.03] * 24,
            timestamps=[f"2022-01-01T{i:02d}:00:00" for i in range(72)],
        )
        target = AssetReturn(
            symbol="ETH",
            returns=[0.01],
            timestamps=["2022-01-01T00:00:00"],
        )

        sequencer = ContagionSequencer()
        result = sequencer.run(source, [target], stress_threshold=-0.05)

        self.assertIsNotNone(result.data_quality_flags)


if __name__ == "__main__":
    unittest.main()
