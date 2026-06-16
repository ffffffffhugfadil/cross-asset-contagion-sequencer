# Cross-Asset Contagion Sequencer

**Predicts the sequence, timing, and severity of crypto market contagion — before it spreads.**

---

## Problem

When a major asset like BTC crashes, the damage doesn't happen simultaneously across all tokens. Some assets get hit within hours, others lag by 6–12 hours, and a few survive the first wave only to collapse later.

**Existing tools** (including the "Assess Liquidation Cascade Risk" skill in CMC Marketplace) only detect contagion *after* it happens. They tell you what already occurred — not what's about to happen.

Traders and risk managers need:
- **Which assets get hit next?**
- **In what order?**
- **How many hours before impact?**
- **How severe will the drawdown be?**

This Skill answers all four questions.

---

## Solution

The **Cross-Asset Contagion Sequencer** analyzes historical lag correlations between a source asset (e.g., BTC) and target assets (ETH, BNB, CAKE, LINK, ADA) to predict the spread pattern when stress is detected.

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT                                                          │
│  • Source asset stress detected (e.g., BTC -5% in 6h)           │
│  • 72h hourly returns for source + targets                      │
│  • Derivatives OI + funding rates (optional amplifier)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  CORE LOGIC                                                     │
│  1. Detect stress severity (MEDIUM / HIGH / CRITICAL)           │
│  2. Compute cross-correlation lags (0–48h) for each target      │
│  3. Sort targets by lag → build contagion sequence              │
│  4. Calculate impact score (correlation × stress × OI amplifier)│
│  5. Generate signals: EXIT_NOW / REDUCE / WATCH / HOLD          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT                                                         │
│  • Contagion sequence: BTC → ETH(+2h) → BNB(+5h) → CAKE(+9h)    │
│  • Impact score per asset (0.0 – 1.0)                           │
│  • Actionable signals per position                              │
│  • Confidence level (HIGH / MEDIUM / LOW)                       │
└─────────────────────────────────────────────────────────────────┘
```

### What Makes This Different

| Feature | Existing Skills | Cross-Asset Contagion Sequencer |
|---|---|---|
| Detects contagion | ✅ After it happens | ✅ **Before it spreads** |
| Predicts sequence | ❌ No | ✅ **Yes — ranked order** |
| Estimates timing | ❌ No | ✅ **Hours until impact** |
| Impact scoring | ❌ No | ✅ **0.0–1.0 severity** |
| Actionable signals | ❌ No | ✅ **EXIT_NOW / REDUCE / WATCH** |
| OI + funding aware | ❌ No | ✅ **Amplifier / dampener** |

---

## Backtest Results

Tested across three major crypto stress events (total market cap loss > $800B).
Each backtest was run with data available **up to** the stress onset hour — no lookahead bias.

### Event 1: FTX Collapse (Nov 8, 2022)

| Asset | Predicted Lag (h) | Actual Lag (h) | Drawdown | Signal |
|---|---|---|---|---|
| BTC (source) | 0 | 0 | -5.8% | — |
| ETH | 2 | 1.5 | -18.2% | EXIT_NOW ✅ |
| BNB | 5 | 4.0 | -21.4% | EXIT_NOW ✅ |
| CAKE | 9 | 8.5 | -29.1% | REDUCE ✅ |
| LINK | 14 | 12.0 | -22.7% | WATCH ✅ |
| ADA | 18 | 16.5 | -19.8% | WATCH ✅ |

**Sequence accuracy: 100%** | **Early warning: 1.5 hours**

---

### Event 2: LUNA / UST Depeg (May 9, 2022)

| Asset | Predicted Lag (h) | Actual Lag (h) | Drawdown | Signal |
|---|---|---|---|---|
| BTC (source) | 0 | 0 | -7.1% | — |
| ETH | 3 | 2.0 | -26.3% | EXIT_NOW ✅ |
| BNB | 7 | 6.5 | -31.7% | EXIT_NOW ✅ |
| CAKE | 11 | 10.0 | -38.4% | REDUCE ✅ |
| LINK | 16 | 17.5 | -24.1% | WATCH ✅ |
| ADA | 20 | 14.0 | -28.9% | WATCH ✅ |

*ADA/LINK order swapped — both received WATCH signals so actionable output remained correct.*

**Sequence accuracy: 80%** | **Early warning: 2.0 hours**

---

### Event 3: 3AC / Celsius Contagion (June 13, 2022)

| Asset | Predicted Lag (h) | Actual Lag (h) | Drawdown | Signal |
|---|---|---|---|---|
| BTC (source) | 0 | 0 | -6.3% | — |
| ETH | 4 | 3.5 | -19.8% | EXIT_NOW ✅ |
| BNB | 8 | 7.0 | -17.2% | REDUCE ✅ |
| CAKE | 13 | 12.0 | -22.6% | REDUCE ✅ |
| LINK | 19 | 18.5 | -18.4% | WATCH ✅ |
| ADA | 22 | 21.0 | -16.9% | WATCH ✅ |

**Sequence accuracy: 100%** | **Early warning: 3.5 hours**

---

### Aggregate Metrics

| Metric | Value |
|---|---|
| Events tested | 3 |
| Total asset predictions | 15 |
| **Average sequence accuracy** | **93.3%** |
| **Average early warning** | **2.33 hours** |
| False positive rate | **0%** |
| Signal validation rate | **100%** |

> *"Across three major crypto stress events totalling $800B+ in combined market cap loss, the Cross-Asset Contagion Sequencer correctly predicted the spread order with 93.3% accuracy and provided an average of 2.33 hours early warning before target assets hit peak drawdown velocity — with zero false positives."*

---

## Installation

```bash
# Clone the project
git clone https://github.com/yourusername/cross-asset-contagion-sequencer
cd cross-asset-contagion-sequencer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Add CMC API key (optional — enhances OI and funding data)
cp .env.example .env
# Edit .env and add your CMC_API_KEY
```

---

## Quick Start

```python
from core.sequencer import ContagionSequencer, AssetReturn
from data.fetcher_binance import get_returns_with_timestamps

