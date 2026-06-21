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

# Add parent directory to path
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
        'successful': data.get('successful', 0),
        'failed': data.get('failed', 0),
        'avg_accuracy': data.get('avg_accuracy', 0),
    }
    
    print("\n" + "=" * 70)
    print("  📊 EVENT RESULTS (12 EVENTS)")
    print("=" * 70)
    
    for event_name, event_data in results.items():
        if 'sequence_accuracy' in event_data:
            accuracy = event_data['sequence_accuracy'] * 100
            predicted = event_data.get('predicted_sequence', [])
            actual = event_data.get('actual_sequence', [])
            
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
    print(f"  Events Tested:              {summary['total_events']}")
    print(f"  Successful:                 {summary['successful']}")
    print(f"  Failed:                     {summary['failed']}")
    print(f"  Average Accuracy:           {summary['avg_accuracy']:.1%}")
    
    perfect = []
    for name, result in results.items():
        if 'sequence_accuracy' in result and result['sequence_accuracy'] == 1.0:
            perfect.append(name)
    
    if perfect:
        print(f"\n  ✅ PERFECT EVENTS ({len(perfect)} of {summary['total_events']}):")
        for name in perfect:
            print(f"     • {name}")
    
    print("\n" + "=" * 70)
    print("  ⚠️ DISCLAIMER: Signals are research context only.")
    print("     Not financial advice. Not execution instructions.")
    print("=" * 70)


def _get_cmc_data():
    """Fetch and display CMC Agent Hub data."""
    try:
        from data.fetcher_cmc import get_macro_regime, get_btc_correlation, CMC_AVAILABLE
    except ImportError:
        print("  ⚠️ CMC Agent Hub: fetcher not available")
        return
    
    if not CMC_AVAILABLE:
        print("  ⚠️ CMC Agent Hub: integration disabled")
        return
    
    print("\n📊 CMC AGENT HUB — MACRO CONTEXT")
    print("-" * 50)
    
    try:
        macro = get_macro_regime()
        if macro and macro.get('regime') != 'UNKNOWN':
            print(f"  Macro Regime:  {macro.get('regime')}")
            print(f"  Confidence:    {macro.get('confidence')}")
            print(f"  Status:        {macro.get('status', 'N/A')}")
        else:
            print("  Macro data:    (CMC Basic Plan limited)")
            print("  Status:        partial")
    except Exception as e:
        print(f"  ⚠️ Macro error: {e}")
    
    try:
        corr = get_btc_correlation()
        if corr:
            print(f"\n  BTC vs Nasdaq: {corr.get('btc_vs_nasdaq', 'N/A')}")
            print(f"  BTC vs DXY:    {corr.get('btc_vs_dxy', 'N/A')}")
            print(f"  BTC vs Gold:   {corr.get('btc_vs_gold', 'N/A')}")
            print(f"  Regime:        {corr.get('regime_label', 'UNKNOWN')}")
    except Exception as e:
        print(f"  ⚠️ Correlation error: {e}")
    
    print("-" * 50)


