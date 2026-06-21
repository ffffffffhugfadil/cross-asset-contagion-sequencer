cat > backtest/events/__init__.py << 'EOF'
"""
backtest/events package
Contains historical crash event data for backtesting.
"""

import os
import json
from typing import List, Dict, Optional

# Try to import individual event data (if files exist)
try:
    from .ftx_collapse_nov2022 import FTX_EVENT_DATA
except ImportError:
    FTX_EVENT_DATA = None

try:
    from .luna_crash_may2022 import LUNA_EVENT_DATA
except ImportError:
    LUNA_EVENT_DATA = None

try:
    from .crypto_winter_jun2022 import CRYPTO_WINTER_EVENT_DATA
except ImportError:
    CRYPTO_WINTER_EVENT_DATA = None

# New events (will be added as files are created)
# For now, they will be loaded from backtest/cache/backtest_results.json

# Event registry with metadata for all 12 events
EVENT_REGISTRY = [
    {
        "name": "FTX Collapse",
        "date": "2022-11-08",
        "source_asset": "BTC",
        "target_assets": ["ETH", "SOL", "BNB"],
        "category": "exchange_insolvency",
        "file": "ftx_collapse_nov2022.py",
        "data": FTX_EVENT_DATA
    },
    {
        "name": "LUNA/UST Depeg",
        "date": "2022-05-09",
        "source_asset": "LUNA",
        "target_assets": ["BTC", "ETH", "BNB", "SOL"],
        "category": "stablecoin_depeg",
        "file": "luna_crash_may2022.py",
        "data": LUNA_EVENT_DATA
    },
    {
        "name": "3AC/Celsius Contagion",
        "date": "2022-06-13",
        "source_asset": "BTC",
        "target_assets": ["ETH", "SOL", "BNB"],
        "category": "lender_contagion",
        "file": "crypto_winter_jun2022.py",
        "data": CRYPTO_WINTER_EVENT_DATA
    },
    # === NEW EVENTS (data loaded from backtest cache) ===
    {
        "name": "USDC Depeg / SVB",
        "date": "2023-03-10",
        "source_asset": "USDC",
        "target_assets": ["ETH", "SOL", "BNB"],
        "category": "bank_run_depeg",
        "file": None,
        "data": None
    },
    {
        "name": "COVID Black Thursday",
        "date": "2020-03-12",
        "source_asset": "BTC",
        "target_assets": ["ETH", "SOL", "BNB"],
        "category": "leverage_cascade",
        "file": None,
        "data": None
    },
    {
        "name": "SEC vs Binance/Coinbase",
        "date": "2023-06-05",
        "source_asset": "BTC",
        "target_assets": ["ETH", "SOL", "BNB"],
        "category": "regulatory_fud",
        "file": None,
        "data": None
    },
    {
        "name": "Ronin Bridge Hack",
        "date": "2022-03-23",
        "source_asset": "AXS",
        "target_assets": ["ETH", "SOL", "BNB"],
        "category": "bridge_exploit",
        "file": None,
        "data": None
    },
    {
        "name": "China Mining Ban + May 2021 Crash",
        "date": "2021-05-19",
        "source_asset": "BTC",
        "target_assets": ["ETH", "SOL", "BNB"],
        "category": "regulatory_shock",
        "file": None,
        "data": None
    },
    {
        "name": "China ICO Ban",
        "date": "2017-09-04",
        "source_asset": "BTC",
        "target_assets": ["ETH", "BNB"],
        "category": "regulatory_ban",
        "file": None,
        "data": None
    },
    {
        "name": "Poly Network Hack",
        "date": "2021-08-10",
        "source_asset": "ETH",
        "target_assets": ["BTC", "SOL", "BNB"],
        "category": "bridge_exploit",
        "file": None,
        "data": None
    },
    {
        "name": "Euler Finance Hack",
        "date": "2023-03-13",
        "source_asset": "EUL",
        "target_assets": ["ETH", "AAVE", "COMP"],
        "category": "defi_exploit",
        "file": None,
        "data": None
    },
    {
        "name": "Bybit Hack",
        "date": "2025-02-21",
        "source_asset": "ETH",
        "target_assets": ["BTC"],
        "category": "custody_hack",
        "file": None,
        "data": None
    },
]


def get_all_events() -> List[Dict]:
    """Get all 12 events with metadata."""
    return EVENT_REGISTRY


def get_event_by_name(name: str) -> Optional[Dict]:
    """Get event metadata by name."""
    for event in EVENT_REGISTRY:
        if event["name"] == name:
            return event
    return None


def get_events_by_category(category: str) -> List[Dict]:
    """Get all events in a category."""
    return [e for e in EVENT_REGISTRY if e.get("category") == category]


def load_event_data_from_cache() -> Dict:
    """Load backtest results from cache if available."""
    cache_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'cache', 'backtest_results.json'
    )
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                return data.get('results', {})
        except:
            pass
    
    return {}


# For backward compatibility
__all__ = [
    'FTX_EVENT_DATA',
    'LUNA_EVENT_DATA',
    'CRYPTO_WINTER_EVENT_DATA',
    'EVENT_REGISTRY',
    'get_all_events',
    'get_event_by_name',
    'get_events_by_category',
    'load_event_data_from_cache',
]
EOF
