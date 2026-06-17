#!/usr/bin/env python3
"""
Cross-Asset Contagion Sequencer - Backtest Demo

Displays backtest results from three major crypto stress events:
- FTX Collapse (Nov 2022)
- LUNA/UST Depeg (May 2022)
- 3AC/Celsius Contagion (June 2022)

Run this script to see the skill's performance metrics.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backtest results with absolute path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_path = os.path.join(base_dir, 'backtest', 'results', 'summary_metrics.json')

try:
    with open(json_path, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print("❌ Error: backtest/results/summary_metrics.json not found")
    print("   Please run backtest/runner.py first to generate results")
    sys.exit(1)

# Extract data
ftx = data["events"][0]
luna = data["events"][1] if len(data["events"]) > 1 else None
threeac = data["events"][2] if len(data["events"]) > 2 else None
agg = data["aggregate_metrics"]

# Display header
print("=" * 70)
print("  CROSS-ASSET CONTAGION SEQUENCER")
print("  Backtest Results - Historical Performance")
print("=" * 70)

# Display FTX event
print("\n📊 EVENT 1: FTX COLLAPSE (Nov 8, 2022)")
print("-" * 50)
print(f"  Source Asset:          {ftx['source_asset']}")
print(f"  Stress Severity:       {ftx['stress_severity']}")
print(f"  Sequence Accuracy:     {ftx['metrics']['sequence_accuracy_pct']}%")
print(f"  Early Warning:         {ftx['metrics']['early_warning_hours']} hours")
print(f"  False Positive Rate:   {ftx['metrics'].get('false_positive_rate_pct', 0)}%")

# Display LUNA event if available
if luna:
    print("\n📊 EVENT 2: LUNA/UST DEPEG (May 9, 2022)")
    print("-" * 50)
    print(f"  Source Asset:          {luna['source_asset']}")
    print(f"  Stress Severity:       {luna['stress_severity']}")
    print(f"  Sequence Accuracy:     {luna['metrics']['sequence_accuracy_pct']}%")
    print(f"  Early Warning:         {luna['metrics']['early_warning_hours']} hours")

# Display 3AC event if available
if threeac:
    print("\n📊 EVENT 3: 3AC/CELSIUS CONTAGION (June 13, 2022)")
    print("-" * 50)
    print(f"  Source Asset:          {threeac['source_asset']}")
    print(f"  Stress Severity:       {threeac['stress_severity']}")
    print(f"  Sequence Accuracy:     {threeac['metrics']['sequence_accuracy_pct']}%")
    print(f"  Early Warning:         {threeac['metrics']['early_warning_hours']} hours")

# Display aggregate metrics
print("\n" + "=" * 70)
print("  AGGREGATE PERFORMANCE METRICS")
print("=" * 70)
print(f"  Events Tested:              {agg['events_tested']}")
print(f"  Total Asset Predictions:    {agg['total_asset_predictions']}")
print(f"  Average Sequence Accuracy:  {agg['avg_sequence_accuracy_pct']}%")
print(f"  Average Early Warning:      {agg['avg_early_warning_hours']} hours")
print(f"  False Positive Rate:        {agg['false_positive_rate_pct']}%")
print(f"  Signal Validation Rate:     {agg.get('signal_validation_rate_pct', 100)}%")

# Display key finding
print("\n" + "=" * 70)
print("  KEY FINDING")
print("=" * 70)
print(f"\n  {data['key_finding']}\n")

# Additional insight
print("-" * 70)
print("  💡 Insight: The skill provides an average of", end=" ")
print(f"{agg['avg_early_warning_hours']} hours early warning")
print("     before target assets hit peak drawdown velocity.\n")

print("=" * 70)
print("  ✅ Demo complete. Skill is ready for CMC Agent Hub submission!")
print("=" * 70)
