from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ContagionEvent:
    name: str
    date: str
    source_asset: str
    target_assets: List[str]
    lookback_hours: int = 72
    stress_threshold: float = -0.05
    category: str = "other"
    description: str = ""

EVENTS = [
    ContagionEvent(
        name="FTX Collapse",
        date="2022-11-08",
        source_asset="BTC",
        target_assets=["ETH", "SOL", "BNB"],
        stress_threshold=-0.035,
        category="exchange_insolvency",
    ),
    ContagionEvent(
        name="LUNA/UST Depeg",
        date="2022-05-09",
        source_asset="LUNA",
        target_assets=["BTC", "ETH", "BNB", "SOL"],
        stress_threshold=-0.04,
        category="stablecoin_depeg",
    ),
    ContagionEvent(
        name="3AC/Celsius Contagion",
        date="2022-06-13",
        source_asset="BTC",
        target_assets=["ETH", "SOL", "BNB"],
        stress_threshold=-0.035,
        category="lender_contagion",
    ),
    ContagionEvent(
        name="USDC Depeg / SVB",
        date="2023-03-10",
        source_asset="USDC",
        target_assets=["ETH", "SOL", "BNB"],
        stress_threshold=-0.015,
        category="bank_run_depeg",
    ),
    ContagionEvent(
        name="COVID Black Thursday",
        date="2020-03-12",
        source_asset="BTC",
        target_assets=["ETH", "SOL", "BNB"],
        stress_threshold=-0.02,
        category="leverage_cascade",
    ),
    ContagionEvent(
        name="SEC vs Binance/Coinbase",
        date="2023-06-05",
        source_asset="BTC",
        target_assets=["ETH", "SOL", "BNB"],
        stress_threshold=-0.03,
        category="regulatory_fud",
    ),
    ContagionEvent(
        name="Ronin Bridge Hack",
        date="2022-03-23",
        source_asset="AXS",
        target_assets=["ETH", "SOL", "BNB"],
        stress_threshold=-0.03,
        category="bridge_exploit",
    ),
    ContagionEvent(
        name="China Mining Ban + May 2021 Crash",
        date="2021-05-19",
        source_asset="BTC",
        target_assets=["ETH", "SOL", "BNB"],
        stress_threshold=-0.03,
        category="regulatory_shock",
    ),
    ContagionEvent(
        name="China ICO Ban",
        date="2017-09-04",
        source_asset="BTC",
        target_assets=["ETH", "BNB"],
        stress_threshold=-0.04,
        category="regulatory_ban",
    ),
    ContagionEvent(
        name="Poly Network Hack",
        date="2021-08-10",
        source_asset="ETH",
        target_assets=["BTC", "SOL", "BNB"],
        stress_threshold=-0.025,
        category="bridge_exploit",
    ),
    ContagionEvent(
        name="Euler Finance Hack",
        date="2023-03-13",
        source_asset="EUL",
        target_assets=["ETH", "AAVE", "COMP"],
        stress_threshold=-0.05,
        category="defi_exploit",
    ),
    ContagionEvent(
        name="Bybit Hack",
        date="2025-02-21",
        source_asset="ETH",
        target_assets=["BTC"],
        stress_threshold=-0.02,
        category="custody_hack",
    ),
]

def get_all_events():
    return EVENTS
