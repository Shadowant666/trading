# Crypto EMA Crossover Trading Bot

This repository contains a Python trading bot prototype implementing a multi-timeframe EMA crossover strategy. It supports backtesting, paper trading (default), and live trading (requires you to provide API keys and enable LIVE mode).

Important safety notes
- This is not financial advice.
- Test with paper/sandbox mode only until you fully understand and verify behavior.
- Never commit API keys. Use environment variables or a local .env file (excluded from git).

Features
- Multi-timeframe EMA crossover strategy across 1m, 5m, 1h, 1d
- Requires EMA crossover confirmation on at least 2 timeframes before entry (configurable)
- Position sizing (% of portfolio), max drawdown stop, and single-position default
- Backtest script using historical OHLCV via ccxt
- Paper mode (simulated orders) and live-capable mode via ccxt
- Dockerfile for local containerized runs

Quick start (local)
1. Clone this repo locally:
   git clone https://github.com/Shadowant666/trading.git
2. Create and activate a Python environment (3.9+ recommended):
   python -m venv venv
   source venv/bin/activate
3. Install dependencies:
   pip install -r requirements.txt
4. Create a .env file (optional) to set environment variables. Example .env:
   COINBASE_API_KEY=your_api_key
   COINBASE_SECRET=your_api_secret
   COINBASE_PASSWORD=your_api_passphrase
   LIVE=false
   BASE_CURRENCY=USD
   SYMBOLS=BTC-USD,ETH-USD,SOL-USD,XRP-USD,XLM-USD,BTC-EUR,ETH-EUR,BTC-GBP,NEAR-USD,DOGE-USD,USDC-EUR,ZEC-USD

   Note: Ensure symbols match the exchange naming (Coinbase uses e.g. BTC-USD). Edit config or symbols accordingly.

5. Run in paper mode (default):
   python bot/main.py --mode paper

6. Run backtest on a symbol:
   python bot/main.py --mode backtest --symbol BTC-USD --since-days 30

Docker
- Build: docker build -t ema-bot .
- Run (paper): docker run --env LIVE=false --env SYMBOLS="BTC-USD" ema-bot

Files
- bot/: main application code
- requirements.txt: pinned dependencies
- Dockerfile: container image

Next steps
- Adjust SYMBOLS in .env to match Coinbase naming (e.g. BTC-USD)
- Test backtesting thoroughly before enabling LIVE=true and providing real API keys

