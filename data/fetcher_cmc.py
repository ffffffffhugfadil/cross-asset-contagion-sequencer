"""
data/fetcher_cmc.py
===================
CoinMarketCap Agent Hub Integration.
"""

import os
import json
import requests
from typing import Optional, Dict, Any

CMC_MCP_URL = "https://mcp.coinmarketcap.com/skill-hub/stream"

# ===== EXPORT FLAG =====
CMC_AVAILABLE = True  # ← Tambahkan ini!

def get_cmc_api_key() -> Optional[str]:
    return os.environ.get('CMC_PRO_API_KEY') or os.environ.get('CMC_API_KEY')


def execute_cmc_skill(skill_name: str, params: dict) -> Optional[Dict[str, Any]]:
    """Execute a skill on CMC Agent Hub."""
    api_key = get_cmc_api_key()
    if not api_key:
        return None
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "execute_skill",
            "arguments": {
                "unique_name": skill_name,
                "parameters": params
            }
        },
        "id": 1
    }
    
    try:
        response = requests.post(
            CMC_MCP_URL,
            headers={
                "X-CMC-MCP-API-KEY": api_key,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        text = response.text
        
        # Parse SSE
        for line in text.split('\n'):
            if line.startswith('data:'):
                json_str = line[5:].strip()
                try:
                    data = json.loads(json_str)
                    if 'result' in data and 'content' in data['result']:
                        content = data['result']['content']
                        if content and 'text' in content[0]:
                            text_content = content[0]['text']
                            try:
                                parsed = json.loads(text_content)
                                return parsed
                            except:
                                return {"raw": text_content}
                except json.JSONDecodeError:
                    continue
        return None
    except Exception as e:
        print(f"⚠️ CMC error: {e}")
        return None


def get_macro_regime() -> Optional[Dict[str, Any]]:
    """Get crypto macro regime overview."""
    result = execute_cmc_skill("crypto_macro_overview", {"preview": True})
    if not result:
        return {"regime": "UNKNOWN", "confidence": "LOW", "status": "error"}
    
    data = result.get('data', {})
    decision_report = data.get('decision_report', {})
    
    return {
        "regime": decision_report.get('regime', 'UNKNOWN'),
        "confidence": decision_report.get('confidence', data.get('confidence', 'LOW')),
        "status": data.get('status', 'unknown'),
        "summary": decision_report.get('summary', ''),
        "risk_assets": decision_report.get('risk_assets', {}),
        "liquidity": decision_report.get('liquidity', {}),
        "title": decision_report.get('title', ''),
        "_raw": result
    }


def get_btc_correlation() -> Optional[Dict[str, Any]]:
    """Get BTC vs Nasdaq, DXY, Gold correlation."""
    result = execute_cmc_skill("btc_cross_asset_correlation", {"preview": True})
    if not result:
        return {"regime_label": "UNKNOWN"}
    
    data = result.get('data', {})
    decision_report = data.get('decision_report', {})
    
    return {
        "btc_vs_nasdaq": decision_report.get('btc_vs_nasdaq', data.get('btc_vs_nasdaq')),
        "btc_vs_spx": decision_report.get('btc_vs_spx', data.get('btc_vs_spx')),
        "btc_vs_dxy": decision_report.get('btc_vs_dxy', data.get('btc_vs_dxy')),
        "btc_vs_gold": decision_report.get('btc_vs_gold', data.get('btc_vs_gold')),
        "regime_label": decision_report.get('regime_label', data.get('regime_label', 'UNKNOWN')),
        "divergence": decision_report.get('divergence', data.get('divergence', {})),
        "_raw": result
    }


def get_daily_market_overview() -> Optional[Dict[str, Any]]:
    """Get daily crypto market overview."""
    result = execute_cmc_skill("daily_market_overview", {"preview": True})
    if not result:
        return None
    
    data = result.get('data', {})
    return {
        "market_read": data.get('market_read', {}),
        "macro_deep_read": data.get('macro_deep_read', {}),
        "trader_readouts": data.get('trader_readouts', {}),
        "watchlist": data.get('watchlist', []),
        "confidence": data.get('confidence', 'LOW'),
        "_raw": result
    }


def get_cmc_all() -> Dict[str, Any]:
    """Get all CMC data in one call."""
    return {
        "macro_regime": get_macro_regime(),
        "btc_correlation": get_btc_correlation(),
        "daily_market": get_daily_market_overview(),
    }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=" * 60)
    print("📊 CMC AGENT HUB — TEST")
    print("=" * 60)
    
    if not get_cmc_api_key():
        print("❌ API Key not found")
    else:
        print("✅ API Key found")
        print(f"   CMC_AVAILABLE = {CMC_AVAILABLE}")
        
        print("\n1. MACRO REGIME")
        print("-" * 40)
        macro = get_macro_regime()
        print(f"   Regime:    {macro.get('regime')}")
        print(f"   Confidence: {macro.get('confidence')}")
        
        print("\n2. BTC CORRELATION")
        print("-" * 40)
        corr = get_btc_correlation()
        print(f"   BTC vs Nasdaq: {corr.get('btc_vs_nasdaq')}")
        print(f"   BTC vs DXY:    {corr.get('btc_vs_dxy')}")
    
    print("\n" + "=" * 60)
