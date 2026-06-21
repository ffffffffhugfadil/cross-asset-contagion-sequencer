# Cross-Asset Contagion Sequencer Makefile
# BNB Hack 2026 — Track 2: Strategy Skills

PYTHON = python3
VENV = venv
ACTIVATE = . $(VENV)/bin/activate

.PHONY: help setup demo backtest charts test images clean zip export all auto result

help:
	@echo "========================================"
	@echo "  CROSS-ASSET CONTAGION SEQUENCER"
	@echo "  BNB Hack 2026 — Track 2"
	@echo "========================================"
	@echo ""
	@echo "  📋 Available Commands:"
	@echo "  ─────────────────────────────────────"
	@echo "  make setup     - Setup virtual environment"
	@echo "  make demo      - Run interactive demo"
	@echo "  make backtest  - Run backtest demo (12 events)"
	@echo "  make charts    - Generate all charts"
	@echo "  make test      - Run 109 unit tests"
	@echo "  make result    - Show 12 events result (73.6%)"
	@echo "  make images    - Open charts folder"
	@echo "  make clean     - Clean cache files"
	@echo "  make zip       - Create submission ZIP"
	@echo "  make all       - Run test + demo"
	@echo "  ─────────────────────────────────────"

setup:
	@echo "Setting up virtual environment..."
	@python3 -m venv venv
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Setup complete!"

demo:
	@echo "Running interactive demo (12 events, 73.6% accuracy)..."
	@. venv/bin/activate && PYTHONPATH=. python3 demo/demo.py
	@echo "✅ Demo complete!"

backtest:
	@echo "Running backtest demo (12 events)..."
	@. venv/bin/activate && PYTHONPATH=. python3 demo/demo_crash.py
	@echo "✅ Backtest complete!"

charts:
	@echo "Generating all charts from 12 events..."
	@. venv/bin/activate && PYTHONPATH=. python3 -c "import demo.demo as d; d.generate_charts_only()"
	@echo "✅ Charts complete!"

test:
	@echo "Running unit tests (109 tests)..."
	@. venv/bin/activate && PYTHONPATH=. python3 -m unittest discover tests/ -v
	@echo "✅ Tests complete!"

result:
	@echo "========================================"
	@echo "  CROSS-ASSET CONTAGION SEQUENCER"
	@echo "  12 EVENTS BACKTEST RESULT"
	@echo "  Data Source: Binance Public API (real)"
	@echo "========================================"
	@echo ""
	@echo "  📊 Average Accuracy: 73.6%"
	@echo "  📊 Perfect Events:   7/12 (58.3%)"
	@echo "  📊 Failed Events:    0"
	@echo ""
	@echo "  ✅ PERFECT EVENTS (100%):"
	@echo "     • 3AC/Celsius Contagion (Jun 2022)"
	@echo "     • USDC Depeg / SVB (Mar 2023)"
	@echo "     • COVID Black Thursday (Mar 2020)"
	@echo "     • Ronin Bridge Hack (Mar 2022)"
	@echo "     • China ICO Ban (Sep 2017)"
	@echo "     • Poly Network Hack (Aug 2021)"
	@echo "     • Bybit Hack (Feb 2025)"
	@echo ""
	@echo "  📈 PARTIAL EVENTS (33.3%):"
	@echo "     • FTX Collapse (Nov 2022)"
	@echo "     • SEC vs Binance/Coinbase (Jun 2023)"
	@echo "     • China Mining Ban (May 2021)"
	@echo "     • Euler Finance Hack (Mar 2023)"
	@echo ""
	@echo "  🟡 50% EVENT:"
	@echo "     • LUNA/UST Depeg (May 2022)"
	@echo ""
	@echo "========================================"
	@echo "  🏆 Ready for BNB Hack 2026!"
	@echo "========================================"

images:
	@open demo/images/

clean:
	@echo "Cleaning cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf data/cache/* 2>/dev/null || true
	@echo "✅ Clean complete!"

zip:
	@echo "Creating submission ZIP..."
	@zip -r cross-asset-contagion-sequencer.zip . -x "venv/*" -x "*.pyc" -x "*__pycache__*" -x ".DS_Store" -x ".env" -x "*.log" -x "demo/images/*.png" -x ".git/*" -x "data/cache/*"
	@echo "✅ ZIP created!"
	@ls -lh cross-asset-contagion-sequencer.zip

all: test demo
	@echo "✅ All tasks completed!"

auto:
	@echo "Running auto-demo (12 events)..."
	@. venv/bin/activate && PYTHONPATH=. python3 demo/demo.py -c "import demo.demo as d; d.run_auto_demo()"
	@echo "✅ Auto-demo complete!"
