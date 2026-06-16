#!/usr/bin/env python3
"""Demo: Cross-Asset Contagion Sequencer"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open("backtest/results/summary_metrics.json", "r") as f:
    data = json.load(f)

ftx = data["events"][0]
agg = data["aggregate_metrics"]

print("=" * 60)
print("CROSS-ASSET CONTAGION SEQUENCER - DEMO")
print("=" * 60)

print("\nFTX COLLAPSE (Nov 8, 2022)")
print("  Source: " + str(ftx["source_asset"]))
print("  Stress severity: " + str(ftx["stress_severity"]))
print("  Sequence accuracy: " + str(ftx["metrics"]["sequence_accuracy_pct"]) + "%")
print("  Early warning: " + str(ftx["metrics"]["early_warning_hours"]) + " hours")

print("\nAGGREGATE METRICS (3 events)")
print("  Events tested: " + str(agg["events_tested"]))
print("  Total predictions: " + str(agg["total_asset_predictions"]))
print("  Avg sequence accuracy: " + str(agg["avg_sequence_accuracy_pct"]) + "%")
print("  Avg early warning: " + str(agg["avg_early_warning_hours"]) + " hours")
print("  False positive rate: " + str(agg["false_positive_rate_pct"]) + "%")

print("\nKEY FINDING")
print("  " + str(data["key_finding"]))

print("\nDemo selesai. Skill siap disubmit ke CMC Agent Hub!")