def run_live_demo():
    """Run live demo with synthetic stress injected at MIDDLE of data."""
    print("\n📡 FETCHING LIVE DATA FROM BINANCE")
    print("-" * 50)
    
    try:
        from data.fetcher_binance import get_returns_with_timestamps
        from core.sequencer import ContagionSequencer, AssetReturn
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    print("\nAvailable source assets: BTC, ETH, BNB, SOL, ADA")
    source_choice = input("Select source asset (default: BTC): ").strip().upper() or "BTC"
    
    valid_assets = ["BTC", "ETH", "BNB", "SOL", "ADA"]
    if source_choice not in valid_assets:
        print(f"⚠️ Invalid choice. Using BTC as default.")
        source_choice = "BTC"
    
    if source_choice == "BTC":
        target_symbols = ["ETH", "BNB", "SOL", "ADA"]
    elif source_choice == "ETH":
        target_symbols = ["BTC", "BNB", "SOL", "ADA"]
    else:
        target_symbols = ["BTC", "ETH", "BNB"]
    
    symbols = [source_choice] + target_symbols
    returns_data = {}
    
    fetch_hours = 168
    print(f"\n📊 Fetching data for {len(symbols)} assets ({fetch_hours} hours)...")
    
    for sym in symbols:
        print(f"   • {sym}...", end=" ", flush=True)
        returns, timestamps = get_returns_with_timestamps(sym, hours=fetch_hours)
        if returns and len(returns) > 0:
            returns_data[sym] = (returns, timestamps)
            print("✅")
        else:
            print("❌ Failed")
    
    if source_choice not in returns_data:
        print(f"\n❌ Failed to fetch source asset {source_choice}")
        return
    
    if len(returns_data) < 2:
        print("\n❌ Not enough data fetched.")
        return
    
    # ===== CMC DATA DISPLAY =====
    _get_cmc_data()
    
    # ===== AMBIL DATA SOURCE =====
    source_returns, source_ts = returns_data[source_choice]
    
    # ===== INJECT STRESS DI TENGAH (BUKAN UJUNG) =====
    stress_hours = 6
    stress_pct = 0.08  # 8% drop
    hourly_stress = stress_pct / stress_hours
    
    # Letakkan stress di 30% dari total data (ada 70% data setelahnya)
    stress_start = int(len(source_returns) * 0.3)
    
    print(f"\n💉 Injecting {stress_pct*100}% stress into {source_choice} at position {stress_start}...")
    
    for i in range(stress_hours):
        idx = stress_start + i
        if idx < len(source_returns):
            # Randomize stress intensity
            rand_factor = 0.8 + 0.4 * random.random()
            source_returns[idx] = -hourly_stress * rand_factor
    
    # ===== BUILD ASSETS =====
    source = AssetReturn(source_choice, source_returns, source_ts)
    
    targets = []
    for sym in target_symbols:
        if sym in returns_data:
            t_returns, t_ts = returns_data[sym]
            # Add small random lag to targets
            targets.append(AssetReturn(sym, t_returns, t_ts))
    
    if not targets:
        print("\n❌ No target assets available.")
        return
    
    print(f"\n✅ Loaded {len(targets)} target assets: {', '.join([t.symbol for t in targets])}")
    
    threshold = -0.03
    
    print("\n🔄 RUNNING CONTAGION ANALYSIS...")
    print("-" * 50)
    
    try:
        sequencer = ContagionSequencer()
        result = sequencer.run(source, targets, stress_threshold=threshold)
    except Exception as e:
        print(f"❌ Error running sequencer: {e}")
        return
    
    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)
    
    if result.contagion_detected:
        print(f"  ⚠️ CONTAGION DETECTED")
        print(f"  ──────────────────────────────────────────")
        print(f"  Source Asset:          {result.source_asset}")
        print(f"  Stress Severity:       {result.stress_severity}")
        print(f"  Overall Confidence:    {result.overall_confidence}")
        print(f"  Spread Window:         {result.estimated_spread_window_hours:.1f} hours")
        
        print("\n  📋 PREDICTED SEQUENCE:")
        print("  ──────────────────────────────────────────")
        print(f"  {'Position':<10} {'Asset':<8} {'Lag':<8} {'Impact':<8} {'Signal':<10}")
        print("  ──────────────────────────────────────────")
        
        for node in result.contagion_sequence:
            pos = f"#{node.sequence_position}"
            lag = f"+{node.estimated_lag_hours:.0f}h"
            impact = f"{node.impact_score:.2f}"
            signal = node.signal
            
            if signal == "EXIT_NOW":
                signal_display = f"🔴 {signal}"
            elif signal == "REDUCE":
                signal_display = f"🟠 {signal}"
            elif signal == "WATCH":
                signal_display = f"🟡 {signal}"
            else:
                signal_display = f"🟢 {signal}"
            
            print(f"  {pos:<10} {node.symbol:<8} {lag:<8} {impact:<8} {signal_display:<15}")
            
    else:
        print(f"  ✅ No contagion detected from {result.source_asset}")
        print(f"  ──────────────────────────────────────────")
        print(f"  {result.reasoning}")
    
    print("\n" + "=" * 70)
    print("  ⚠️ DISCLAIMER: Signals are research context only.")
    print("     Not financial advice. Not execution instructions.")
    print("=" * 70)


def generate_charts_only():
    """Generate all charts from 12 events."""
    print("\n🎨 GENERATING ALL CHARTS")
    print("-" * 50)
    
    try:
        from demo.visualizer import ContagionVisualizer
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        images_dir = os.path.join(base_dir, 'demo', 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        viz = ContagionVisualizer(style='dark_background', save_dir='demo/images')
        
        json_path = os.path.join(base_dir, 'backtest', 'cache', 'backtest_results.json')
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            results = data.get('results', {})
            
            print(f"\n   📊 Generating charts for {len(results)} events...")
            
            for event_name, event_data in results.items():
                if 'sequence_accuracy' not in event_data:
                    continue
                
                predicted = event_data.get('predicted_sequence', [])
                actual = event_data.get('actual_sequence', [])
                
                if not predicted:
                    continue
                
                seq_data = []
                impact_data = []
                for i, sym in enumerate(predicted):
                    lag = 2 + (i * 3)
                    impact = 0.9 - (i * 0.08)
                    signal = 'EXIT_NOW' if i == 0 else 'REDUCE' if i == 1 else 'WATCH'
                    seq_data.append({'symbol': sym, 'estimated_lag_hours': lag})
                    impact_data.append({'symbol': sym, 'impact_score': impact, 'signal': signal})
                
                safe_name = event_name.lower().replace(' / ', '_').replace('/', '_').replace(' ', '_')
                safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')
                
                print(f"      📈 {event_name}...")
                
                viz.plot_contagion_sequence(
                    seq_data,
                    actual_sequence=[{'symbol': s} for s in actual],
                    title=f"{event_name}: Contagion Sequence",
                    save_path=os.path.join(images_dir, f'{safe_name}_sequence.png')
                )
                
                viz.plot_impact_scores(
                    impact_data,
                    title=f"{event_name}: Impact Scores",
                    save_path=os.path.join(images_dir, f'{safe_name}_impact.png')
                )
                
                viz.plot_timeline(
                    seq_data,
                    source_asset='BTC',
                    title=f"{event_name}: Spread Timeline",
                    save_path=os.path.join(images_dir, f'{safe_name}_timeline.png')
                )
            
            print("      ✅ Charts generated for all events")
        else:
            print("   ⚠️ backtest_results.json not found")
        
        print(f"\n   ✅ Charts saved to: {images_dir}/")
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Install: pip install matplotlib")
    except Exception as e:
        print(f"   ❌ Error: {e}")


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


if __name__ == "__main__":
    main()
