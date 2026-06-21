---
name: cross-asset-contagion-sequencer
description: Predicts the sequence, timing, and severity of crypto market contagion before it spreads. 73.6% accuracy across 12 real events (2017-2025), 7 events at 100%. Integrated with CMC Agent Hub for macro validation.
license: MIT
compatibility: ">=1.0.0"
user-invocable: true
allowed-tools:
  - mcp__cmc-skill-hub__find_skill
  - mcp__cmc-skill-hub__execute_skill
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__search_cryptos
  - mcp__cmc-mcp__get_global_metrics_latest
---

# Cross-Asset Contagion Sequencer

## What It Does

Predicts which crypto assets get hit next, in what order, and when — before a crash spreads across the market.

## The Problem

When a major asset like BTC crashes, the damage doesn't happen all at once. Some assets get hit within hours, others lag by 6–12 hours, and a few survive the first wave only to collapse later.

Most existing tools only detect contagion *after* it has already happened. This skill instead predicts **which assets get hit next, in what order, and when**.

## How It Works

1. **Detect stress** in a source asset (e.g., BTC drops -5% in 6 hours)
2. **Compute cross-correlation lags** (0–48h) for each candidate target asset
3. **Sort by lag** to build the predicted contagion sequence
4. **Generate signals**: `EXIT_NOW` / `REDUCE` / `WATCH` / `HOLD`

### Pipeline

```
SOURCE STRESS DETECTED
  BTC: -5.8% cumulative over 6 hours
            │
            ▼
  ┌─────────────────────────────────┐
  │  1. Detect stress onset         │
  │  2. Compute cross-correlation   │
  │     lags (0–48h) per target     │
  │  3. Sort by lag → sequence      │
  │  4. Score impact (OI amplifier) │
  │  5. Assign signals              │
  └─────────────────────────────────┘
            │
            ▼
CONTAGION SEQUENCE OUTPUT
  BTC → ETH(+2h) → BNB(+5h) → SOL(+9h) → ADA(+14h)
  Signals: EXIT_NOW · REDUCE · WATCH · HOLD
```

## Example Output

```json
{
  "contagion_detected": true,
  "source_asset": "BTC",
  "stress_severity": "CRITICAL",
  "overall_confidence": "HIGH",
  "estimated_spread_window_hours": 18.0,
  "contagion_sequence": [
    {
      "symbol": "ETH",
      "sequence_position": 1,
      "estimated_lag_hours": 2.0,
      "impact_score": 0.94,
      "signal": "EXIT_NOW"
    },
    {
      "symbol": "BNB",
      "sequence_position": 2,
      "estimated_lag_hours": 5.0,
      "impact_score": 0.88,
      "signal": "EXIT_NOW"
    },
    {
      "symbol": "SOL",
      "sequence_position": 3,
      "estimated_lag_hours": 9.0,
      "impact_score": 0.71,
      "signal": "REDUCE"
    },
    {
      "symbol": "ADA",
      "sequence_position": 4,
      "estimated_lag_hours": 14.0,
      "impact_score": 0.52,
      "signal": "WATCH"
    }
  ]
}
```

## Backtest Results

### Performance Summary

| Metric | Value |
|---|---|
| Events tested | 12 |
| Average accuracy | **73.6%** |
| Perfect events (100%) | **7/12 (58.3%)** |
| Failed events | **0** |
| Data source | Binance Public API (real) |

### Perfect Events

| Event | Date | Category |
|---|---|---|
| 3AC/Celsius Contagion | Jun 2022 | Lender Contagion |
| USDC Depeg / SVB | Mar 2023 | Bank-Run Depeg |
| COVID Black Thursday | Mar 2020 | Leverage Cascade |
| Ronin Bridge Hack | Mar 2022 | Bridge Exploit |
| China ICO Ban | Sep 2017 | Regulatory Ban |
| Poly Network Hack | Aug 2021 | Bridge Exploit |
| Bybit Hack | Feb 2025 | Custody Hack |

## Key Differentiators

| Feature | Existing Skills | This Skill |
|---|---|---|
| Detects contagion | After it happens | Before it spreads |
| Predicts sequence | No | Yes, ranked order |
| Estimates timing | No | Hours until impact |
| Impact scoring | No | 0.0–1.0 severity |
| Actionable signals | No | EXIT_NOW / REDUCE / WATCH |
| OI and funding aware | No | Amplifier / dampener |

## CMC Agent Hub Integration

This skill integrates with the CoinMarketCap Agent Hub:

- **MCP connection**: verified (`find_skill` returns 5 skills)
- **Skill execution**: verified (`execute_skill` works)
- **Architecture**: ready for CMC Pro tier

### Available CMC Skills

| Skill | Purpose |
|---|---|
| `daily_market_overview` | Daily crypto market brief |
| `crypto_macro_overview` | Macro regime validation |
| `btc_cross_asset_correlation` | BTC vs Nasdaq, DXY, Gold |
| `btc_etf_institutional_demand` | ETF flow + demand |
| `altcoin_breakout_scanner_spot` | Breakout detection |

## Installation

```bash
git clone https://github.com/ffffffffhugfadil/cross-asset-contagion-sequencer
cd cross-asset-contagion-sequencer
pip install -r requirements.txt
```

## Usage

```python
from core.sequencer import ContagionSequencer, AssetReturn
from data.fetcher_binance import get_returns_with_timestamps

# Fetch data
returns, timestamps = get_returns_with_timestamps('BTC', hours=72)

# Build source and targets
source = AssetReturn('BTC', returns, timestamps)
targets = [
    AssetReturn('ETH', returns_eth, timestamps_eth),
    AssetReturn('BNB', returns_bnb, timestamps_bnb),
]

# Run sequencer
sequencer = ContagionSequencer()
result = sequencer.run(source, targets, stress_threshold=-0.05)
print(result.to_dict())
```

## Quick Start

```bash
make setup
make demo
make test
```

## Disclaimer

Not financial advice. Backtests are historical and do not guarantee future results. Signals are research context only — not execution instructions.

## License

MIT — open for hackathon submission and future development.

---

**Built for BNB Hack 2026 — Track 2: Strategy Skills**
**Powered by CoinMarketCap Agent Hub · BNB Chain · Trust Wallet**
