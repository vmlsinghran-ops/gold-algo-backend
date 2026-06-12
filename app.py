import os
import json
import threading
from flask import Flask, jsonify
from flask_cors import CORS
import websocket

app = Flask(__name__)
CORS(app)  # Allows your HTML site to safely pull data from this Python server

# Global storage dictionary for tracking live calculations
live_market_state = {
    "symbol": "XAUUSDT",
    "price": 0.0,
    "volume": 0.0,
    "cash_inflow": 0.0,
    "status": "Scanning Matrix"
}

def on_message(ws, message):
    global live_market_state
    data = json.loads(message)
    
    # Extracting live parameters from Binance stream frame
    price = float(data.get('c', 0))
    volume = float(data.get('v', 0))
    cash = float(data.get('q', 0))
    
    live_market_state["price"] = price
    live_market_state["volume"] = volume
    live_market_state["cash_inflow"] = cash
    
    # Execute strategy evaluation logic
    if volume >= 50.0 or cash >= 200000.0:
        live_market_state["status"] = "⚠️ BREAKOUT DETECTED"
    else:
        live_market_state["status"] = "Scanning Matrix"

def run_websocket():
    ws_url = "wss://fstream.binance.com/ws/xauusdt@ticker"
    ws = websocket.WebSocketApp(ws_url, on_message=on_message)
    ws.run_forever()

# Start the zero-latency network stream in a background thread
threading.Thread(target=run_websocket, daemon=True).start()

@app.route('/api/data', methods=['GET'])
def get_metrics():
    return jsonify(live_market_state)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
