"""
data package - Data fetching from Binance and CMC APIs
"""

from .fetcher_binance import (
    get_binance_klines,
    get_historical_returns,
    get_historical_candles,
    get_multi_asset_returns,
    get_returns_with_timestamps,
    BINANCE_SYMBOLS,
)

from .preprocessor import (
    build_asset_returns,
    prepare_sequencer_input,
)

__all__ = [
    # Binance fetcher
    "get_binance_klines",
    "get_historical_returns",
    "get_historical_candles",
    "get_multi_asset_returns",
    "get_returns_with_timestamps",
    "BINANCE_SYMBOLS",
    # Preprocessor
    "build_asset_returns",
    "prepare_sequencer_input",
]
