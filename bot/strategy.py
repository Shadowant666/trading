import pandas as pd

class EMACrossoverStrategy:
    def __init__(self, cfg):
        self.cfg = cfg

    def _compute_emas(self, df: pd.DataFrame, short: int, long: int):
        close = df['close'].astype(float)
        ema_short = close.ewm(span=short, adjust=False).mean()
        ema_long = close.ewm(span=long, adjust=False).mean()
        df = df.copy()
        df['ema_short'] = ema_short
        df['ema_long'] = ema_long
        return df

    def timeframe_signal(self, df: pd.DataFrame):
        df = self._compute_emas(df, self.cfg.ema_short, self.cfg.ema_long)
        if len(df) < 2:
            return "HOLD"
        prev = df.iloc[-2]
        last = df.iloc[-1]
        # Crossover from below -> buy
        if prev['ema_short'] <= prev['ema_long'] and last['ema_short'] > last['ema_long']:
            return "BUY"
        # Crossunder -> sell
        if prev['ema_short'] >= prev['ema_long'] and last['ema_short'] < last['ema_long']:
            return "SELL"
        return "HOLD"

    def generate_signal(self, symbol: str, ohlcv_multi: dict):
        # ohlcv_multi: {tf: df}
        signals = []
        for tf, df in ohlcv_multi.items():
            if df is None or df.empty:
                continue
            s = self.timeframe_signal(df)
            signals.append(s)
        # Count BUY vs SELL
        buys = signals.count("BUY")
        sells = signals.count("SELL")
        if buys >= self.cfg.confirmation_required and buys > sells:
            print(f"Signal BUY for {symbol}: {buys} timeframe confirmations")
            return "BUY"
        if sells >= self.cfg.confirmation_required and sells > buys:
            print(f"Signal SELL for {symbol}: {sells} timeframe confirmations")
            return "SELL"
        return "HOLD"
