import time
import pandas as pd

class Backtester:
    def __init__(self, client, strategy, cfg):
        self.client = client
        self.strategy = strategy
        self.cfg = cfg

    def run(self, symbol: str, since_days=30):
        print(f"Running backtest for {symbol} past {since_days} days")
        # For backtest, use a single timeframe (1h) for step-through simplicity
        tf = '1h'
        limit = int((24 * since_days) + 10)
        df = self.client.fetch_ohlcv(symbol, tf, limit=limit)
        df = df.reset_index(drop=True)
        cash = 10000.0
        position = 0.0
        entry_price = None
        trades = []
        for i in range(35, len(df)):
            window = df.iloc[:i+1]
            # Build minimal multi-tf dict by reusing same df for all tf for simplicity in backtest
            multi = {t: window for t in self.cfg.timeframes}
            signal = self.strategy.generate_signal(symbol, multi)
            price = float(window.iloc[-1]['close'])
            if signal == 'BUY' and position == 0:
                size = (cash * self.cfg.max_position_pct) / price
                position = size
                entry_price = price
                cash -= size * price
                trades.append({'side': 'BUY', 'price': price})
            elif signal == 'SELL' and position > 0:
                cash += position * price
                trades.append({'side': 'SELL', 'price': price})
                position = 0
                entry_price = None
        # finalize
        if position > 0:
            cash += position * price
            position = 0
        pnl = cash - 10000.0
        print(f"Backtest complete. PnL: {pnl:.2f}, Trades: {len(trades)}")
        for t in trades[:50]:
            print(t)
