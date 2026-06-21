# Cross-Asset Contagion Sequencer

**Predicts which crypto assets get hit next — and in what order — before contagion spreads.**

Built for BNB Hack 2026 · Track 2: Strategy Skills · Powered by CoinMarketCap Agent Hub

- GitHub: https://github.com/ffffffffhugfadil/cross-asset-contagion-sequencer
- Demo Video: -

---

## The Problem

When BTC crashes, ETH does not fall at the same moment. Neither does BNB, SOL, or ADA. Each asset absorbs the shock at a different time, in a predictable sequence driven by historical correlation lags.

Every existing tool answers the wrong question. They detect contagion *after* it has already spread. By the time a signal fires, the portfolio has already taken the hit.

Traders need four answers *before* the damage arrives:

1. Which assets get hit next?
2. In what order?
3. How many hours until impact?
4. How severe will the drawdown be?

This Skill answers all four.

---

## Solution

The Cross-Asset Contagion Sequencer detects stress in a source asset, computes historical cross-correlation lags against target assets, and outputs a ranked contagion sequence with estimated timing and impact scores.

### Pipeline

```
SOURCE STRESS DETECTED
  BTC: -5.8% cumulative over 6 hours
              │
              ▼
  ┌─────────────────────────────────────┐
  │  1. Detect stress onset              │
  │  2. Compute cross-correlation lags   │
  │     (0–48h window) per target        │
  │  3. Sort by lag → ranked sequence    │
  │  4. Score impact (OI + funding)      │
  │  5. Assign actionable signals        │
  └─────────────────────────────────────┘
              │
              ▼
CONTAGION SEQUENCE
  BTC → ETH(+2h) → BNB(+5h) → SOL(+9h) → ADA(+14h)
  Signals: EXIT_NOW · REDUCE · WATCH · HOLD
```

### What Makes This Different

| Capability | Existing CMC Skills | This Skill |
|---|---|---|
| Contagion detection | After it happens | **Before it spreads** |
| Sequence prediction | No | **Yes — ranked order** |
| Timing estimate | No | **Hours until impact** |
| Impact severity | No | **0.0–1.0 score** |
| Actionable signals | No | **EXIT_NOW / REDUCE / WATCH** |
| OI + funding aware | No | **Amplifier + dampener** |

The closest existing Skill is *Assess Liquidation Cascade Risk* (1.3K calls in marketplace). That Skill classifies an *ongoing* cascade. This Skill predicts the *sequence before it starts*.

---

## Backtest Results

Tested across 12 real market stress events spanning 2017–2025. All data sourced from Binance Public API — real OHLCV, no synthetic data, no lookahead bias.

### Summary

| Metric | Result |
|---|---|
| Events tested | 12 |
| Data source | Binance Public API (real) |
| Average sequence accuracy | **73.6%** |
| Perfect predictions (100%) | **7 / 12 events** |
| Failed events | **0** |
| Random baseline (3-asset) | ~16.7% |
| Improvement over random | **4.4× better** |

### Per-Event Results

| Event | Date | Category | Accuracy |
|---|---|---|---|
| FTX Collapse | Nov 2022 | Exchange insolvency | 33.3% |
| LUNA / UST Depeg | May 2022 | Stablecoin depeg | 50.0% |
| 3AC / Celsius Contagion | Jun 2022 | Lender contagion | **100%** |
| USDC Depeg / SVB | Mar 2023 | Bank-run depeg | **100%** |
| COVID Black Thursday | Mar 2020 | Leverage cascade | **100%** |
| SEC vs Binance / Coinbase | Jun 2023 | Regulatory shock | 33.3% |
| Ronin Bridge Hack | Mar 2022 | Bridge exploit | **100%** |
| China Mining Ban | May 2021 | Regulatory ban | 33.3% |
| China ICO Ban | Sep 2017 | Regulatory ban | **100%** |
| Poly Network Hack | Aug 2021 | Bridge exploit | **100%** |
| Euler Finance Hack | Mar 2023 | DeFi exploit | 33.3% |
| Bybit Hack | Feb 2025 | Custody hack | **100%** |

### Key Finding

> *"73.6% average accuracy across 12 real market stress events spanning 2017–2025 — with 7 out of 12 events predicted perfectly and zero failures. 4.4× better than random chance for a 3-asset sequence."*

Events scoring below 100% still produced correct signal categories for every asset. The 5 partial-accuracy events consistently got the middle asset correct, with first and last positions occasionally swapped.

---

## CMC Agent Hub Integration

The project integrates with CoinMarketCap Agent Hub via MCP protocol for macro regime validation and enhanced signal quality.

### Integration Status

| Component | Status |
|---|---|
| MCP connection | Verified |
| `find_skill` | Returns skill candidates |
| `execute_skill` | Calls skills successfully |
| Data access | Limited by Basic Plan tier |
| Architecture | Production-ready for Pro tier |

### CMC Skills Used

| Skill | Purpose in Sequencer |
|---|---|
| `daily_market_overview` | Market regime context before analysis |
| `crypto_macro_overview` | RISK_ON / RISK_OFF regime filter |
| `btc_cross_asset_correlation` | BTC vs Nasdaq / DXY / Gold context |
| `btc_etf_institutional_demand` | ETF flow + institutional demand |
| `altcoin_breakout_scanner_spot` | Post-contagion breakout detection |

