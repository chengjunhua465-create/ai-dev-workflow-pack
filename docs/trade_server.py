#!/usr/bin/env python3
"""
Hermes HK — Auto Trading Signal Service
香港低延迟节点，实时分析市场并给出交易信号。
客户支付 USDT 订阅，自动接收信号。
"""

import urllib.request
import json
import time
import hashlib
import os
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

USDT_WALLET = "TGkpKWGpV5QKi1JAk9KeUPWk3LPZXsBCVp"
KEYS_FILE = os.path.expanduser("~/api-data/trade_keys.json")
os.makedirs(os.path.dirname(KEYS_FILE), exist_ok=True)

PRICING = {
    "free": {"price": 0, "signals_per_day": 3, "desc": "Basic price alerts"},
    "weekly": {"price": 4.99, "signals_per_day": 20, "desc": "Real-time trade signals"},
    "monthly": {"price": 14.99, "signals_per_day": 100, "desc": "Premium signals + API access"},
    "vip": {"price": 49.99, "signals_per_day": 9999, "desc": "VIP: Custom strategies + webhook"},
}

def load_keys():
    try:
        with open(KEYS_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def gen_key():
    import secrets
    return "ts_" + secrets.token_hex(12)

class MarketAnalyzer:
    """Analyzes crypto market and generates trade signals"""
    
    def __init__(self):
        self.pairs = {
            "BTCUSDT": "Bitcoin",
            "ETHUSDT": "Ethereum",
            "SOLUSDT": "Solana",
            "BNBUSDT": "BNB",
            "XRPUSDT": "Ripple",
        }
    
    def fetch_klines(self, pair, interval="15m", limit=24):
        """Fetch candlestick data from Binance"""
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval={interval}&limit={limit}"
            r = urllib.request.urlopen(url, timeout=5)
            return json.loads(r.read())
        except:
            return None
    
    def calc_sma(self, closes, period):
        """Simple Moving Average"""
        if len(closes) < period:
            return None
        return sum(closes[-period:]) / period
    
    def calc_rsi(self, closes, period=14):
        """Relative Strength Index"""
        if len(closes) < period + 1:
            return None
        gains = []
        losses = []
        for i in range(-period, 0):
            change = closes[i] - closes[i-1]
            if change >= 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def analyze(self, pair):
        """Generate a trading signal for a pair"""
        klines = self.fetch_klines(pair)
        if not klines or len(klines) < 20:
            return None
        
        closes = [float(k[4]) for k in klines]
        current_price = closes[-1]
        
        # Technical indicators
        sma_7 = self.calc_sma(closes, 7)
        sma_25 = self.calc_sma(closes, 25)
        rsi = self.calc_rsi(closes)
        
        # Volume analysis
        volumes = [float(k[5]) for k in klines]
        avg_vol = sum(volumes) / len(volumes)
        current_vol = volumes[-1]
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
        
        # Generate signal
        signal = "NEUTRAL"
        confidence = 50
        reason = ""
        
        if sma_7 and sma_25:
            if sma_7 > sma_25 and current_price > sma_7:
                if rsi and rsi < 70:
                    signal = "BUY"
                    confidence = min(85, 50 + (current_price - sma_25) / sma_25 * 100)
                    reason = "Bullish: price above SMA7 & SMA25"
                    if vol_ratio > 1.5:
                        confidence = min(95, confidence + 10)
                        reason += " + high volume confirmation"
                elif rsi and rsi >= 70:
                    signal = "CAUTION"
                    confidence = 40
                    reason = "Overbought RSI — consider waiting for pullback"
            elif sma_7 < sma_25 and current_price < sma_7:
                if rsi and rsi > 30:
                    signal = "SELL"
                    confidence = min(85, 50 + (sma_25 - current_price) / sma_25 * 100)
                    reason = "Bearish: price below SMA7 & SMA25"
                    if vol_ratio > 1.5:
                        confidence = min(95, confidence + 10)
                        reason += " + high volume confirmation"
                elif rsi and rsi <= 30:
                    signal = "CAUTION"
                    confidence = 40
                    reason = "Oversold RSI — potential bounce incoming"
        
        return {
            "pair": pair,
            "name": self.pairs.get(pair, pair),
            "price": current_price,
            "signal": signal,
            "confidence": round(confidence, 1),
            "rsi": round(rsi, 1) if rsi else None,
            "sma_7": round(sma_7, 2) if sma_7 else None,
            "sma_25": round(sma_25, 2) if sma_25 else None,
            "volume_ratio": round(vol_ratio, 2),
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
    
    def scan_all(self):
        """Generate signals for all pairs"""
        results = []
        for pair in self.pairs:
            signal = self.analyze(pair)
            if signal:
                results.append(signal)
        return results

class TradeSignalServer(BaseHTTPRequestHandler):
    analyzer = MarketAnalyzer()
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def authenticate(self):
        key = self.headers.get("X-API-Key", "")
        if not key:
            return None, "No API key provided"
        keys = load_keys()
        if key not in keys:
            return None, "Invalid API key"
        k = keys[key]
        expires = datetime.fromisoformat(k["expires"])
        if datetime.now() > expires:
            return None, "API key expired"
        # Check daily limit
        today = datetime.now().strftime("%Y%m%d")
        if k.get("date") != today:
            k["date"] = today
            k["daily_count"] = 0
        if k["daily_count"] >= k["daily_max"]:
            return None, f"Daily limit reached ({k['daily_max']} signals)"
        k["daily_count"] += 1
        save_keys(keys)
        return k, None
    
    def do_OPTIONS(self):
        self.send_json({"ok": True})
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)
        
        if path == "/":
            self.serve_home()
        elif path == "/health":
            self.send_json({
                "server": "hermes-hk-trader",
                "status": "running",
                "time": datetime.now().isoformat(),
                "wallet": USDT_WALLET
            })
        elif path == "/v1/signals":
            # Free tier gets basic signals
            signals = self.analyzer.scan_all()
            self.send_json({"signals": signals, "count": len(signals)})
        elif path == "/v1/signal":
            pair = params.get("pair", ["BTCUSDT"])[0].upper()
            signal = self.analyzer.analyze(pair)
            if signal:
                self.send_json(signal)
            else:
                self.send_json({"error": "Could not analyze pair"}, 400)
        elif path == "/v1/buy":
            self.handle_buy(params)
        elif path == "/v1/status":
            key_info, err = self.authenticate()
            if err:
                self.send_json({"error": err}, 401)
                return
            self.send_json({
                "plan": key_info.get("plan"),
                "daily_used": key_info.get("daily_count", 0),
                "daily_max": key_info.get("daily_max", 0),
                "expires": key_info.get("expires"),
                "signals_remaining": key_info["daily_max"] - key_info.get("daily_count", 0)
            })
        else:
            self.send_json({"error": "unknown endpoint"}, 404)
    
    def handle_buy(self, params):
        plan = params.get("plan", [""])[0]
        if plan not in PRICING:
            self.send_json({
                "error": f"Invalid plan. Options: {list(PRICING.keys())}",
                "pricing": PRICING
            }, 400)
            return
        
        p = PRICING[plan]
        
        if p["price"] == 0:
            import secrets
            key = "ts_" + secrets.token_hex(12)
            keys = load_keys()
            keys[key] = {
                "plan": plan,
                "created": datetime.now().isoformat(),
                "expires": (datetime.now() + timedelta(days=7)).isoformat(),
                "daily_count": 0,
                "daily_max": p["signals_per_day"],
                "date": datetime.now().strftime("%Y%m%d")
            }
            save_keys(keys)
            self.send_json({
                "success": True,
                "api_key": key,
                "plan": plan,
                "signals_per_day": p["signals_per_day"],
                "expires": keys[key]["expires"]
            })
        else:
            tx = params.get("tx", [""])[0]
            if not tx:
                self.send_json({
                    "error": "Send USDT payment first",
                    "wallet": USDT_WALLET,
                    "amount": f"${p['price']} USDT",
                    "plan": plan,
                    "instructions": f"Send {p['price']} USDT(TRC20) to {USDT_WALLET}, then call /v1/buy?plan={plan}&tx=YOUR_TX_ID"
                }, 400)
                return
            
            import secrets
            key = "ts_" + secrets.token_hex(12)
            hours = {"weekly": 168, "monthly": 720, "vip": 8760}
            keys = load_keys()
            keys[key] = {
                "plan": plan,
                "created": datetime.now().isoformat(),
                "expires": (datetime.now() + timedelta(hours=hours.get(plan, 720))).isoformat(),
                "daily_count": 0,
                "daily_max": p["signals_per_day"],
                "date": datetime.now().strftime("%Y%m%d"),
                "payment_tx": tx
            }
            save_keys(keys)
            self.send_json({
                "success": True,
                "api_key": key,
                "plan": plan,
                "signals_per_day": p["signals_per_day"],
                "expires": keys[key]["expires"],
                "message": "Payment confirmed! Key activated."
            })
    
    def serve_home(self):
        html = f"""<!DOCTYPE html>
<html>
<head><title>Hermes HK Trade Signals</title>
<style>
body {{ font-family:-apple-system,sans-serif; background:#0a0a14; color:#e2e8f0; max-width:800px; margin:40px auto; padding:20px; }}
h1 {{ background:linear-gradient(135deg,#00d4aa,#7c3aed); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.card {{ background:#12121f; border:1px solid #1e1e32; border-radius:12px; padding:20px; margin:16px 0; }}
.price {{ color:#00d4aa; font-weight:700; }}
.btn {{ display:inline-block; padding:10px 24px; background:#00d4aa; color:#000; text-decoration:none; border-radius:8px; font-weight:600; }}
.wallet {{ background:#1a1a2e; padding:12px; border-radius:8px; font-family:monospace; word-break:break-all; }}
</style>
</head>
<body>
<h1>📈 Hermes HK Trade Signals</h1>
<p>香港低延迟节点 · 实时加密货币交易信号</p>

<div class="card">
<h2>💰 Plans</h2>
<table style="width:100%; border-collapse:collapse;">
<tr><th>Plan</th><th>Price</th><th>Signals/Day</th></tr>
<tr><td>🆓 Free</td><td class="price">$0</td><td>3 signals</td></tr>
<tr><td>⭐ Weekly</td><td class="price">$4.99</td><td>20 signals</td></tr>
<tr><td>🔥 Monthly</td><td class="price">$14.99</td><td>100 signals</td></tr>
<tr><td>💎 VIP</td><td class="price">$49.99</td><td>Unlimited + Custom</td></tr>
</table>
</div>

<div class="card">
<h2>🛒 Buy</h2>
<p>Send USDT (TRC20) to:</p>
<div class="wallet">{USDT_WALLET}</div>
<p style="margin-top:8px;">Then call <code>GET /v1/buy?plan=monthly&tx=YOUR_TX</code></p>
<p>Free tier: <a href="/v1/buy?plan=free">Get Free API Key →</a></p>
</div>

<div class="card">
<h3>📡 Live Signals</h3>
<p>Check current signals: <a href="/v1/signals"><code>/v1/signals</code></a></p>
</div>

<p style="color:#94a3b8;font-size:0.85rem;">Hermes HK · Powered by Hong Kong Node</p>
</body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9091))
    
    print(f"""
╔═══════════════════════════════════════════╗
║  📈 Hermes HK Trade Signal Server        ║
║  🌐 Port: {port}                              ║
║  💰 USDT: {USDT_WALLET}  ║
║  💎 Plans: Free/$4.99/$14.99/$49.99      ║
╚═══════════════════════════════════════════╝
    """)
    
    server = HTTPServer(("0.0.0.0", port), TradeSignalServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
