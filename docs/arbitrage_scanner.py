#!/usr/bin/env python3
"""
Hermes HK - Cross-Exchange Arbitrage Scanner
Monitors real-time prices across exchanges to find arbitrage opportunities.
Runs continuously from Hong Kong node for lowest latency.
"""

import urllib.request
import json
import time
import hmac
import hashlib
from datetime import datetime

class ArbitrageScanner:
    def __init__(self):
        self.pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT"]
        self.last_prices = {}
        
    def fetch_binance(self, pair):
        """Fetch price from Binance"""
        try:
            r = urllib.request.urlopen(
                f"https://api.binance.com/api/v3/ticker/bookTicker?symbol={pair}", 
                timeout=3
            )
            data = json.loads(r.read())
            return {
                "bid": float(data["bidPrice"]),
                "ask": float(data["askPrice"]),
                "exchange": "Binance"
            }
        except:
            return None
    
    def fetch_coinbase(self, pair):
        """Fetch price from Coinbase"""
        try:
            coinbase_pair = pair.replace("USDT", "-USD")
            r = urllib.request.urlopen(
                f"https://api.coinbase.com/v2/prices/{coinbase_pair}/spot", 
                timeout=3
            )
            data = json.loads(r.read())
            price = float(data["data"]["amount"])
            return {
                "bid": price * 0.999,
                "ask": price * 1.001,
                "exchange": "Coinbase"
            }
        except:
            return None
    
    def fetch_bybit(self, pair):
        """Fetch price from Bybit"""
        try:
            r = urllib.request.urlopen(
                f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={pair}",
                timeout=3
            )
            data = json.loads(r.read())
            ticker = data["result"]["list"][0]
            return {
                "bid": float(ticker["bid1Price"]),
                "ask": float(ticker["ask1Price"]),
                "exchange": "Bybit"
            }
        except:
            return None
    
    def scan(self):
        """Scan all pairs across all exchanges"""
        opportunities = []
        
        for pair in self.pairs:
            prices = {}
            
            # Fetch from all exchanges
            for fetcher in [self.fetch_binance, self.fetch_coinbase, self.fetch_bybit]:
                result = fetcher(pair)
                if result:
                    prices[result["exchange"]] = result
            
            if len(prices) >= 2:
                # Find best bid (buy) and best ask (sell)
                best_bid = max(prices.values(), key=lambda x: x["bid"])
                best_ask = min(prices.values(), key=lambda x: x["ask"])
                
                spread = best_bid["bid"] - best_ask["ask"]
                spread_pct = (spread / best_ask["ask"]) * 100
                
                # Check if profitable after estimated fees (0.1% each side = 0.2% total)
                net_spread = spread_pct - 0.2  # subtract trading fees
                
                opp = {
                    "pair": pair,
                    "buy_at": best_ask["exchange"],
                    "buy_price": best_ask["ask"],
                    "sell_at": best_bid["exchange"],
                    "sell_price": best_bid["bid"],
                    "gross_spread_pct": round(spread_pct, 4),
                    "net_spread_pct": round(net_spread, 4),
                    "timestamp": datetime.now().isoformat()
                }
                
                if net_spread > 0:
                    opp["profit_per_1000"] = round(1000 * net_spread / 100, 2)
                    opportunities.append(opp)
        
        return opportunities
    
    def report(self, opportunities):
        """Generate a clean report"""
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  HERMES HK — ARBITRAGE SCAN")
        lines.append(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} HKT")
        lines.append(f"  Node: Hong Kong (latency optimized)")
        lines.append(f"{'='*70}")
        
        if not opportunities:
            lines.append(f"\n  📊 No profitable arbitrage found (net after fees)")
            lines.append(f"  💡 Tip: Check again in 5-10 minutes")
        else:
            lines.append(f"\n  🔥 PROFITABLE OPPORTUNITIES FOUND: {len(opportunities)}")
            lines.append(f"  {'─'*70}")
            
            for opp in sorted(opportunities, key=lambda x: x["net_spread_pct"], reverse=True):
                star = "🤑" if opp["net_spread_pct"] > 0.5 else "💰" if opp["net_spread_pct"] > 0.2 else "✅"
                lines.append(f"\n  {star} {opp['pair']}")
                lines.append(f"     BUY  {opp['buy_at']:>10} @ ${opp['buy_price']:<10.2f}")
                lines.append(f"     SELL {opp['sell_at']:>10} @ ${opp['sell_price']:<10.2f}")
                lines.append(f"     Gross spread: {opp['gross_spread_pct']}%")
                lines.append(f"     Net spread (after fees): {opp['net_spread_pct']}%")
                lines.append(f"     Profit per $1,000: ${opp['profit_per_1000']}")
            
            total_profit = sum(o["profit_per_1000"] for o in opportunities)
            lines.append(f"\n  {'─'*70}")
            lines.append(f"  💰 Total profit per $1000 across all: ${total_profit:.2f}")
        
        lines.append(f"\n{'='*70}\n")
        return "\n".join(lines)

if __name__ == "__main__":
    scanner = ArbitrageScanner()
    
    print(f"🔄 Hermes HK Arbitrage Scanner starting...")
    print(f"📡 Monitoring {len(scanner.pairs)} pairs across Binance, Coinbase, Bybit")
    print(f"🌐 Hong Kong node — low latency to global exchanges\n")
    
    # Run scan
    opps = scanner.scan()
    print(scanner.report(opps))
    
    # Track historical
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    with open(f"/tmp/arbitrage_{timestamp}.json", "w") as f:
        json.dump(opps, f, indent=2)
    print(f"📊 Saved: arbitrage_{timestamp}.json")
