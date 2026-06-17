from data.fetcher_binance import get_returns_with_timestamps
from data.fetcher import CMCFetcher

print('=' * 50)
print('📊 DATA ASLI CAKE & LINK')
print('=' * 50)

# Binance API - CAKE
cake_returns, cake_ts = get_returns_with_timestamps('CAKE', hours=24)
if cake_returns:
    print(f'\n🍰 CAKE (PancakeSwap) - Binance')
    print(f'   Data points: {len(cake_returns)} jam')
    print(f'   Last price: ${cake_returns[-1]:.4f}')
    print(f'   24h change: {(sum(cake_returns) * 100):.2f}%')
else:
    print('\n🍰 CAKE: Gagal ambil data')

# Binance API - LINK
link_returns, link_ts = get_returns_with_timestamps('LINK', hours=24)
if link_returns:
    print(f'\n🔗 LINK (Chainlink) - Binance')
    print(f'   Data points: {len(link_returns)} jam')
    print(f'   Last price: ${link_returns[-1]:.4f}')
    print(f'   24h change: {(sum(link_returns) * 100):.2f}%')
else:
    print('\n🔗 LINK: Gagal ambil data')

# CMC API - CAKE & LINK
try:
    fetcher = CMCFetcher()
    quotes = fetcher.get_latest_quotes(['CAKE', 'LINK'])
    
    print('\n' + '=' * 50)
    print('📊 DATA DARI CMC API')
    print('=' * 50)
    
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
except Exception as e:
    print(f'\n❌ CMC API error: {e}')
