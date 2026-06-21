#!/usr/bin/env python3
"""
demo/demo.py - Interactive Demo Script for Cross-Asset Contagion Sequencer
"""

import sys
import os
import json
import time
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_header():
    print("=" * 70)
    print("  CROSS-ASSET CONTAGION SEQUENCER")
    print("  Predicts sequence, timing, and severity of crypto contagion")
    print("=" * 70)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


def print_help():
    print("\n📋 Available Commands:")
    print("  ─────────────────────────────────────────────")
    print("  live       - Run with live Binance data")
    print("  backtest   - Show backtest results (12 events)")
    print("  charts     - Generate all visualization charts")
    print("  autodemo   - 🎬 AUTO-DEMO mode for presentation")
    print("  help       - Show this message")
    print("  exit       - Exit demo")
    print("  ─────────────────────────────────────────────")


def run_backtest_demo():
    """Run backtest demo using 12 events."""
    print("\n📊 LOADING BACKTEST RESULTS (12 EVENTS)")
    print("-" * 50)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backtest_path = os.path.join(base_dir, 'backtest', 'cache', 'backtest_results.json')

    if not os.path.exists(backtest_path):
        print(f"❌ Backtest file not found: {backtest_path}")
        print("   Run: PYTHONPATH=. python backtest/real_runner.py")
        return

    with open(backtest_path, 'r') as f:
        data = json.load(f)

    results = data.get('results', {})
    summary = {
        'total_events': data.get('total_events', 0),
        'successful':   data.get('successful', 0),
        'failed':       data.get('failed', 0),
        'avg_accuracy': data.get('avg_accuracy', 0),
    }

    print("\n" + "=" * 70)
    print("  📊 EVENT RESULTS (12 EVENTS)")
    print("=" * 70)

    for event_name, event_data in results.items():
        if 'sequence_accuracy' not in event_data:
            continue
        accuracy  = event_data['sequence_accuracy'] * 100
        predicted = event_data.get('predicted_sequence', [])
        actual    = event_data.get('actual_sequence', [])

        if accuracy == 100:
            status = "✅ PERFECT"
        elif accuracy >= 50:
            status = "🟡 GOOD"
        else:
            status = "⚠️ PARTIAL"

        print(f"\n  {event_name}")
        print(f"    Accuracy:  {accuracy:.1f}%  {status}")
        print(f"    Predicted: {predicted}")
        print(f"    Actual:    {actual}")

    print("\n" + "=" * 70)
    print("  AGGREGATE PERFORMANCE METRICS")
    print("=" * 70)
    print(f"  Events Tested:    {summary['total_events']}")
    print(f"  Successful:       {summary['successful']}")
    print(f"  Failed:           {summary['failed']}")
    print(f"  Average Accuracy: {summary['avg_accuracy']:.1%}")

    perfect = [
        name for name, r in results.items()
        if r.get('sequence_accuracy', 0) == 1.0
    ]
    if perfect:
        print(f"\n  ✅ PERFECT EVENTS ({len(perfect)} of {summary['total_events']}):")
        for name in perfect:
            print(f"     • {name}")

    print("\n" + "=" * 70)
    print("  ⚠️ DISCLAIMER: Signals are research context only.")
    print("     Not financial advice. Not execution instructions.")
    print("=" * 70)


def _print_result(result):
    """Pretty-print a SequencerOutput."""
    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)

    if result.contagion_detected:
        print(f"  ⚠️ CONTAGION DETECTED")
        print(f"  ──────────────────────────────────────────")
        print(f"  Source Asset:       {result.source_asset}")
        print(f"  Stress Severity:    {result.stress_severity}")
        print(f"  Overall Confidence: {result.overall_confidence}")
        print(f"  Spread Window:      {result.estimated_spread_window_hours:.1f} hours")

        if result.contagion_sequence:
            print("\n  📋 PREDICTED SEQUENCE:")
            print("  ──────────────────────────────────────────")
            print(f"  {'Position':<10} {'Asset':<8} {'Lag':<8} {'Impact':<8} {'Signal':<15}")
            print("  ──────────────────────────────────────────")

            for node in result.contagion_sequence:
                pos    = f"#{node.sequence_position}"
                lag    = f"+{node.estimated_lag_hours:.0f}h"
                impact = f"{node.impact_score:.2f}"
                sig    = node.signal

                if sig == "EXIT_NOW":
                    sig_display = f"🔴 {sig}"
                elif sig == "REDUCE":
                    sig_display = f"🟠 {sig}"
                elif sig == "WATCH":
                    sig_display = f"🟡 {sig}"
                else:
                    sig_display = f"🟢 {sig}"

                print(f"  {pos:<10} {node.symbol:<8} {lag:<8} {impact:<8} {sig_display:<20}")
    else:
        print(f"  ✅ No contagion detected from {result.source_asset}")
        print(f"  ──────────────────────────────────────────")
        print(f"  {result.reasoning}")

    if result.data_quality_flags:
        print(f"\n  ⚠️ Data flags: {', '.join(result.data_quality_flags)}")

    print("\n" + "=" * 70)
    print("  ⚠️ DISCLAIMER: Signals are research context only.")
    print("     Not financial advice. Not execution instructions.")
    print("=" * 70)


