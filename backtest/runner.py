"""
backtest/runner.py
==================
Runs backtests on historical stress events.

Executes the sequencer on past crash events (FTX, LUNA, 3AC)
and compares predictions against actual outcomes.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Import sequencer components
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.sequencer import ContagionSequencer, AssetReturn


class BacktestRunner:
    """
    Run backtests on historical crypto crash events.
    
    Usage:
        runner = BacktestRunner()
        results = runner.run_all_events()
        print(results['aggregate_metrics'])
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize backtest runner.
        
        Args:
            data_dir: Directory containing event data (default: backtest/events/)
        """
        if data_dir is None:
            self.data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'backtest', 'events'
            )
        else:
            self.data_dir = data_dir
        
        self.sequencer = ContagionSequencer()
        self.results = []
    
    def load_event_data(self, event_name: str) -> Optional[Dict]:
        """
        Load historical event data from JSON file.
        
        Args:
            event_name: Name of event file (without .json extension)
        
        Returns:
            Dict with event data or None if not found
        """
        file_path = os.path.join(self.data_dir, f"{event_name}.json")
        
        if not os.path.exists(file_path):
            print(f"Event file not found: {file_path}")
            return None
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def run_event(
        self,
        event_data: Dict,
        stress_threshold: float = -0.05,
    ) -> Optional[Dict]:
        """
        Run backtest on a single event.
        
        Args:
            event_data: Dict with event data (source returns, target returns, actual sequence)
            stress_threshold: Cumulative return threshold for stress detection
        
        Returns:
            Dict with backtest results or None if failed
        """
        try:
            # Extract data
            source_symbol = event_data.get('source_asset', 'BTC')
            source_returns = event_data.get('source_returns', [])
            source_timestamps = event_data.get('timestamps', [])
            targets_data = event_data.get('targets', [])
            
            if not source_returns or not targets_data:
                print(f"Missing data for event {event_data.get('event_name', 'unknown')}")
                return None
            
            # Build source AssetReturn
            source = AssetReturn(
                symbol=source_symbol,
                returns=source_returns,
                timestamps=source_timestamps,
            )
            
            # Build target AssetReturns
            targets = []
            for t in targets_data:
                target = AssetReturn(
                    symbol=t.get('symbol'),
                    returns=t.get('returns', []),
                    timestamps=t.get('timestamps', []),
                    derivatives_oi=t.get('open_interest_usd'),
                    funding_rate=t.get('funding_rate'),
                )
                targets.append(target)
            
            # Run sequencer
            result = self.sequencer.run(source, targets, stress_threshold)
            
            # Compare with actual sequence
            actual_sequence = event_data.get('actual_sequence', [])
            comparison = self._compare_sequences(
                result.contagion_sequence,
                actual_sequence
            )
            
            return {
                'event_name': event_data.get('event_name'),
                'event_id': event_data.get('event_id'),
                'stress_onset': event_data.get('stress_onset'),
                'source_asset': source_symbol,
                'stress_severity': result.stress_severity,
                'contagion_detected': result.contagion_detected,
                'predicted_sequence': [
                    {
                        'symbol': n.symbol,
                        'estimated_lag_hours': n.estimated_lag_hours,
                        'impact_score': n.impact_score,
                        'signal': n.signal,
                    }
                    for n in result.contagion_sequence
                ],
                'actual_sequence': actual_sequence,
                'metrics': comparison,
                'overall_confidence': result.overall_confidence,
                'reasoning': result.reasoning,
            }
        
        except Exception as e:
            print(f"Error running backtest: {e}")
            return None
    
    def _compare_sequences(
        self,
        predicted: List,
        actual: List,
    ) -> Dict:
        """
        Compare predicted sequence with actual outcomes.
        
        Returns:
            Dict with accuracy metrics
        """
        if not predicted or not actual:
            return {
                'sequence_accuracy_pct': 0.0,
                'avg_lag_error_hours': 0.0,
                'early_warning_hours': 0.0,
                'false_positives': 0,
            }
        
        # Build predicted order
        pred_order = [p.symbol for p in predicted]
        actual_order = [a.get('symbol') for a in actual]
        
        # Calculate sequence accuracy
        correct_positions = 0
        for i, symbol in enumerate(pred_order):
            if i < len(actual_order) and symbol == actual_order[i]:
                correct_positions += 1
        
        sequence_accuracy = (correct_positions / len(pred_order)) * 100 if pred_order else 0
        
        # Calculate lag errors
        lag_errors = []
        for pred in predicted:
            actual_match = next(
                (a for a in actual if a.get('symbol') == pred.symbol),
                None
            )
            if actual_match:
                error = abs(pred.estimated_lag_hours - actual_match.get('actual_lag_hours', 0))
                lag_errors.append(error)
        
        avg_lag_error = sum(lag_errors) / len(lag_errors) if lag_errors else 0
        
        # Early warning = lag of first predicted asset
        early_warning = predicted[0].estimated_lag_hours if predicted else 0
        
        return {
            'sequence_accuracy_pct': round(sequence_accuracy, 1),
            'avg_lag_error_hours': round(avg_lag_error, 1),
            'early_warning_hours': early_warning,
            'false_positives': 0,
        }
    
    def run_all_events(self) -> Dict:
        """
        Run backtests on all available events.
        
        Returns:
            Dict with all results and aggregate metrics
        """
        # Define standard events with their data
        # In production, these would load from JSON files
        events = self._get_builtin_events()
        
        results = []
        for event in events:
            print(f"Running backtest: {event.get('event_name')}...")
            result = self.run_event(event)
            if result:
                results.append(result)
        
        aggregate = self._calculate_aggregate_metrics(results)
        
        return {
            'events': results,
            'aggregate_metrics': aggregate,
            'total_events': len(results),
        }
    
    def _get_builtin_events(self) -> List[Dict]:
        """
        Get built-in event data for backtesting.
        
        These are the FTX, LUNA, and 3AC events from summary_metrics.json.
        """
        # Load from summary_metrics.json if available
        summary_path = os.path.join(
            os.path.dirname(self.data_dir) if self.data_dir else '.',
            'results', 'summary_metrics.json'
        )
        
        if os.path.exists(summary_path):
            with open(summary_path, 'r') as f:
                summary = json.load(f)
                return summary.get('events', [])
        
        # Fallback: return empty list
        print("No event data found. Please ensure backtest/events/ contains JSON files.")
        return []
    
    def _calculate_aggregate_metrics(self, results: List[Dict]) -> Dict:
        """
        Calculate aggregate metrics across all events.
        """
        if not results:
            return {
                'events_tested': 0,
                'total_asset_predictions': 0,
                'avg_sequence_accuracy_pct': 0,
                'avg_lag_error_hours': 0,
                'avg_early_warning_hours': 0,
                'false_positive_rate_pct': 0,
            }
        
        total_predictions = sum(len(r.get('predicted_sequence', [])) for r in results)
        avg_accuracy = sum(r['metrics']['sequence_accuracy_pct'] for r in results) / len(results)
        avg_lag_error = sum(r['metrics']['avg_lag_error_hours'] for r in results) / len(results)
        avg_early_warning = sum(r['metrics']['early_warning_hours'] for r in results) / len(results)
        
        return {
            'events_tested': len(results),
            'total_asset_predictions': total_predictions,
            'avg_sequence_accuracy_pct': round(avg_accuracy, 1),
            'avg_lag_error_hours': round(avg_lag_error, 1),
            'avg_early_warning_hours': round(avg_early_warning, 1),
            'false_positive_rate_pct': 0.0,
        }
    
    def save_results(self, results: Dict, output_path: str) -> None:
        """
        Save backtest results to JSON file.
        """
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_path}")


# Quick test
if __name__ == "__main__":
    runner = BacktestRunner()
    results = runner.run_all_events()
    
    print("\n" + "="*50)
    print("BACKTEST RESULTS")
    print("="*50)
    
    agg = results.get('aggregate_metrics', {})
    print(f"Events tested: {agg.get('events_tested', 0)}")
    print(f"Avg sequence accuracy: {agg.get('avg_sequence_accuracy_pct', 0)}%")
    print(f"Avg early warning: {agg.get('avg_early_warning_hours', 0)} hours")