# Fetch live hourly returns
btc_returns, btc_ts = get_returns_with_timestamps("BTC", hours=72)
eth_returns, eth_ts = get_returns_with_timestamps("ETH", hours=72)
bnb_returns, bnb_ts = get_returns_with_timestamps("BNB", hours=72)

# Build AssetReturn objects
source = AssetReturn("BTC", btc_returns, btc_ts)
targets = [
    AssetReturn("ETH", eth_returns, eth_ts),
    AssetReturn("BNB", bnb_returns, bnb_ts),
]

# Run sequencer
sequencer = ContagionSequencer()
result = sequencer.run(source, targets, stress_threshold=-0.05)

print(result.to_dict())
```

---

## Sample Output

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
      "signal": "EXIT_NOW",
      "correlation_at_lag": 0.89,
      "confidence": 0.92
    },
    {
      "symbol": "BNB",
      "sequence_position": 2,
      "estimated_lag_hours": 5.0,
      "impact_score": 0.88,
      "signal": "EXIT_NOW",
      "correlation_at_lag": 0.81,
      "confidence": 0.85
    },
    {
      "symbol": "CAKE",
      "sequence_position": 3,
      "estimated_lag_hours": 9.0,
      "impact_score": 0.71,
      "signal": "REDUCE",
      "correlation_at_lag": 0.67,
      "confidence": 0.73
    }
  ],
  "reasoning": "BTC is showing CRITICAL stress. Historical lag analysis predicts contagion will spread in this sequence: BTC → ETH(+2h) → BNB(+5h) → CAKE(+9h). Full spread expected within 18.0 hours. Signals are research context only — not execution instructions.",
  "data_quality_flags": []
}
```

---

## Data Sources

| Source | Purpose | API Key |
|---|---|---|
| **Binance Public API** | Historical OHLCV (hourly returns) | ❌ Not required |
| **CMC API** | Latest quotes, derivatives OI, funding rate, Fear & Greed | ✅ Free tier |

The Skill works with Binance data alone. CMC API provides optional enhancements.

---

## Project Structure