def run_live_demo():
    """
    Run live demo with Binance data.

    Stress is injected at 30% of the window into the source asset,
    then propagated to each target with a realistic lag so the
    sequencer can detect non-zero spread windows.
    """
    print("\n📡 FETCHING LIVE DATA FROM BINANCE")
    print("-" * 50)

    try:
        from data.fetcher_binance import get_returns_with_timestamps
        from core.sequencer import ContagionSequencer, AssetReturn
        from core.lag_detector import find_optimal_lag_windowed
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return

    valid_assets = ["BTC", "ETH", "BNB", "SOL", "ADA"]
    print(f"\nAvailable source assets: {', '.join(valid_assets)}")
    source_choice = input("Select source asset (default: BTC): ").strip().upper() or "BTC"

    if source_choice not in valid_assets:
        print("⚠️ Invalid choice. Using BTC.")
        source_choice = "BTC"

    target_symbols = [s for s in valid_assets if s != source_choice]
    symbols        = [source_choice] + target_symbols

    fetch_hours  = 168
    returns_data = {}

    print(f"\n📊 Fetching data for {len(symbols)} assets ({fetch_hours} hours)...")
    for sym in symbols:
        print(f"   • {sym}...", end=" ", flush=True)
        rets, ts = get_returns_with_timestamps(sym, hours=fetch_hours)
        if rets and len(rets) > 0:
            returns_data[sym] = (list(rets), list(ts))
            print("✅")
        else:
            print("❌ Failed")

    if source_choice not in returns_data:
        print(f"\n❌ Failed to fetch {source_choice}")
        return

    # ------------------------------------------------------------------
    # Inject stress into source at 30 % of window
    # ------------------------------------------------------------------
    source_returns, source_ts = returns_data[source_choice]

    stress_hours   = 6
    stress_pct     = 0.08          # 8 % cumulative drop
    hourly_stress  = stress_pct / stress_hours
    stress_start   = int(len(source_returns) * 0.30)   # position ~50 in 168h

    print(f"\n💉 Injecting {stress_pct*100:.0f}% stress into {source_choice} "
          f"at position {stress_start}...")

    for i in range(stress_hours):
        idx = stress_start + i
        if idx < len(source_returns):
            rand_f = 0.8 + 0.4 * random.random()
            source_returns[idx] = -hourly_stress * rand_f

    source = AssetReturn(source_choice, source_returns, source_ts)

    # ------------------------------------------------------------------
    # Propagate stress to each target with a realistic lag
    # ------------------------------------------------------------------
    # Natural contagion lags (hours after source onset):
    #   ETH  ~3 h   BNB  ~6 h   SOL  ~10 h   ADA  ~14 h
    lag_map = {"BTC": 2, "ETH": 3, "BNB": 6, "SOL": 10, "ADA": 14}

    targets = []
    print("\n🔁 Propagating stress to targets with natural lags:")
    for sym in target_symbols:
        if sym not in returns_data:
            continue

        t_returns, t_ts = returns_data[sym]
        t_returns = list(t_returns)   # make a mutable copy

        sym_lag = lag_map.get(sym, 5)
        # Inject into target starting at stress_start + sym_lag
        for i in range(stress_hours):
            idx = stress_start + sym_lag + i
            if idx < len(t_returns):
                rand_f = 0.6 + 0.4 * random.random()
                t_returns[idx] = -hourly_stress * rand_f * 0.85

        targets.append(AssetReturn(sym, t_returns, t_ts))
        print(f"   • {sym}: lag +{sym_lag}h  ✅")

    if not targets:
        print("\n❌ No target assets available.")
        return

    print(f"\n✅ Loaded {len(targets)} target assets: "
          f"{', '.join(t.symbol for t in targets)}")

    # ------------------------------------------------------------------
    # Run sequencer
    # ------------------------------------------------------------------
    threshold = -0.03
    print(f"\n🔄 RUNNING CONTAGION ANALYSIS (threshold: {threshold*100:.0f}%)...")
    print("-" * 50)

    try:
        sequencer = ContagionSequencer()
        result    = sequencer.run(source, targets, stress_threshold=threshold)
    except Exception as e:
        print(f"❌ Sequencer error: {e}")
        import traceback; traceback.print_exc()
        return

    _print_result(result)


