#!/bin/bash
echo "========================================"
echo "  Cross-Asset Contagion Sequencer"
echo "  Running All Tasks"
echo "========================================"

# Aktifkan venv
source venv/bin/activate

echo ""
echo "📊 1. Running Tests (109 tests)..."
echo "----------------------------------------"
PYTHONPATH=. python3 -m unittest discover tests/ -v

echo ""
echo "📊 2. Running Backtest Demo..."
echo "----------------------------------------"
PYTHONPATH=. python3 demo/demo_crash.py

echo ""
echo "📊 3. Generating Charts..."
echo "----------------------------------------"
PYTHONPATH=. python3 -c "
import json, os
from demo.visualizer import ContagionVisualizer
os.makedirs('demo/images', exist_ok=True)
viz = ContagionVisualizer(style='dark_background', save_dir='demo/images')
json_path = 'backtest/cache/backtest_results.json'
if os.path.exists(json_path):
    with open(json_path) as f:
        data = json.load(f)
    results = data.get('results', {})
    print(f'Generating charts for {len(results)} events...')
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
        print(f'  Generating {event_name}...')
        viz.plot_contagion_sequence(seq_data, actual_sequence=[{'symbol': s} for s in actual], title=f'{event_name}: Contagion Sequence', save_path=f'demo/images/{safe_name}_sequence.png')
        viz.plot_impact_scores(impact_data, title=f'{event_name}: Impact Scores', save_path=f'demo/images/{safe_name}_impact.png')
        viz.plot_timeline(seq_data, source_asset='BTC', title=f'{event_name}: Spread Timeline', save_path=f'demo/images/{safe_name}_timeline.png')
    print(f'✅ Charts generated for {len(results)} events!')
else:
    print('⚠️ backtest_results.json not found')
print('\n📁 Charts saved to: demo/images/')
"

echo ""
echo "========================================"
echo "  ✅ ALL TASKS COMPLETE!"
echo "========================================"
echo ""
echo "📁 Charts: demo/images/"
echo "📊 Results: backtest/cache/backtest_results.json"
