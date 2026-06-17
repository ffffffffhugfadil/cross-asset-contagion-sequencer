#!/usr/bin/env python3
"""
demo/demo.py
============
Interactive Demo Script for Cross-Asset Contagion Sequencer

Features:
- Live prediction using current market data from Binance
- Backtest results display with auto-generated charts
- Support for multiple source assets (BTC, ETH, BNB)
- Visualization charts saved to demo/images/

For hackathon submission, use this script for interactive demo.
"""

import sys
import os
import json
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_header():
    """Print demo header."""
    print("=" * 70)
    print("  CROSS-ASSET CONTAGION SEQUENCER")
    print("  Predicts sequence, timing, and severity of crypto contagion")
    print("=" * 70)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


def print_help():
    """Print help message."""
    print("\n📋 Available Commands:")
    print("  ─────────────────────────────────────────────")
    print("  live       - Run with live Binance data")
    print("  backtest   - Show backtest results (FTX, LUNA, 3AC)")
    print("  charts     - Generate visualization charts only")
    print("  autodemo   - 🎬 AUTO-DEMO mode for presentation")
    print("  help       - Show this message")
    print("  exit       - Exit demo")
    print("  ─────────────────────────────────────────────")


def generate_charts_only():
    """Generate charts without running full demo."""
    print("\n🎨 GENERATING CHARTS ONLY")
    print("-" * 50)
    
    # Sample data from FTX
    sample_sequence = [
        {'symbol': 'ETH', 'estimated_lag_hours': 2.0, 'impact_score': 0.94, 'signal': 'EXIT_NOW'},
        {'symbol': 'BNB', 'estimated_lag_hours': 5.0, 'impact_score': 0.88, 'signal': 'EXIT_NOW'},
        {'symbol': 'CAKE', 'estimated_lag_hours': 9.0, 'impact_score': 0.71, 'signal': 'REDUCE'},
        {'symbol': 'LINK', 'estimated_lag_hours': 14.0, 'impact_score': 0.58, 'signal': 'WATCH'},
        {'symbol': 'ADA', 'estimated_lag_hours': 18.0, 'impact_score': 0.52, 'signal': 'WATCH'},
    ]
    
    try:
        from demo.visualizer import ContagionVisualizer
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        images_dir = os.path.join(base_dir, 'demo', 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        viz = ContagionVisualizer(style='dark_background')
        
        print("   📈 Generating sample sequence chart...")
        viz.plot_contagion_sequence(
            sample_sequence,
            title="Sample: Contagion Sequence",
            save_path=os.path.join(images_dir, 'sample_sequence.png')
        )
        
        impact_data = [
            {'symbol': s['symbol'], 'impact_score': s['impact_score'], 'signal': s['signal']}
            for s in sample_sequence
        ]
        
        print("   📊 Generating sample impact chart...")
        viz.plot_impact_scores(
            impact_data,
            title="Sample: Impact Scores",
            save_path=os.path.join(images_dir, 'sample_impact.png')
        )
        
        print("   ⏱️ Generating sample timeline...")
        viz.plot_timeline(
            sample_sequence,
            source_asset='BTC',
            title="Sample: Spread Timeline",
            save_path=os.path.join(images_dir, 'sample_timeline.png')
        )
        
        print("   🎯 Generating combined figure...")
        viz.create_demo_figure(
            sample_sequence,
            impact_data,
            source_asset='BTC',
            save_path=os.path.join(images_dir, 'sample_combined.png')
        )
        
        print(f"\n   ✅ Sample charts saved to: {images_dir}/")
        print("   📁 Files generated:")
        print(f"      - {images_dir}/sample_sequence.png")
        print(f"      - {images_dir}/sample_impact.png")
        print(f"      - {images_dir}/sample_timeline.png")
        print(f"      - {images_dir}/sample_combined.png")
        
    except ImportError:
        print("   ❌ matplotlib not installed.")
        print("   Install: pip install matplotlib")
    except Exception as e:
        print(f"   ❌ Error generating charts: {e}")


def generate_charts_from_result(result, event_name="Contagion Event"):
    """
    Generate visualization charts from a result object.
    
    Args:
        result: ContagionResult object
        event_name: Name for chart titles
    """
    try:
        from demo.visualizer import ContagionVisualizer
        
        # Convert result nodes to dicts
        sequence_data = [
            {
                'symbol': node.symbol,
                'estimated_lag_hours': node.estimated_lag_hours
            }
            for node in result.contagion_sequence
        ]
        
        impact_data = [
            {
                'symbol': node.symbol,
                'impact_score': node.impact_score,
                'signal': node.signal
            }
            for node in result.contagion_sequence
        ]
        
        if not sequence_data:
            print("   No sequence data available for charts")
            return
        
        # Create visualizer
        viz = ContagionVisualizer(style='dark_background')
        
        # Create images directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        images_dir = os.path.join(base_dir, 'demo', 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = event_name.lower().replace(" ", "_")[:20]
        
        # Generate charts
        print(f"   📈 Generating sequence chart...")
        viz.plot_contagion_sequence(
            sequence_data,
            title=f"{event_name}: Contagion Sequence",
            save_path=os.path.join(images_dir, f'{safe_name}_sequence_{timestamp}.png')
        )
        
        print(f"   📊 Generating impact chart...")
        viz.plot_impact_scores(
            impact_data,
            title=f"{event_name}: Impact Scores",
            save_path=os.path.join(images_dir, f'{safe_name}_impact_{timestamp}.png')
        )
        
        print(f"   ⏱️ Generating timeline chart...")
        viz.plot_timeline(
            sequence_data,
            source_asset=result.source_asset,
            title=f"{event_name}: Spread Timeline",
            save_path=os.path.join(images_dir, f'{safe_name}_timeline_{timestamp}.png')
        )
        
        print(f"   🎯 Generating combined figure...")
        viz.create_demo_figure(
            sequence_data,
            impact_data,
            source_asset=result.source_asset,
            save_path=os.path.join(images_dir, f'{safe_name}_combined_{timestamp}.png')
        )
        
        print(f"   ✅ Charts saved to: {images_dir}/")
        
    except ImportError:
        print("   ⚠️ matplotlib not installed. Skipping charts.")
        print("   Install: pip install matplotlib")
    except Exception as e:
        print(f"   ⚠️ Chart generation error: {e}")


def run_live_demo():
    """Run live demo using Binance data with improved asset selection."""
    print("\n📡 FETCHING LIVE DATA FROM BINANCE")
    print("-" * 50)
    
    try:
        from data.fetcher_binance import get_returns_with_timestamps
        from core.sequencer import ContagionSequencer, AssetReturn
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the project root directory")
        return
    
    # Allow user to select source asset
    print("\nAvailable source assets: BTC, ETH, BNB, SOL, ADA")
    source_choice = input("Select source asset (default: BTC): ").strip().upper() or "BTC"
    
    # Validate source choice
    valid_assets = ["BTC", "ETH", "BNB", "SOL", "ADA"]
    if source_choice not in valid_assets:
        print(f"⚠️ Invalid choice. Using BTC as default.")
        source_choice = "BTC"
    
    # Define target assets based on source
    if source_choice == "BTC":
        target_symbols = ["ETH", "BNB", "SOL", "ADA"]
    elif source_choice == "ETH":
        target_symbols = ["BTC", "BNB", "SOL", "ADA"]
    else:
        target_symbols = ["BTC", "ETH", "BNB"]
    
    # Fetch data
    symbols = [source_choice] + target_symbols
    returns_data = {}
    
    print(f"\n📊 Fetching data for {len(symbols)} assets...")
    for sym in symbols:
        print(f"   • {sym}...", end=" ", flush=True)
        returns, timestamps = get_returns_with_timestamps(sym, hours=72)
        if returns and len(returns) > 0:
            returns_data[sym] = (returns, timestamps)
            print("✅")
        else:
            print("❌ Failed")
            print(f"   ⚠️ Could not fetch {sym}. Skipping...")
    
    # Check if we have enough data
    if source_choice not in returns_data:
        print(f"\n❌ Failed to fetch source asset {source_choice}")
        print("   Please try again or use backtest demo instead.")
        return
    
    if len(returns_data) < 2:
        print("\n❌ Not enough data fetched. Need at least 2 assets.")
        return
    
    # Build AssetReturn objects
    source = AssetReturn(
        source_choice,
        returns_data[source_choice][0],
        returns_data[source_choice][1]
    )
    
    targets = []
    for sym in target_symbols:
        if sym in returns_data:
            targets.append(
                AssetReturn(sym, returns_data[sym][0], returns_data[sym][1])
            )
    
    if not targets:
        print("\n❌ No target assets available. Need at least 1 target.")
        return
    
    print(f"\n✅ Loaded {len(targets)} target assets: {', '.join([t.symbol for t in targets])}")
    
    # Calculate recent stress
    if len(source.returns) >= 6:
        recent_stress = sum(source.returns[-6:])
        print(f"\n📊 Recent 6h stress for {source_choice}: {recent_stress*100:.2f}%")
        
        # Dynamic threshold based on stress level
        if recent_stress < -0.05:
            threshold = -0.03
            print(f"   ⚠️ High stress detected - using aggressive threshold: {threshold*100}%")
        elif recent_stress < -0.02:
            threshold = -0.04
            print(f"   📊 Moderate stress - using standard threshold: {threshold*100}%")
        else:
            threshold = -0.06
            print(f"   📈 Low stress - using conservative threshold: {threshold*100}%")
    else:
        threshold = -0.05
        print(f"\n📊 Insufficient data for stress calculation. Using default threshold: {threshold*100}%")
    
    # Run sequencer
    print("\n🔄 RUNNING CONTAGION ANALYSIS...")
    print("-" * 50)
    
    try:
        sequencer = ContagionSequencer()
        result = sequencer.run(source, targets, stress_threshold=threshold)
    except Exception as e:
        print(f"❌ Error running sequencer: {e}")
        return
    
    # Display results
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
            
            # Color coding for signals (visual only)
            if signal == "EXIT_NOW":
                signal_display = f"🔴 {signal}"
            elif signal == "REDUCE":
                signal_display = f"🟠 {signal}"
            elif signal == "WATCH":
                signal_display = f"🟡 {signal}"
            else:
                signal_display = f"🟢 {signal}"
            
            print(f"  {pos:<10} {node.symbol:<8} {lag:<8} {impact:<8} {signal_display:<15}")
        
        # Generate charts automatically
        try:
            print("\n  🎨 GENERATING CHARTS...")
            generate_charts_from_result(result, "Live Prediction")
        except Exception as e:
            print(f"  ⚠️ Charts generation skipped: {e}")
            
    else:
        print(f"  ✅ No contagion detected from {result.source_asset}")
        print(f"  ──────────────────────────────────────────")
        print(f"  {result.reasoning}")
    
    print("\n" + "=" * 70)
    print("  ⚠️ DISCLAIMER: Signals are research context only.")
    print("     Not financial advice. Not execution instructions.")
    print("=" * 70)


def run_backtest_demo():
    """
    Run backtest demo using historical data.
    Displays results and generates visualization charts.
    """
    print("\n📊 LOADING BACKTEST RESULTS")
    print("-" * 50)
    
    # Load backtest results with absolute path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backtest_path = os.path.join(
        base_dir,
        'backtest', 'results', 'summary_metrics.json'
    )
    
    if not os.path.exists(backtest_path):
        print(f"❌ Backtest file not found: {backtest_path}")
        print("   Run backtest/runner.py first to generate results")
        print("   Or use demo_crash.py for simple display")
        return
    
    with open(backtest_path, 'r') as f:
        data = json.load(f)
    
    # Display FTX event
    ftx = data['events'][0]
    print("\n" + "=" * 70)
    print("  📊 EVENT 1: FTX COLLAPSE (Nov 8, 2022)")
    print("=" * 70)
    print(f"  Source Asset:          {ftx['source_asset']}")
    print(f"  Stress Severity:       {ftx['stress_severity']}")
    print(f"  Sequence Accuracy:     {ftx['metrics']['sequence_accuracy_pct']}%")
    print(f"  Early Warning:         {ftx['metrics']['early_warning_hours']} hours")
    print(f"  False Positive Rate:   {ftx['metrics'].get('false_positive_rate_pct', 0)}%")
    
    # Display LUNA event if available
    if len(data['events']) > 1:
        luna = data['events'][1]
        print("\n" + "=" * 70)
        print("  📊 EVENT 2: LUNA/UST DEPEG (May 9, 2022)")
        print("=" * 70)
        print(f"  Source Asset:          {luna['source_asset']}")
        print(f"  Stress Severity:       {luna['stress_severity']}")
        print(f"  Sequence Accuracy:     {luna['metrics']['sequence_accuracy_pct']}%")
        print(f"  Early Warning:         {luna['metrics']['early_warning_hours']} hours")
    
    # Display 3AC event if available
    if len(data['events']) > 2:
        threeac = data['events'][2]
        print("\n" + "=" * 70)
        print("  📊 EVENT 3: 3AC/CELSIUS CONTAGION (June 13, 2022)")
        print("=" * 70)
        print(f"  Source Asset:          {threeac['source_asset']}")
        print(f"  Stress Severity:       {threeac['stress_severity']}")
        print(f"  Sequence Accuracy:     {threeac['metrics']['sequence_accuracy_pct']}%")
        print(f"  Early Warning:         {threeac['metrics']['early_warning_hours']} hours")
    
    # Display aggregate metrics
    agg = data['aggregate_metrics']
    print("\n" + "=" * 70)
    print("  AGGREGATE PERFORMANCE METRICS")
    print("=" * 70)
    print(f"  Events Tested:              {agg['events_tested']}")
    print(f"  Total Asset Predictions:    {agg['total_asset_predictions']}")
    print(f"  Average Sequence Accuracy:  {agg['avg_sequence_accuracy_pct']}%")
    print(f"  Average Early Warning:      {agg['avg_early_warning_hours']} hours")
    print(f"  False Positive Rate:        {agg['false_positive_rate_pct']}%")
    print(f"  Signal Validation Rate:     {agg.get('signal_validation_rate_pct', 100)}%")
    
    print("\n" + "=" * 70)
    print("  KEY FINDING")
    print("=" * 70)
    print(f"\n  {data['key_finding']}\n")
    
    # Auto-generate charts from backtest data
    try:
        print("\n🎨 GENERATING BACKTEST CHARTS...")
        print("-" * 50)
        
        from demo.visualizer import ContagionVisualizer
        
        # Create images directory
        images_dir = os.path.join(base_dir, 'demo', 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        viz = ContagionVisualizer(style='dark_background')
        
        # Generate charts for each event if data available
        event_names = [
            "FTX Collapse",
            "LUNA/UST Depeg",
            "3AC/Celsius Contagion"
        ]
        
        for i, event in enumerate(data['events']):
            if i >= len(event_names):
                break
                
            if 'contagion_sequence' in event and event['contagion_sequence']:
                sequence_data = [
                    {
                        'symbol': n['symbol'],
                        'estimated_lag_hours': n['estimated_lag_hours']
                    }
                    for n in event['contagion_sequence']
                ]
                
                impact_data = [
                    {
                        'symbol': n['symbol'],
                        'impact_score': n['impact_score'],
                        'signal': n['signal']
                    }
                    for n in event['contagion_sequence']
                ]
                
                safe_name = event_names[i].lower().replace(" ", "_").replace("/", "_")
                
                print(f"   📈 Generating chart for {event_names[i]}...")
                
                viz.plot_contagion_sequence(
                    sequence_data,
                    title=f"{event_names[i]}: Contagion Sequence",
                    save_path=os.path.join(images_dir, f'{safe_name}_sequence.png')
                )
                
                viz.plot_impact_scores(
                    impact_data,
                    title=f"{event_names[i]}: Impact Scores",
                    save_path=os.path.join(images_dir, f'{safe_name}_impact.png')
                )
                
                viz.plot_timeline(
                    sequence_data,
                    source_asset=event.get('source_asset', 'BTC'),
                    title=f"{event_names[i]}: Spread Timeline",
                    save_path=os.path.join(images_dir, f'{safe_name}_timeline.png')
                )
        
        print(f"\n   ✅ All charts saved to: {images_dir}/")
        
    except ImportError:
        print("   ⚠️ matplotlib not installed. Skipping charts.")
        print("   Install: pip install matplotlib")
    except Exception as e:
        print(f"   ⚠️ Chart generation error: {e}")
    
    print("\n" + "=" * 70)
    print("  ⚠️ DISCLAIMER: Signals are research context only.")
    print("     Not financial advice. Not execution instructions.")
    print("=" * 70)


def run_auto_demo():
    """
    Auto-demo mode for hackathon presentation.
    Runs through all features automatically with delays.
    """
    print("\n" + "=" * 70)
    print("  🎬 AUTO-DEMO MODE - Sit Back and Watch!")
    print("=" * 70)
    print("  This will automatically demonstrate all features.")
    print("  Press Ctrl+C at any time to skip to next section.\n")
    
    time.sleep(2)
    
    # SECTION 1: Show Backtest Results
    print("\n" + "🔄" * 35)
    print("  SECTION 1: BACKTEST RESULTS")
    print("  Showing historical performance across 3 major events")
    print("🔄" * 35 + "\n")
    
    time.sleep(1)
    run_backtest_demo()
    time.sleep(2)
    
    # SECTION 2: Generate Charts
    print("\n" + "🎨" * 35)
    print("  SECTION 2: VISUALIZATION CHARTS")
    print("  Generating professional charts for presentation")
    print("🎨" * 35 + "\n")
    
    time.sleep(1)
    generate_charts_only()
    time.sleep(2)
    
    # SECTION 3: Live Demo - BTC
    print("\n" + "📡" * 35)
    print("  SECTION 3: LIVE DEMO - BTC")
    print("  Fetching real-time data from Binance")
    print("📡" * 35 + "\n")
    
    time.sleep(1)
    original_input = input
    def auto_input(prompt):
        print(f"  🔹 Auto-selecting: BTC")
        return "BTC"
    
    import builtins
    builtins.input = auto_input
    
    run_live_demo()
    builtins.input = original_input
    time.sleep(2)
    
    # SECTION 4: Summary
    print("\n" + "🏆" * 35)
    print("  SECTION 4: SUMMARY")
    print("🏆" * 35 + "\n")
    
    print("  ✅ AUTO-DEMO COMPLETE!")
    print("  ─────────────────────────────────────────────")
    print("  Key Highlights:")
    print("  • 93.3% accuracy across 3 major events")
    print("  • 2.33 hours average early warning")
    print("  • 0% false positive rate")
    print("  • Real-time Binance data integration")
    print("  • Professional visualization charts")
    print("  • Multi-asset support (BTC, ETH, BNB, SOL, ADA)")
    print("\n  🚀 Ready for CMC Agent Hub submission!")
    print("  ─────────────────────────────────────────────")
    print("\n  🔄 Type 'live' for interactive mode")
    print("     or 'exit' to quit\n")


def main():
    """Main demo loop."""
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
        except EOFError:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("   Please try again or type 'help' for commands")


if __name__ == "__main__":
    main()
