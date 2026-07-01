import ccxt
import time
import pandas as pd

class ExchangeClient:
    def __init__(self, cfg):
        self.cfg = cfg
        # Use ccxt exchange by id
        exchange_class = getattr(ccxt, cfg.exchange_id)
        if cfg.live and cfg.api_key:
            self.exchange = exchange_class({
                'apiKey': cfg.api_key,
                'secret': cfg.secret,
                'password': cfg.password,
                'enableRateLimit': True,
            })
        else:
            # No keys or paper mode: instantiate without creds for public requests
            self.exchange = exchange_class({'enableRateLimit': True})
        # In-memory paper trading state
        self.positions = {}

    def _normalize_symbol(self, symbol: str) -> str:
        # Coinbase Pro uses dashes like BTC-USD; allow simple mapping
        if '/' in symbol and '-' not in symbol:
            base, quote = symbol.split('/')
            return f"{base}-{quote}"
        return symbol

    def fetch_ohlcv(self, symbol: str, timeframe: str, since=None, limit=200):
        s = self._normalize_symbol(symbol)
        # ccxt returns [timestamp, open, high, low, close, volume]
        data = self.exchange.fetch_ohlcv(s, timeframe=timeframe, since=since, limit=limit)
        df = pd.DataFrame(data, columns=["ts", "open", "high", "low", "close", "volume"])
        df["ts"] = pd.to_datetime(df["ts"], unit='ms')
        return df

    def fetch_ohlcv_multi_tf(self, symbol: str):
        # return dict of timeframe -> df
        result = {}
        for tf in self.cfg.timeframes:
            try:
                df = self.fetch_ohlcv(symbol, tf, limit=200)
                result[tf] = df
                time.sleep(self.exchange.rateLimit / 1000)
            except Exception as e:
                print(f"fetch_ohlcv error {symbol} {tf}: {e}")
        return result

    def enter_position(self, symbol: str, cfg):
        # Simplified: buys using max_position_pct of available balance
        if not cfg.live:
            print(f"[PAPER] Entering simulated LONG for {symbol}")
            self.positions[symbol] = {"side": "long", "size_pct": cfg.max_position_pct}
            return None
        # Live: place market buy (user must ensure funds)
        # Implement basic market order (coinbasepro uses 'createMarketOrder')
        s = self._normalize_symbol(symbol)
        print(f"[LIVE] Placing market buy for {s}")
        # The actual amount calculation would need account balance checks — left as TODO
        try:
            order = self.exchange.create_market_buy_order(s, cfg.max_position_pct)
            print("Order placed:", order)
            return order
        except Exception as e:
            print("Order error:", e)
            return None

    def exit_position(self, symbol: str, cfg):
        if symbol not in self.positions and not cfg.live:
            print(f"[PAPER] No position to exit for {symbol}")
            return None
        if not cfg.live:
            print(f"[PAPER] Exiting simulated position for {symbol}")
            self.positions.pop(symbol, None)
            return None
        s = self._normalize_symbol(symbol)
        try:
            order = self.exchange.create_market_sell_order(s, cfg.max_position_pct)
            print("Exit order placed:", order)
            return order
        except Exception as e:
            print("Exit order error:", e)
            return None
