# Cross-Asset Contagion Sequencer Makefile

PYTHON = python3
VENV = venv
ACTIVATE = . $(VENV)/bin/activate

.PHONY: help setup demo backtest charts test images clean zip export all auto

help:
	@echo "Cross-Asset Contagion Sequencer - Commands"
	@echo ""
	@echo "  make setup     - Setup virtual environment"
	@echo "  make demo      - Run interactive demo"
	@echo "  make backtest  - Run backtest demo"
	@echo "  make charts    - Generate all charts (13 files)"
	@echo "  make test      - Run unit tests (109 tests)"
	@echo "  make images    - Open charts folder"
	@echo "  make clean     - Clean cache files"
	@echo "  make zip       - Create submission ZIP"
	@echo "  make export    - Export for CMC Agent Hub"
	@echo "  make all       - Run test + demo"
	@echo "  make auto      - Full auto-demo"

setup:
	@echo "Setting up virtual environment..."
	@python3 -m venv venv
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "Setup complete!"

demo:
	@echo "Running interactive demo..."
	@. venv/bin/activate && python3 demo/demo.py

backtest:
	@echo "Running backtest demo..."
	@. venv/bin/activate && python3 demo/demo_crash.py

charts:
	@echo "Generating all charts (13 files)..."
	@. venv/bin/activate && python3 -c "import json, os; from demo.visualizer import ContagionVisualizer; os.makedirs('demo/images', exist_ok=True); data = json.load(open('backtest/results/summary_metrics.json')); viz = ContagionVisualizer(style='dark_background'); name_map = {'FTX Collapse': 'ftx_collapse', 'LUNA / UST Depeg Collapse': 'luna_ust_depeg_collapse', '3AC / Celsius Contagion': '3ac_celsius_contagion'}; [viz.plot_contagion_sequence([{'symbol': p['symbol'], 'estimated_lag_hours': p['estimated_lag_hours']} for p in event['predicted_sequence']], actual_sequence=[{'symbol': a['symbol'], 'actual_lag_hours': a['actual_lag_hours']} for a in event['actual_sequence']], title=f\"{event['event_name']}: Contagion Sequence\", save_path=f\"demo/images/{name_map.get(event['event_name'], event['event_name'].lower().replace(' / ', '_').replace('/', '_').replace(' ', '_'))}_sequence.png\") or viz.plot_impact_scores([{'symbol': p['symbol'], 'impact_score': p['impact_score'], 'signal': 'WATCH'} for p in event['predicted_sequence']], title=f\"{event['event_name']}: Impact Scores\", save_path=f\"demo/images/{name_map.get(event['event_name'], event['event_name'].lower().replace(' / ', '_').replace('/', '_').replace(' ', '_'))}_impact.png\") or viz.plot_timeline([{'symbol': p['symbol'], 'estimated_lag_hours': p['estimated_lag_hours']} for p in event['predicted_sequence']], source_asset='BTC', title=f\"{event['event_name']}: Spread Timeline\", save_path=f\"demo/images/{name_map.get(event['event_name'], event['event_name'].lower().replace(' / ', '_').replace('/', '_').replace(' ', '_'))}_timeline.png\") for event in data['events']]; sample_seq = [{'symbol': 'ETH', 'estimated_lag_hours': 2, 'impact_score': 0.94, 'signal': 'EXIT_NOW'}, {'symbol': 'BNB', 'estimated_lag_hours': 5, 'impact_score': 0.88, 'signal': 'EXIT_NOW'}, {'symbol': 'CAKE', 'estimated_lag_hours': 9, 'impact_score': 0.71, 'signal': 'REDUCE'}, {'symbol': 'LINK', 'estimated_lag_hours': 14, 'impact_score': 0.58, 'signal': 'WATCH'}, {'symbol': 'ADA', 'estimated_lag_hours': 18, 'impact_score': 0.52, 'signal': 'WATCH'}]; sample_impact = [{'symbol': s['symbol'], 'impact_score': s['impact_score'], 'signal': s['signal']} for s in sample_seq]; viz.plot_contagion_sequence(sample_seq, title='Sample: Contagion Sequence', save_path='demo/images/sample_sequence.png'); viz.plot_impact_scores(sample_impact, title='Sample: Impact Scores', save_path='demo/images/sample_impact.png'); viz.plot_timeline(sample_seq, source_asset='BTC', title='Sample: Spread Timeline', save_path='demo/images/sample_timeline.png'); viz.create_demo_figure(sample_seq, sample_impact, source_asset='BTC', save_path='demo/images/sample_combined.png'); print('\n✅ All 13 charts generated!')"
	@echo "📁 Charts saved to demo/images/ (13 files)"

test:
	@echo "Running unit tests (109 tests)..."
	@. venv/bin/activate && python3 -m unittest discover tests/ -v
	@echo "All tests passed!"

images:
	@open demo/images/

clean:
	@echo "Cleaning cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "Clean complete!"

zip:
	@echo "Creating submission ZIP..."
	@zip -r cross-asset-contagion-sequencer.zip . -x "venv/*" -x "*.pyc" -x "*__pycache__*" -x ".DS_Store" -x ".env" -x "*.log" -x "demo/images/*.png" -x ".git/*"
	@echo "ZIP created!"
	@ls -lh cross-asset-contagion-sequencer.zip

export:
	@echo "Exporting agent..."
	@. venv/bin/activate && python3 export_agent.py || echo "export_agent.py not found"

all: test demo
	@echo "All tasks completed!"

auto:
	@echo "Running auto-demo..."
	@. venv/bin/activate && python3 demo/demo.py
	@echo "Type 'autodemo' when prompted"
