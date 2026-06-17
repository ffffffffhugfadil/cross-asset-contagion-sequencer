"""
test_data.py
============
Test script to fetch and display real-time market data from Binance and CMC APIs.

Displays 24-hour returns for multiple assets from Binance (free, no API key)
and latest quotes from CMC API (optional, requires API key).
"""

from data.fetcher_binance import get_returns_with_timestamps
from data.fetcher import CMCFetcher

# Assets to display
ASSETS = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'CAKE', 'LINK']

print('=' * 60)
print('📊 REAL-TIME MARKET DATA')
print('=' * 60)

# ============================================
# 1. BINANCE API (FREE, NO API KEY REQUIRED)
# ============================================
print('\n' + '=' * 60)
print('📡 BINANCE API - 24h Returns')
print('=' * 60)
print(f'  Source: Binance Public API (free, no API key)')
print('-' * 60)

for symbol in ASSETS:
    returns, ts = get_returns_with_timestamps(symbol, hours=24)
    if returns:
        total_change = sum(returns) * 100
        last_price = returns[-1]
        print(f'\n🔹 {symbol}')
        print(f'   Data points: {len(returns)} hours')
        print(f'   Last price: ${last_price:.4f}')
        print(f'   24h change: {total_change:.2f}%')
    else:
        print(f'\n❌ {symbol}: Failed to fetch data')

# ============================================
# 2. CMC API (OPTIONAL, REQUIRES API KEY)
# ============================================
print('\n' + '=' * 60)
print('📊 CMC API - Latest Quotes')
print('=' * 60)
print(f'  Source: CoinMarketCap API (optional, requires API key)')
print('-' * 60)

try:
    fetcher = CMCFetcher()
    quotes = fetcher.get_latest_quotes(ASSETS)
    
    for symbol, q in quotes.items():
        if q:
            price = q.get('price', 0)
            volume = q.get('volume_24h', 0)
            market_cap = q.get('market_cap', 0)
            change = q.get('percent_change_24h', 0)
            
            print(f'\n🔹 {symbol}')
            print(f'   Price: ${price:,.2f}')
            print(f'   24h Volume: ${volume:,.0f}')
            print(f'   Market Cap: ${market_cap:,.0f}')
            print(f'   24h Change: {change:.2f}%')
        else:
            print(f'\n❌ {symbol}: Data not available')
            
except Exception as e:
    print(f'\n❌ CMC API error: {e}')
    print('   (CMC API key may not be set in .env file)')

# ============================================
# 3. SUMMARY
# ============================================
print('\n' + '=' * 60)
print('📊 SUMMARY')
print('=' * 60)
print(f'  Total assets displayed: {len(ASSETS)}')
print(f'  Data sources: Binance (free) + CMC (optional)')
print(f'  Time window: 24 hours')
print('=' * 60)

print('\n✅ Test complete!')
