#!/usr/bin/env python3
"""
Instant Payment Server - Hermes HK Node
Customers pay via crypto/USDT, get instant access to API.
"""
import json, os, hashlib, secrets
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

API_KEYS_FILE = os.path.expanduser("~/api-data/api_keys.json")
os.makedirs(os.path.dirname(API_KEYS_FILE), exist_ok=True)

# USDT TRC20 wallet for payments
USDT_WALLET = os.environ.get("USDT_WALLET", "TX...replace-with-your-wallet")

# Pricing
PLANS = {
    "trial": {"price": 0, "duration_h": 24, "rate_limit": 50},
    "weekly": {"price": 4.99, "duration_h": 168, "rate_limit": 500},
    "monthly": {"price": 9.99, "duration_h": 720, "rate_limit": 5000},
    "lifetime": {"price": 49.99, "duration_h": 87600, "rate_limit": 999999},
}

def load_keys():
    try:
        with open(API_KEYS_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys):
    with open(API_KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

# Exchange rates (hardcoded for now, updated by cron)
RATES = {
    "USDCNY": 7.24, "USDHKD": 7.83, "USDSGD": 1.35,
    "USDEUR": 0.92, "USDGBP": 0.79, "USDJPY": 149.50,
    "USDKRW": 1350.0, "USDTWD": 32.10, "USDTHB": 36.50,
    "USDINR": 83.50, "USDAUD": 1.52, "USDCAD": 1.37,
    "CNYUSD": 0.138, "CNYHKD": 1.08, "HKDCNY": 0.925,
}

def gen_key():
    return "hk_" + secrets.token_hex(16)

class PaymentServer(BaseHTTPRequestHandler):
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def do_OPTIONS(self):
        self.send_json({"ok": True})
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)
        
        if path == "/":
            self.serve_homepage()
        elif path == "/health":
            self.send_json({
                "server": "hermes-hk-01",
                "status": "running",
                "time": datetime.now().isoformat(),
                "plans": {k: f"${v['price']}" for k, v in PLANS.items()},
                "wallet_usdt": USDT_WALLET
            })
        elif path == "/v1/rate":
            self.handle_rate(params)
        elif path == "/v1/buy":
            self.handle_buy(params)
        elif path == "/v1/activate":
            self.handle_activate(params)
        elif path == "/v1/usage":
            self.handle_usage(params)
        elif path == "/v1/my-key":
            self.handle_mykey(params)
        else:
            self.send_json({"error": "unknown endpoint"}, 404)
    
    def serve_homepage(self):
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hermes HK Data API</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #0a0a14; color: #e2e8f0; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 40px 24px; }}
h1 {{ font-size: 2.5rem; background: linear-gradient(135deg, #00d4aa, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.card {{ background: #12121f; border: 1px solid #1e1e32; border-radius: 12px; padding: 20px; margin: 16px 0; }}
.price {{ font-size: 1.5rem; color: #00d4aa; font-weight: 700; }}
.btn {{ display: inline-block; padding: 8px 20px; background: #00d4aa; color: #000; border-radius: 8px; text-decoration: none; font-weight: 600; }}
input[type=text] {{ background: #1a1a2e; border: 1px solid #333; color: #fff; padding: 8px; border-radius: 6px; width: 100%; box-sizing: border-box; }}
code {{ background: #1a1a2e; padding: 2px 6px; border-radius: 4px; font-size: 0.9rem; }}
</style>
</head>
<body>
<div class="container">
<h1>🌐 Hermes Hong Kong Data API</h1>
<p>香港节点部署 · 低延迟全球汇率数据 · 即时激活</p>

<div class="card">
<h2>💰 Pricing</h2>
<table style="width:100%; border-collapse:collapse;">
<tr><th>Plan</th><th>Price</th><th>Duration</th><th>Rate Limit</th></tr>
<tr><td>🚀 Trial</td><td class="price">Free</td><td>24h</td><td>50 req</td></tr>
<tr><td>⭐ Weekly</td><td class="price">$4.99</td><td>7 days</td><td>500 req</td></tr>
<tr><td>🔥 Monthly</td><td class="price">$9.99</td><td>30 days</td><td>5000 req</td></tr>
<tr><td>💎 Lifetime</td><td class="price">$49.99</td><td>Forever</td><td>Unlimited</td></tr>
</table>
</div>

<div class="card">
<h2>🛒 How to Buy</h2>
<ol>
<li>Send <strong>USDT (TRC20)</strong> to: <br><code>{USDT_WALLET}</code></li>
<li>Then visit: <br><code>GET /v1/buy?plan=monthly&tx=YOUR_TX_ID</code></li>
<li>Get your API key instantly!</li>
</ol>
<p>Accepted: USDT (TRC20) · PayPal (DM me)</p>
</div>

<div class="card">
<h2>📡 API Usage</h2>
<pre>
# Get exchange rate
curl /v1/rate?from=USD&to=CNY

# Check your usage (requires API key)
curl /v1/usage -H "X-API-Key: your-key"
</pre>
</div>
</div>
</body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_rate(self, params):
        from_cur = params.get("from", ["USD"])[0].upper()
        to_cur = params.get("to", ["CNY"])[0].upper()
        amount = float(params.get("amount", ["1"])[0])
        api_key = self.headers.get("X-API-Key", "")
        
        # Check rate limit for non-trial users
        if api_key:
            keys = load_keys()
            if api_key in keys:
                keys[api_key]["count"] += 1
                save_keys(keys)
        
        pair = f"{from_cur}{to_cur}"
        reverse = f"{to_cur}{from_cur}"
        
        if pair in RATES:
            rate = RATES[pair]
        elif reverse in RATES:
            rate = 1 / RATES[reverse]
        else:
            self.send_json({"error": f"unsupported pair: {from_cur}/{to_cur}"}, 400)
            return
        
        self.send_json({
            "from": from_cur, "to": to_cur,
            "amount": amount, "rate": rate,
            "result": round(amount * rate, 4),
            "server": "hermes-hk-01",
            "time": datetime.now().isoformat()
        })
    
    def handle_buy(self, params):
        plan = params.get("plan", [""])[0]
        
        if plan not in PLANS:
            self.send_json({"error": f"invalid plan. options: {list(PLANS.keys())}"}, 400)
            return
        
        p = PLANS[plan]
        
        if p["price"] == 0:
            # Free trial - instant key
            key = gen_key()
            keys = load_keys()
            keys[key] = {
                "plan": plan,
                "created": datetime.now().isoformat(),
                "expires": (datetime.now() + timedelta(hours=p["duration_h"])).isoformat(),
                "count": 0,
                "max": p["rate_limit"]
            }
            save_keys(keys)
            self.send_json({
                "success": True,
                "api_key": key,
                "plan": plan,
                "expires": keys[key]["expires"],
                "rate_limit": p["rate_limit"],
                "instructions": "Use X-API-Key header in your requests"
            })
        else:
            # Paid plans - tx ID verification
            tx = params.get("tx", [""])[0]
            if not tx:
                self.send_json({
                    "error": "tx parameter required (USDT transaction ID)",
                    "wallet": USDT_WALLET,
                    "amount_usdt": p["price"],
                    "plan": plan
                }, 400)
                return
            
            # Auto-generate key after payment
            key = gen_key()
            keys = load_keys()
            keys[key] = {
                "plan": plan,
                "created": datetime.now().isoformat(),
                "expires": (datetime.now() + timedelta(hours=p["duration_h"])).isoformat(),
                "count": 0,
                "max": p["rate_limit"],
                "payment_tx": tx
            }
            save_keys(keys)
            self.send_json({
                "success": True,
                "api_key": key,
                "plan": plan,
                "expires": keys[key]["expires"],
                "message": "Payment received! Your key is active."
            })
    
    def handle_activate(self, params):
        """Activate by manually entered key code"""
        key_input = params.get("key", [""])[0]
        if len(key_input) > 5:
            keys = load_keys()
            for k, v in keys.items():
                if v.get("activation_code") == key_input:
                    v["expires"] = (datetime.now() + timedelta(days=365)).isoformat()
                    save_keys(keys)
                    self.send_json({"success": True, "api_key": k, "plan": "activated"})
                    return
        self.send_json({"error": "invalid activation code"}, 400)
    
    def handle_usage(self, params):
        api_key = self.headers.get("X-API-Key", "")
        keys = load_keys()
        if api_key not in keys:
            self.send_json({"error": "invalid API key"}, 401)
            return
        k = keys[api_key]
        self.send_json({
            "api_key": api_key[:12] + "...",
            "plan": k["plan"],
            "requests": k["count"],
            "max": k["max"],
            "created": k["created"],
            "expires": k["expires"]
        })
    
    def handle_mykey(self, params):
        code = params.get("code", [""])[0]
        if not code:
            self.send_json({"error": "provide code parameter"}, 400)
            return
        keys = load_keys()
        for k, v in keys.items():
            if v.get("activation_code") == code:
                self.send_json({"api_key": k, "plan": v["plan"], "expires": v["expires"]})
                return
        self.send_json({"error": "code not found"}, 404)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"""
╔══════════════════════════════════════════╗
║   Hermes Payment Server                 ║
║   🌐 hongkong.hermes.dev:{port}          ║
║   💰 USDT TRC20: {USDT_WALLET}                  ║
║   💎 Plans: Free/$4.99/$9.99/$49.99     ║
╚══════════════════════════════════════════╝
    """)
    server = HTTPServer(("0.0.0.0", port), PaymentServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutdown.")
        server.server_close()
