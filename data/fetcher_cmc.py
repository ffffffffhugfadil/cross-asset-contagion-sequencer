# data/fetcher_cmc.py
"""
Fetch historical OHLCV data from CoinMarketCap API.
Free tier: 15,000 credits/month, 50 requests/min.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional

import requests

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def fetch_cmc_ohlcv(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    api_key: str,
    interval: str = "1h"
) -> Tuple[List[float], List[str]]:
    """
    Fetch OHLCV data from CoinMarketCap API.
    
    Args:
        symbol: Asset symbol (e.g., "BTC", "ETH")
        start_date: Start datetime
        end_date: End datetime
        api_key: CMC Pro API key
        interval: Time interval ("1h", "1d", etc.)
    
    Returns:
        Tuple of (returns, timestamps)
    """
    # Cache check
    cache_file = CACHE_DIR / f"cmc_{symbol}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
    
    if cache_file.exists():
        with open(cache_file) as f:
            data = json.load(f)
        return data["returns"], data["timestamps"]
    
    url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/ohlcv/historical"
    headers = {
        'X-CMC_PRO_API_KEY': api_key,
        'Accept': 'application/json'
    }
    
    params = {
        'symbol': symbol,
        'time_period': interval,
        'time_start': start_date.isoformat() + 'Z',
        'time_end': end_date.isoformat() + 'Z',
        'count': 2000  # Max 2000 candles per request
    }
    
    print(f"    Fetching {symbol} from CMC ({start_date.date()} to {end_date.date()})...")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data['status']['error_code'] != 0:
            raise Exception(f"CMC API Error: {data['status']['error_message']}")
        
        # Extract quotes
        quotes = data['data']['quotes']
        quotes.sort(key=lambda x: x['time_open'])
        
        closes = []
        timestamps = []
        
        for quote in quotes:
            closes.append(quote['quote']['USD']['close'])
            timestamps.append(quote['time_open'])
        
        # Calculate returns
        returns = []
        for i in range(1, len(closes)):
            if closes[i-1] != 0:
                ret = (closes[i] - closes[i-1]) / closes[i-1]
            else:
                ret = 0
            returns.append(ret)
        
        timestamps = timestamps[1:]  # Align with returns
        
        # Cache
        with open(cache_file, 'w') as f:
            json.dump({"returns": returns, "timestamps": timestamps}, f)
        
        return returns, timestamps
    
    except requests.exceptions.RequestException as e:
        print(f"    ERROR: CMC request failed: {e}")
        raise
    except Exception as e:
        print(f"    ERROR: {e}")
        raise

def get_returns_with_timestamps(symbol: str, hours: int = 72) -> Tuple[List[float], List[str]]:
    """Fetch last N hours (convenience function)."""
    end = datetime.now()
    start = end - timedelta(hours=hours)
    
    api_key = os.environ.get('CMC_PRO_API_KEY')
    if not api_key:
        raise ValueError("CMC_PRO_API_KEY not set in environment")
    
    return fetch_cmc_ohlcv(symbol, start, end, api_key)
