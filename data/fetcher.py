"""
data/fetcher.py
===============
Fetch crypto market data from CoinMarketCap API.

Endpoints used (Basic Plan compatible):
- /v1/cryptocurrency/quotes/latest        → latest prices + volume
- /v3/cryptocurrency/quotes/historical    → historical hourly close prices
- /v1/global-metrics/quotes/latest        → Fear & Greed, BTC dominance
- /v1/global-metrics/quotes/latest        → derivatives OI + funding (limited)

Usage:
    from data.fetcher import CMCFetcher
    fetcher = CMCFetcher()
    prices = fetcher.get_latest_quotes(["BTC", "ETH", "BNB"])
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

CMC_BASE_URL = "https://pro-api.coinmarketcap.com"
DEFAULT_SYMBOLS = ["BTC", "ETH", "BNB", "CAKE", "LINK", "ADA"]

SYMBOL_TO_ID = {
    "BTC": 1,
    "ETH": 1027,
    "BNB": 1839,
    "CAKE": 7186,
    "LINK": 1975,
    "ADA": 2010,
    "SOL": 5426,
    "DOGE": 74,
    "XRP": 52,
    "MATIC": 3890,
}


class CMCFetcher:

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("CMC_API_KEY")
        if not self.api_key:
            raise ValueError("CMC_API_KEY not found. Set it in .env file.")
        self.headers = {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json",
        }

    def _get(self, endpoint: str, params: dict) -> dict:
        """Base GET request with error handling."""
        url = f"{CMC_BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"[CMC API Error] {e}")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"[Network Error] {e}")
            return {}

    def _symbol_to_id(self, symbol: str) -> int:
        """Convert symbol to CMC ID."""
        if symbol not in SYMBOL_TO_ID:
            raise ValueError(f"Unknown symbol: {symbol}. Add to SYMBOL_TO_ID mapping.")
        return SYMBOL_TO_ID[symbol]

    # 1. Latest Prices

    def get_latest_quotes(self, symbols: list[str] = DEFAULT_SYMBOLS) -> dict:
        """
        Get latest price, volume, market cap for a list of symbols.

        Returns dict keyed by symbol:
        {
            "BTC": {
                "price": 27000.0,
                "volume_24h": 15000000000,
                "market_cap": 520000000000,
                "percent_change_1h": -0.5,
                "percent_change_24h": -3.2,
            },
            ...
        }
        """
        data = self._get(
            "/v1/cryptocurrency/quotes/latest",
            {"symbol": ",".join(symbols), "convert": "USD"},
        )

        result = {}
        for symbol in symbols:
            try:
                token = data["data"][symbol]
                if isinstance(token, list):
                    token = token[0]
                quote = token["quote"]["USD"]
                result[symbol] = {
                    "price": quote.get("price"),
                    "volume_24h": quote.get("volume_24h"),
                    "market_cap": quote.get("market_cap"),
                    "percent_change_1h": quote.get("percent_change_1h"),
                    "percent_change_24h": quote.get("percent_change_24h"),
                }
            except (KeyError, TypeError):
                print(f"[Warning] Could not parse quote for {symbol}")
                result[symbol] = None

        return result

    # 2. Historical Quotes (Basic Plan compatible)


    def get_historical_quotes(
        self,
        symbol: str,
        count: int = 72,
        interval: str = "hourly",
    ) -> list[dict]:
        """
        Get historical hourly close prices for one symbol.
        Compatible with CMC Basic Plan.

        Returns list of candles (oldest first):
        [
            {
                "timestamp": "2022-11-08T06:00:00Z",
                "close": 20900.0,
                "volume": 980000000.0,
            },
            ...
        ]

        Note: Only close price + volume are available in Basic plan.
        For return calculation, close price is sufficient.
        """
        cmc_id = self._symbol_to_id(symbol)
        
        data = self._get(
            "/v3/cryptocurrency/quotes/historical",
            {
                "id": cmc_id,
                "interval": interval,
                "count": count,
                "convert": "USD",
            },
        )

        candles = []
        try:
            # Response structure: data[0].quotes[...]
            quotes_data = data.get("data", [{}])[0].get("quotes", [])
            for q in quotes_data:
                quote = q.get("quote", {}).get("USD", {})
                candles.append({
                    "timestamp": q.get("timestamp"),
                    "close": quote.get("price"),
                    "volume": quote.get("volume_24h"),
                })
        except (KeyError, TypeError, IndexError) as e:
            print(f"[Warning] Could not parse historical quotes for {symbol}: {e}")

        return candles

    # 3. Global Metrics (Fear & Greed, BTC dominance)

    def get_global_metrics(self) -> dict:
        """
        Get global market metrics.

        Returns:
        {
            "btc_dominance": 48.2,
            "total_market_cap": 1_100_000_000_000,
            "total_volume_24h": 85_000_000_000,
            "fear_greed_index": 32,
            "fear_greed_label": "Fear",
        }
        """
        data = self._get("/v1/global-metrics/quotes/latest", {"convert": "USD"})

        result = {}
        try:
            d = data["data"]
            quote = d["quote"]["USD"]
            result = {
                "btc_dominance": d.get("btc_dominance"),
                "total_market_cap": quote.get("total_market_cap"),
                "total_volume_24h": quote.get("total_volume_24h"),
                "fear_greed_index": d.get("fear_greed_value"),
                "fear_greed_label": d.get("fear_greed_value_classification"),
            }
        except (KeyError, TypeError):
            print("[Warning] Could not parse global metrics")

        return result

    # 4. Derivatives Metrics (OI + funding rate)

    def get_derivatives_metrics(self, symbols: list[str] = DEFAULT_SYMBOLS) -> dict:
        """
        Get open interest and funding rate for a list of symbols.

        Returns dict keyed by symbol:
        {
            "BTC": {
                "open_interest_usd": 12_000_000_000,
                "funding_rate": 0.0001,
            },
            ...
        }
        Note: CMC Basic plan has limited derivatives coverage (BTC + ETH only).
        """
        data = self._get("/v1/global-metrics/quotes/latest", {"convert": "USD"})

        result = {s: {"open_interest_usd": None, "funding_rate": None} for s in symbols}

        try:
            d = data["data"]
            if "BTC" in symbols:
                result["BTC"]["open_interest_usd"] = d.get("btc_total_open_interest_usd")
                result["BTC"]["funding_rate"] = d.get("btc_funding_rate_rolling_average")
            if "ETH" in symbols:
                result["ETH"]["open_interest_usd"] = d.get("eth_total_open_interest_usd")
                result["ETH"]["funding_rate"] = d.get("eth_funding_rate_rolling_average")
        except (KeyError, TypeError):
            print("[Warning] Could not parse derivatives metrics")

        return result


    # 5. Convenience: fetch all data needed by sequencer in one call
   

    def fetch_all(
        self,
        symbols: list[str] = DEFAULT_SYMBOLS,
        historical_hours: int = 72,
    ) -> dict:
        """
        Single call that fetches everything the sequencer needs.

        Returns:
        {
            "quotes":      { symbol: {...} },
            "historical":  { symbol: [candle, ...] },
            "global":      { btc_dominance, fear_greed_index, ... },
            "derivatives": { symbol: { open_interest_usd, funding_rate } },
        }
        """
        print(f"[CMC] Fetching quotes for {symbols}...")
        quotes = self.get_latest_quotes(symbols)

        print(f"[CMC] Fetching {historical_hours}h historical quotes...")
        historical = {}
        for symbol in symbols:
            historical[symbol] = self.get_historical_quotes(symbol, count=historical_hours)
            time.sleep(0.3)  # gentle rate-limit buffer

        print("[CMC] Fetching global metrics...")
        global_metrics = self.get_global_metrics()

        print("[CMC] Fetching derivatives metrics...")
        derivatives = self.get_derivatives_metrics(symbols)

        return {
            "quotes": quotes,
            "historical": historical,
            "global": global_metrics,
            "derivatives": derivatives,
        }


# ---------------------------------------------------------------------------
# Quick connection test (run directly: python data/fetcher.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    fetcher = CMCFetcher()

    print("=== Testing CMC API Connection (Basic Plan Compatible) ===\n")

    # Test 1: Latest quotes
    print("1. Latest quotes (BTC, ETH, BNB):")
    quotes = fetcher.get_latest_quotes(["BTC", "ETH", "BNB"])
    for sym, q in quotes.items():
        if q:
            print(f"   {sym}: ${q['price']:,.2f} | 24h vol: ${q['volume_24h']:,.0f}")

    # Test 2: Global metrics
    print("\n2. Global metrics:")
    g = fetcher.get_global_metrics()
    print(f"   BTC dominance : {g.get('btc_dominance')}%")
    print(f"   Fear & Greed  : {g.get('fear_greed_index')} ({g.get('fear_greed_label')})")

    # Test 3: Historical quotes (Basic Plan compatible)
    print("\n3. BTC historical quotes (last 5 hours):")
    historical = fetcher.get_historical_quotes("BTC", count=5)
    for c in historical:
        print(f"   {c['timestamp']} | close: ${c['close']:,.2f} | volume: ${c['volume']:,.0f}")

    # Test 4: Derivatives (limited)
    print("\n4. Derivatives metrics:")
    deriv = fetcher.get_derivatives_metrics(["BTC", "ETH"])
    for sym, d in deriv.items():
        oi = d.get('open_interest_usd')
        fr = d.get('funding_rate')
        print(f"   {sym}: OI=${oi:,.0f if oi else 'N/A'} | funding={fr if fr else 'N/A'}")

    print("\n=== Connection OK ===")