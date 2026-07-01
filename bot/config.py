import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.exchange_id = os.getenv("EXCHANGE", "coinbasepro")
        self.mode = os.getenv("MODE", "paper")
        # Pruned symbol list normalized for Coinbase (use hyphens)
        raw = os.getenv("SYMBOLS", "BTC-USD,ETH-USD,SOL-USD,XRP-USD,XLM-USD,BTC-EUR,ETH-EUR,BTC-GBP,NEAR-USD,DOGE-USD,USDC-EUR,ZEC-USD")
        self.symbols = [s.strip() for s in raw.split(",") if s.strip()]
        self.timeframes = ["1m", "5m", "1h", "1d"]
        # Strategy params
        self.ema_short = int(os.getenv("EMA_SHORT", "12"))
        self.ema_long = int(os.getenv("EMA_LONG", "26"))
        self.confirmation_required = int(os.getenv("CONFIRMATION_REQUIRED", "2"))
        # Risk
        self.max_position_pct = float(os.getenv("MAX_POSITION_PCT", "0.05"))
        self.max_drawdown = float(os.getenv("MAX_DRAWDOWN", "0.10"))
        self.max_positions = int(os.getenv("MAX_POSITIONS", "1"))
        # API keys (do NOT commit)
        self.api_key = os.getenv("COINBASE_API_KEY")
        self.secret = os.getenv("COINBASE_SECRET")
        self.password = os.getenv("COINBASE_PASSWORD")
        # Live toggle
        self.live = os.getenv("LIVE", "false").lower() in ("1", "true", "yes")