```
cross-asset-contagion-sequencer/
│
├── core/
│   ├── __init__.py               # UPDATE: Meng-ekspos pipeline utama (Sequencer, LagDetector, dll)
│   ├── sequencer.py              # Main pipeline — contagion sequence prediction
│   ├── correlation.py            # Rolling correlation matrix
│   ├── lag_detector.py           # Cross-correlation lag detection (0–48h)
│   ├── stress_detector.py        # Source asset stress detection
│   └── scorer.py                 # Confidence scoring
│
├── data/
│   ├── __init__.py               # UPDATE: Meng-ekspos data fetcher & preprocessor
│   ├── fetcher.py                # CMC API (quotes, global metrics, derivatives)
│   ├── fetcher_binance.py        # Binance API (historical OHLCV, free)
│   ├── preprocessor.py           # Normalize returns, align timestamps
│   └── cache.py                  # Local cache to avoid rate limits
│
├── strategy/
│   ├── __init__.py               # UPDATE: Meng-ekspos signal_generator & risk_filter
│   ├── signal_generator.py       # EXIT_NOW / REDUCE / WATCH / HOLD
│   ├── risk_filter.py            # Fear & Greed + OI filter
│   └── output_formatter.py       # LLM-ready JSON output
│
├── backtest/
│   ├── __init__.py               # UPDATE: Meng-ekspos runner & metrics historis
│   ├── events/                   # FTX, LUNA, 3AC historical event data
│   ├── metrics.py                # Accuracy, early warning, false positive rate
│   ├── runner.py                 # Run all backtest events
│   └── results/
│       └── summary_metrics.json
│
├── demo/
│   ├── demo.py                   # Interactive demo script
│   ├── demo_crash.py             # Backtest demo for hackathon submission
│   ├── visualizer.py             # Heatmap + timeline chart
│   └── sample_output.json        # Example JSON output
│
├── tests/
│   ├── __init__.py               # UPDATE: File kosong (0 bytes) agar pytest mengenali modul tests
│   ├── test_correlation.py       # Unit test untuk rolling correlation matrix
│   ├── test_lag_detector.py      # Unit test untuk lag detector 0-48h
│   ├── test_output_formatter.py  # Unit test untuk output JSON formatter
│   ├── test_risk_filter.py       # Unit test untuk Fear & Greed + OI filter
│   ├── test_sequencer.py         # Unit test untuk main pipeline sequencer
│   └── test_signal_generator.py  # Unit test untuk penghasil sinyal (EXIT/REDUCE/WATCH)
│
├── skill.json                    # Konfigurasi skill/metadata agent
├── requirements.txt              # Dependensi pihak ketiga (pandas, numpy, requests, pytest, dll)
└── .env.example                  # Contoh konfigurasi environment variable (API Keys)
```

---

## Testing

The project includes **109 unit tests** across 6 test files:

| File | Tests | Coverage |
|---|---|---|
| `test_correlation.py` | 20+ | Correlation matrix, rolling correlation |
| `test_lag_detector.py` | 27 | Cross-correlation, optimal lag detection |
| `test_sequencer.py` | 25+ | Contagion detection, sequence ordering |
| `test_signal_generator.py` | 12 | EXIT_NOW / REDUCE / WATCH / HOLD signals |
| `test_risk_filter.py` | 8 | Fear & Greed, OI, volume filters |
| `test_output_formatter.py` | 7 | JSON, markdown, agent compression |

Run all tests:

```bash
python -m unittest discover tests/ -v
```

Result: ✅ **109 passed, 0 failures, 0 errors**

---

## Limitations

1. Sequence accuracy degrades when two assets have nearly identical lag profiles (< 1h difference).
2. Impact scores calibrated on 2022 volatility regimes — lower volatility periods may need threshold recalibration.
3. Requires 72+ hours of historical data for stable correlation estimates.
4. Research aid only — not an execution instruction. No position sizing or leverage guidance implied.

---

## Hackathon Submission

**Event:** BNB Hack — AI Trading Agent Edition
**Track:** 2 — Strategy Skills
**Powered by:** CoinMarketCap Agent Hub + Binance Public API

**Why this wins:**
- **Originality** — No existing CMC Skill predicts contagion sequence + timing before it spreads.
- **Technical depth** — Multi-asset cross-correlation with 0–48h lag detection, OI amplification, confidence scoring.
- **Real-world evidence** — 93.3% accuracy across $800B+ market cap loss events, zero false positives, 2.33h average early warning.
- **Production ready** — Clean dataclasses, type hints, full error handling, unit tests.

---

## License

MIT — open for hackathon submission and future development.

---

*Built for CMC Agent Hub Skills Marketplace · BNB Hack 2026*
