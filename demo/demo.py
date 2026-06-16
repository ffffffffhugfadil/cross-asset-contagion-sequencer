"""
demo/demo.py
============
Interactive demo script for Cross-Asset Contagion Sequencer.

Shows live prediction using current market data from Binance.
For hackathon submission, use demo_crash.py for backtest results.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_header():
    """Print demo header."""
    print("=" * 60)
    print("CROSS-ASSET CONTAGION SEQUENCER")
    print("=" * 60)
    print("Predicts sequence, timing, and severity of crypto contagion")
    print("-" * 60)


def print_help():
    """Print help message."""
    print("\nAvailable commands:")
    print("  live      - Run with live Binance data")
    print("  backtest  - Show backtest results (FTX, LUNA, 3AC)")
    print("  help      - Show this message")
    print("  exit      - Exit demo")
    print()


def run_live_demo():
    """Run live demo using Binance data."""
    print("\n📡 Fetching live data from Binance...")
    
    try:
        from data.fetcher_binance import get_returns_with_timestamps
        from core.sequencer import ContagionSequencer, AssetReturn
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running from the project root directory")
        return
    
    # Fetch data for BTC, ETH, BNB
    symbols = ["BTC", "ETH", "BNB"]
    returns_data = {}
    
    for sym in symbols:
        print(f"  Fetching {sym}...")
        returns, timestamps = get_returns_with_timestamps(sym, hours=72)
        if returns:
            returns_data[sym] = (returns, timestamps)
        else:
            print(f"  Failed to fetch {sym}")
            return
    
    # Build AssetReturn objects
    source = AssetReturn("BTC", returns_data["BTC"][0], returns_data["BTC"][1])
    targets = [
        AssetReturn("ETH", returns_data["ETH"][0], returns_data["ETH"][1]),
        AssetReturn("BNB", returns_data["BNB"][0], returns_data["BNB"][1]),
    ]
    
    # Calculate recent stress
    if len(source.returns) >= 6:
        recent_stress = sum(source.returns[-6:])
        print(f"\n📊 Recent 6h stress for BTC: {recent_stress*100:.2f}%")
        
        if recent_stress < -0.03:
            threshold = -0.03
        else:
            threshold = -0.05
        print(f"Using stress threshold: {threshold*100}%")
    else:
        threshold = -0.05
    
    # Run sequencer
    print("\n🔄 Running contagion analysis...")
    sequencer = ContagionSequencer()
    result = sequencer.run(source, targets, stress_threshold=threshold)
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if result.contagion_detected:
        print(f"⚠️ CONTAGION DETECTED")
        print(f"   Source: {result.source_asset}")
        print(f"   Stress severity: {result.stress_severity}")
        print(f"   Confidence: {result.overall_confidence}")
        print(f"   Spread window: {result.estimated_spread_window_hours:.1f} hours")
        
        print("\n📋 Predicted Sequence:")
        print("-" * 40)
        for node in result.contagion_sequence:
            print(f"   {node.symbol}: +{node.estimated_lag_hours:.0f}h | "
                  f"impact: {node.impact_score:.2f} | signal: {node.signal}")
    else:
        print(f"✅ No contagion detected from {result.source_asset}")
        print(f"   {result.reasoning}")
    
    print("\n" + "-" * 40)
    print("⚠️ Signals are research context only — not execution instructions.")
    print("=" * 60)


def run_backtest_demo():
    """Run backtest demo using historical data."""
    print("\n📊 Loading backtest results...")
    
    backtest_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'backtest', 'results', 'summary_metrics.json'
    )
    
    if not os.path.exists(backtest_path):
        print(f"Backtest file not found: {backtest_path}")
        print("Run demo_crash.py for backtest display")
        return
    
    with open(backtest_path, 'r') as f:
        data = json.load(f)
    
    # Display FTX event
    ftx = data['events'][0]
    print("\n" + "=" * 60)
    print("FTX COLLAPSE (Nov 8, 2022)")
    print("=" * 60)
    print(f"Source: {ftx['source_asset']}")
    print(f"Stress severity: {ftx['stress_severity']}")
    print(f"Sequence accuracy: {ftx['metrics']['sequence_accuracy_pct']}%")
    print(f"Early warning: {ftx['metrics']['early_warning_hours']} hours")
    
    # Display aggregate metrics
    agg = data['aggregate_metrics']
    print("\n" + "=" * 60)
    print("AGGREGATE METRICS (3 events)")
    print("=" * 60)
    print(f"Events tested: {agg['events_tested']}")
    print(f"Total predictions: {agg['total_asset_predictions']}")
    print(f"Avg sequence accuracy: {agg['avg_sequence_accuracy_pct']}%")
    print(f"Avg early warning: {agg['avg_early_warning_hours']} hours")
    print(f"False positive rate: {agg['false_positive_rate_pct']}%")
    
    print("\n" + "=" * 60)
    print("KEY FINDING")
    print("=" * 60)
    print(f"\n{data['key_finding']}\n")


def main():
    """Main demo loop."""
    print_header()
    print_help()
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'live':
                run_live_demo()
            elif cmd == 'backtest':
                run_backtest_demo()
            elif cmd == 'help':
                print_help()
            elif cmd in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            else:
                print(f"Unknown command: {cmd}")
                print_help()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
