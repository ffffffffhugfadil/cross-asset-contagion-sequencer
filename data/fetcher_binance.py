"""
data/fetcher_binance.py
========================
Fetch historical OHLCV data from Binance Public API.
No API key required — completely free for hackathon use.

Binance provides hourly candles for all major trading pairs.
This is used as fallback / primary source for historical data
since CMC Basic Plan does not support historical endpoints.

Usage:
    from data.fetcher_binance import get_historical_returns
    
    returns = get_historical_returns("BTC", hours=72)
    # returns: list of hourly percentage changes
"""

import requests
from datetime import datetime
from typing import List, Dict, Optional

# Mapping from CMC symbol to Binance trading pair
BINANCE_SYMBOLS = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "BNB": "BNBUSDT",
    "CAKE": "CAKEUSDT",
    "LINK": "LINKUSDT",
    "ADA": "ADAUSDT",
    "SOL": "SOLUSDT",
    "DOGE": "DOGEUSDT",
    "XRP": "XRPUSDT",
    "MATIC": "MATICUSDT",
}

# Reverse mapping for display
REVERSE_MAP = {v: k for k, v in BINANCE_SYMBOLS.items()}


def get_binance_klines(
    symbol: str,
    interval: str = "1h",
    limit: int = 100
) -> List[Dict]:
    """
    Get OHLCV klines from Binance API.
    
    Args:
        symbol: Trading pair (e.g., "BTCUSDT")
        interval: "1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"
        limit: Number of candles to return (max 1000)
    
    Returns:
        List of candles with keys:
        - timestamp (ms)
        - datetime (ISO string)
        - open, high, low, close, volume
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[Binance Error] Failed to fetch {symbol}: {e}")
        return []
    
    candles = []
    for item in data:
        timestamp_ms = item[0]
        dt = datetime.fromtimestamp(timestamp_ms / 1000).isoformat() + "Z"
        
        candles.append({
            "timestamp": timestamp_ms,
            "datetime": dt,
            "open": float(item[1]),
            "high": float(item[2]),
            "low": float(item[3]),
            "close": float(item[4]),
            "volume": float(item[5]),
            "close_time": item[6],
            "quote_volume": float(item[7]),
            "trades": item[8],
        })
    
    return candles


def get_historical_returns(
    symbol: str,
    hours: int = 72,
    interval: str = "1h"
) -> List[float]:
    """
    Get hourly percentage returns for a token.
    
    Args:
        symbol: CMC-style symbol (BTC, ETH, BNB, etc.)
        hours: Number of hourly returns to fetch
        interval: Should be "1h" for hourly data
    
    Returns:
        List of hourly percentage returns (e.g., [0.002, -0.005, ...])
        Oldest first, newest last.
    """
    if symbol not in BINANCE_SYMBOLS:
        print(f"[Warning] No Binance mapping for {symbol}. Available: {list(BINANCE_SYMBOLS.keys())}")
        return []
    
    binance_symbol = BINANCE_SYMBOLS[symbol]
    candles = get_binance_klines(binance_symbol, interval=interval, limit=hours + 1)
    
    if len(candles) < 2:
        return []
    
    returns = []
    for i in range(1, len(candles)):
        prev_close = candles[i-1]["close"]
        curr_close = candles[i]["close"]
        ret = (curr_close - prev_close) / prev_close
        returns.append(ret)
    
    return returns


def get_historical_candles(
    symbol: str,
    hours: int = 72,
    interval: str = "1h"
) -> List[Dict]:
    """
    Get full candle data including timestamps and OHLC.
    
    Returns list of candles with datetime and close price,
    suitable for building AssetReturn objects.
    """
    if symbol not in BINANCE_SYMBOLS:
        return []
    
    binance_symbol = BINANCE_SYMBOLS[symbol]
    candles = get_binance_klines(binance_symbol, interval=interval, limit=hours)
    
    result = []
    for c in candles:
        result.append({
            "timestamp": c["datetime"],
            "close": c["close"],
            "volume": c["volume"],
            "open": c["open"],
            "high": c["high"],
            "low": c["low"],
        })
    
    return result


def get_multi_asset_returns(
    symbols: List[str],
    hours: int = 72,
) -> Dict[str, List[float]]:
    """
    Fetch hourly returns for multiple assets.
    
    Returns:
        Dict mapping symbol -> list of returns (oldest first)
    """
    results = {}
    for symbol in symbols:
        print(f"[Binance] Fetching {symbol} ({hours} hours)...")
        returns = get_historical_returns(symbol, hours=hours)
        if returns:
            results[symbol] = returns
        else:
            print(f"[Warning] Failed to fetch {symbol}")
            results[symbol] = []
    return results


def get_returns_with_timestamps(
    symbol: str,
    hours: int = 72,
) -> tuple[List[float], List[str]]:
    """
    Get returns and aligned timestamps for AssetReturn dataclass.
    
    Returns:
        (returns_list, timestamps_list)
        Timestamps correspond to the END of each hourly period.
    """
    if symbol not in BINANCE_SYMBOLS:
        return [], []
    
    candles = get_binance_klines(BINANCE_SYMBOLS[symbol], interval="1h", limit=hours + 1)
    
    if len(candles) < 2:
        return [], []
    
    returns = []
    timestamps = []
    
    for i in range(1, len(candles)):
        prev_close = candles[i-1]["close"]
        curr_close = candles[i]["close"]
        ret = (curr_close - prev_close) / prev_close
        returns.append(ret)
        timestamps.append(candles[i]["datetime"])  # timestamp of current candle
    
    return returns, timestamps


# Quick test

if __name__ == "__main__":
    print("=== Testing Binance API (Free, no API key) ===\n")
    
    # Test 1: Single asset returns
    print("1. BTC hourly returns (last 5 hours):")
    returns = get_historical_returns("BTC", hours=5)
    for i, r in enumerate(returns):
        print(f"   Hour {i+1}: {r*100:.4f}%")
    
    # Test 2: Timestamps
    print("\n2. BTC returns with timestamps:")
    rets, ts = get_returns_with_timestamps("BTC", hours=3)
    for r, t in zip(rets, ts):
        print(f"   {t}: {r*100:.4f}%")
    
    # Test 3: Multiple assets
    print("\n3. Multiple assets (last 24h returns):")
    multi = get_multi_asset_returns(["BTC", "ETH", "BNB"], hours=24)
    for sym, rets in multi.items():
        if rets:
            total_24h = sum(rets) * 100
            print(f"   {sym}: 24h change = {total_24h:.2f}%")
    
    print("\n=== Binance API OK ===")