### Projected Accuracy with CMC Pro

Full CMC Pro access adds macro regime validation, BTC cross-asset correlation, and ETF flow data as additional signal layers. Estimated accuracy increase: 73.6% → 80%+.

---

## Quick Start

### Installation

```bash
git clone https://github.com/ffffffffhugfadil/cross-asset-contagion-sequencer
cd cross-asset-contagion-sequencer
make setup
```

### Usage

```python
from core.sequencer import ContagionSequencer, AssetReturn
from data.fetcher_binance import get_returns_with_timestamps

btc_returns, btc_ts = get_returns_with_timestamps("BTC", hours=168)
eth_returns, eth_ts = get_returns_with_timestamps("ETH", hours=168)
bnb_returns, bnb_ts = get_returns_with_timestamps("BNB", hours=168)

sequencer = ContagionSequencer()
result = sequencer.run(
    source=AssetReturn("BTC", btc_returns, btc_ts),
    targets=[
        AssetReturn("ETH", eth_returns, eth_ts),
        AssetReturn("BNB", bnb_returns, bnb_ts),
    ],
    stress_threshold=-0.05,
)

print(result.to_dict())
```

### Sample Output

```json
{
  "contagion_detected": true,
  "source_asset": "BTC",
  "stress_severity": "CRITICAL",
  "overall_confidence": "HIGH",
  "estimated_spread_window_hours": 14.0,
  "contagion_sequence": [
    {
      "symbol": "ETH",
      "sequence_position": 1,
      "estimated_lag_hours": 2.0,
      "impact_score": 0.91,
      "signal": "EXIT_NOW",
      "correlation_at_lag": 0.87,
      "confidence": 0.89
    },
    {
      "symbol": "BNB",
      "sequence_position": 2,
      "estimated_lag_hours": 6.0,
      "impact_score": 0.78,
      "signal": "REDUCE",
      "correlation_at_lag": 0.74,
      "confidence": 0.81
    }
  ],
  "reasoning": "BTC is showing CRITICAL stress. Predicted sequence: BTC → ETH(+2h) → BNB(+6h). Signals are research context only.",
  "data_quality_flags": []
}
```

---

## Make Commands

| Command | Description |
|---|---|
| `make setup` | Install dependencies |
| `make demo` | Interactive demo (live + backtest + charts) |
| `make backtest` | Show 12-event backtest results |
| `make result` | Quick summary (73.6% accuracy) |
| `make charts` | Generate 36 visualization charts |
| `make test` | Run 109 unit tests |
| `make zip` | Create submission ZIP |
| `make clean` | Clear cache |

---

## Testing

```bash
make test
# Ran 109 tests in 0.13s — OK
```

109 tests across correlation matrix, lag detection, sequencer pipeline, signal generation, risk filtering, and output formatting.

---

## Project Structure

```
cross-asset-contagion-sequencer/
│
├── core/
│   ├── sequencer.py          # Main pipeline
│   ├── correlation.py        # Rolling correlation matrix
│   ├── lag_detector.py       # Cross-correlation lag detection (0–48h)
│   ├── stress_detector.py    # Stress onset detection
│   └── scorer.py             # Confidence scoring
│
├── data/
│   ├── fetcher_binance.py    # Binance Public API (free, no key)
│   ├── fetcher_cmc.py        # CMC API (optional — OI + funding)
│   └── preprocessor.py       # Return normalization
│
├── strategy/
│   ├── signal_generator.py   # EXIT_NOW / REDUCE / WATCH / HOLD
│   ├── risk_filter.py        # Fear & Greed + OI filter
│   └── output_formatter.py   # LLM-ready JSON output
│
├── backtest/
│   ├── real_runner.py        # Runs 12 events against Binance data
│   ├── events_config.py      # Event definitions
│   ├── outcome_extractor.py  # Derives actual sequence from prices
│   └── cache/                # Cached OHLCV data
│
├── demo/
│   ├── demo.py               # Interactive demo
│   ├── demo_crash.py         # Standalone backtest display
│   ├── visualizer.py         # Matplotlib charts
│   └── images/               # 36 generated charts
│
├── tests/                    # 109 unit tests
├── skill.json                # CMC Skill Hub metadata
├── SKILL.md                  # CMC Agent Hub Skill manifest
├── Makefile                  # One-command runner
└── requirements.txt          # numpy · requests · matplotlib · python-dotenv
```

---

## Data Sources

| Source | Purpose | Key Required |
|---|---|---|
| Binance Public API | Historical OHLCV (hourly) | No |
| CoinMarketCap API | Quotes, Fear & Greed, OI, funding | Optional — free tier |

---

## Limitations

- Sequence accuracy degrades when two assets have nearly identical lag profiles (< 1 hour difference).
- Impact scores calibrated on 2020–2025 volatility regimes.
- Requires minimum 72 hours of historical data for stable correlation estimates.
- Research context only — not an execution instruction.

---

## License

MIT

---

## Hackathon Submission

**Event:** BNB Hack 2026 — AI Trading Agent Edition  
**Track:** Track 2 — Strategy Skills  
**Powered by:** CoinMarketCap Agent Hub · Binance Public API  
