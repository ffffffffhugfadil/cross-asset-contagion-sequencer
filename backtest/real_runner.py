# backtest/real_runner.py
"""
Real backtest runner using Binance API (public, free).
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backtest.events_config import EVENTS
from core.sequencer import ContagionSequencer, AssetReturn
from backtest.outcome_extractor import compute_actual_order, find_stress_onset_index

# Import langsung dari file (hindari __init__.py)
import importlib.util
spec = importlib.util.spec_from_file_location("fetcher_binance", "data/fetcher_binance.py")
fetcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetcher)
fetch_hourly_klines = fetcher.fetch_hourly_klines

print("✓ Using Binance Public API (free, no API key required)")

CACHE_DIR = Path("backtest/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_or_fetch_data(symbol: str, event_date: str, before_hours: int = 96, after_hours: int = 72):
    """Fetch data from Binance with caching."""
    cache_file = CACHE_DIR / f"binance_{symbol}_{event_date}_{before_hours}_{after_hours}.json"
    
    if cache_file.exists():
        with open(cache_file) as f:
            data = json.load(f)
        return data.get("returns", []), data.get("timestamps", [])
    
    print(f"  Fetching {symbol} from Binance...")
    event_dt = datetime.strptime(event_date, "%Y-%m-%d")
    start = event_dt - timedelta(hours=before_hours)
    end = event_dt + timedelta(hours=after_hours)
    
    returns, timestamps = fetch_hourly_klines(symbol, start, end)
    
    if not returns:
        raise ValueError(f"No data for {symbol}")
    
    with open(cache_file, "w") as f:
        json.dump({"returns": returns, "timestamps": timestamps}, f)
    
    return returns, timestamps

def run_single_event(event):
    """Run sequencer on one event."""
    print(f"\n--- {event.name} ({event.date}) ---")
    
    try:
        source_returns, source_ts = get_or_fetch_data(event.source_asset, event.date)
        if len(source_returns) < 10:
            return {"error": f"Insufficient data: {len(source_returns)} points"}
        
        onset_idx = find_stress_onset_index(source_returns, threshold=event.stress_threshold)
        if onset_idx is None:
            return {"error": f"No stress detected (threshold: {event.stress_threshold})"}
        
        source_trimmed = source_returns[:onset_idx+1]
        source_ts_trimmed = source_ts[:onset_idx+1]
        source = AssetReturn(event.source_asset, source_trimmed, source_ts_trimmed)
        
        targets = []
        for target in event.target_assets:
            try:
                t_returns, t_ts = get_or_fetch_data(target, event.date)
                if len(t_returns) > 10:
                    targets.append(AssetReturn(target, t_returns[:onset_idx+1], t_ts[:onset_idx+1]))
            except Exception as e:
                print(f"  Warning: Failed to fetch {target}: {e}")
        
        if not targets:
            return {"error": "No valid target data"}
        
        sequencer = ContagionSequencer()
        result = sequencer.run(source, targets, stress_threshold=event.stress_threshold)
        
        predicted = [n.symbol for n in result.contagion_sequence]
        actual = compute_actual_order(targets, source_trimmed, event.date)
        
        accuracy = 0
        if predicted and actual:
            matches = sum(1 for i in range(min(len(predicted), len(actual))) if predicted[i] == actual[i])
            accuracy = matches / len(predicted)
        
        return {
            "event": event.name,
            "date": event.date,
            "category": event.category,
            "predicted_sequence": predicted,
            "actual_sequence": actual,
            "sequence_accuracy": accuracy,
            "overall_confidence": result.overall_confidence,
            "stress_severity": result.stress_severity,
            "data_quality_flags": result.data_quality_flags,
        }
    except Exception as e:
        return {"error": str(e)}

def run_all_events():
    results = {}
    for event in EVENTS:
        results[event.name] = run_single_event(event)
    return results

def generate_summary(results):
    accuracies = []
    errors = []
    for name, result in results.items():
        if "sequence_accuracy" in result:
            accuracies.append(result["sequence_accuracy"])
        elif "error" in result:
            errors.append(name)
    
    return {
        "total_events": len(results),
        "successful": len(accuracies),
        "failed": len(errors),
        "failed_names": errors,
        "avg_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0,
        "results": results,
    }

if __name__ == "__main__":
    print("=" * 60)
    print("CROSS-ASSET CONTAGION SEQUENCER")
    print("Real Backtest — Binance Public API")
    print("=" * 60)
    
    print(f"\nFound {len(EVENTS)} events to test")
    print("-" * 60)
    
    results = run_all_events()
    summary = generate_summary(results)
    
    with open(CACHE_DIR / "backtest_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total events: {summary['total_events']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    if summary['failed_names']:
        print(f"Failed events: {summary['failed_names']}")
    if summary['successful'] > 0:
        print(f"Average accuracy: {summary['avg_accuracy']:.1%}")
        print("-" * 60)
        for name, result in results.items():
            if "sequence_accuracy" in result:
                status = "✅" if result['sequence_accuracy'] > 0.5 else "⚠️"
                print(f"  {status} {name}: {result['sequence_accuracy']:.1%}")
    
    print(f"\nResults saved to: {CACHE_DIR / 'backtest_results.json'}")