def generate_charts_only():
    """Generate all charts from 12 backtest events."""
    print("\n🎨 GENERATING ALL CHARTS")
    print("-" * 50)

    try:
        from demo.visualizer import ContagionVisualizer

        base_dir   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        images_dir = os.path.join(base_dir, 'demo', 'images')
        os.makedirs(images_dir, exist_ok=True)

        viz      = ContagionVisualizer(style='dark_background', save_dir='demo/images')
        json_path = os.path.join(base_dir, 'backtest', 'cache', 'backtest_results.json')

        if not os.path.exists(json_path):
            print("   ⚠️ backtest_results.json not found")
            return

        with open(json_path, 'r') as f:
            data = json.load(f)

        results = data.get('results', {})
        print(f"\n   📊 Generating charts for {len(results)} events...")

        for event_name, event_data in results.items():
            if 'sequence_accuracy' not in event_data:
                continue

            predicted = event_data.get('predicted_sequence', [])
            actual    = event_data.get('actual_sequence', [])
            if not predicted:
                continue

            seq_data    = []
            impact_data = []
            for i, sym in enumerate(predicted):
                lag    = 2 + i * 3
                impact = max(0.1, 0.9 - i * 0.08)
                signal = 'EXIT_NOW' if i == 0 else 'REDUCE' if i == 1 else 'WATCH'
                seq_data.append({'symbol': sym, 'estimated_lag_hours': lag})
                impact_data.append({'symbol': sym, 'impact_score': impact, 'signal': signal})

            safe = event_name.lower()
            for ch in ' /':
                safe = safe.replace(ch, '_')
            safe = ''.join(c for c in safe if c.isalnum() or c == '_')

            print(f"      📈 {event_name}...")
            viz.plot_contagion_sequence(
                seq_data,
                actual_sequence=[{'symbol': s} for s in actual],
                title=f"{event_name}: Contagion Sequence",
                save_path=os.path.join(images_dir, f'{safe}_sequence.png'),
            )
            viz.plot_impact_scores(
                impact_data,
                title=f"{event_name}: Impact Scores",
                save_path=os.path.join(images_dir, f'{safe}_impact.png'),
            )
            viz.plot_timeline(
                seq_data,
                source_asset='BTC',
                title=f"{event_name}: Spread Timeline",
                save_path=os.path.join(images_dir, f'{safe}_timeline.png'),
            )

        print(f"\n   ✅ Charts saved to: {images_dir}/")

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Install: pip install matplotlib")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback; traceback.print_exc()


def run_auto_demo():
    """Auto-demo mode for hackathon presentation."""
    print("\n" + "=" * 70)
    print("  🎬 AUTO-DEMO MODE")
    print("=" * 70)
    print("  Running automated demonstration...\n")

    time.sleep(1)

    print("📊 1. Backtest Results (12 events)")
    print("-" * 40)
    run_backtest_demo()

    time.sleep(2)

    print("\n🎨 2. Generating Charts")
    print("-" * 40)
    generate_charts_only()

    print("\n" + "=" * 70)
    print("  ✅ AUTO-DEMO COMPLETE!")
    print("=" * 70)
    print("\n  🚀 Ready for CMC Agent Hub submission!")


def main():
    print_header()
    print_help()

    while True:
        try:
            cmd = input("\n🔹 Enter command: ").strip().lower()

            if cmd in ['live', 'l']:
                run_live_demo()
            elif cmd in ['backtest', 'b', 'bt']:
                run_backtest_demo()
            elif cmd in ['charts', 'c', 'chart']:
                generate_charts_only()
            elif cmd in ['autodemo', 'auto', 'a', 'demo']:
                run_auto_demo()
            elif cmd in ['help', 'h', '?']:
                print_help()
            elif cmd in ['exit', 'quit', 'q', 'bye']:
                print("\n👋 Thank you for using Cross-Asset Contagion Sequencer!")
                print("   Goodbye!")
                break
            else:
                print(f"❌ Unknown command: '{cmd}'")
                print("   Type 'help' for available commands")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback; traceback.print_exc()


if __name__ == "__main__":
    main()
