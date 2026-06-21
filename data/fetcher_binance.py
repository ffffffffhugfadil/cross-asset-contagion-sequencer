# data/fetcher_binance.py
"""
Fetch historical OHLCV data from Binance Public API.
Free, no API key required.
"""

import json
import time
import ssl
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def fetch_hourly_klines(symbol: str, start_date: datetime, end_date: datetime, max_retries: int = 3) -> Tuple[List[float], List[str]]:
    """Fetch hourly OHLCV from Binance with retry logic."""
    cache_file = CACHE_DIR / f"binance_{symbol}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
    
    if cache_file.exists():
        with open(cache_file) as f:
            data = json.load(f)
        return data.get("returns", []), data.get("timestamps", [])
    
    symbol_full = f"{symbol}USDT" if not symbol.endswith("USDT") else symbol
    base_url = "https://api.binance.com/api/v3/klines"
    
    all_klines = []
    current_start = int(start_date.timestamp() * 1000)
    end_ms = int(end_date.timestamp() * 1000)
    
    retries = 0
    
    # Custom session with SSL fix
    session = requests.Session()
    session.verify = False  # Disable SSL verification
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    while current_start < end_ms and retries < max_retries:
        params = {
            "symbol": symbol_full,
            "interval": "1h",
            "limit": 1000,
            "startTime": current_start,
        }
        
        try:
            print(f"      Requesting {symbol_full}...")
            response = session.get(base_url, params=params, timeout=30)
            
            if response.status_code == 429:
                print(f"      Rate limited, waiting 5s...")
                time.sleep(5)
                retries += 1
                continue
            elif response.status_code == 418:
                print(f"      IP banned, waiting 60s...")
                time.sleep(60)
                retries += 1
                continue
            elif response.status_code != 200:
                print(f"      Binance error: {response.status_code}")
                time.sleep(2)
                retries += 1
                continue
            
            data = response.json()
            if not data:
                break
            
            all_klines.extend(data)
            last_close = data[-1][6]
            current_start = last_close + 1
            retries = 0
            
        except requests.exceptions.RequestException as e:
            print(f"      Request failed: {e}")
            time.sleep(2)
            retries += 1
    
    if not all_klines:
        print(f"    WARNING: No data for {symbol_full}")
        return [], []
    
    # Extract data
    closes = [float(k[4]) for k in all_klines]
    timestamps = [datetime.fromtimestamp(k[0]/1000).isoformat() for k in all_klines]
    
    # Calculate returns
    returns = []
    for i in range(1, len(closes)):
        if closes[i-1] != 0:
            returns.append((closes[i] - closes[i-1]) / closes[i-1])
        else:
            returns.append(0)
    timestamps = timestamps[1:]
    
    # Cache
    with open(cache_file, "w") as f:
        json.dump({"returns": returns, "timestamps": timestamps}, f)
    
    return returns, timestamps

def get_returns_with_timestamps(symbol: str, hours: int = 72) -> Tuple[List[float], List[str]]:
    """Fetch last N hours."""
    end = datetime.now()
    start = end - timedelta(hours=hours)
    return fetch_hourly_klines(symbol, start, end)
