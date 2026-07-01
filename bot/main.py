"""Entry point for the EMA crossover bot.

Usage:
  python bot/main.py --mode [paper|live|backtest] [--symbol SYMBOL] [--since-days N]

"""
import argparse
import os
import time
from bot.config import Config
from bot.exchange_client import ExchangeClient
from bot.strategy import EMACrossoverStrategy
from bot.backtest import Backtester


def run_live_loop(cfg: Config, client: ExchangeClient, strategy: EMACrossoverStrategy):
    print("Starting live/paper loop. Mode:", cfg.mode)
    poll_interval = 60  # seconds (1m)
    while True:
        for symbol in cfg.symbols:
            try:
                ohlcv = client.fetch_ohlcv_multi_tf(symbol)
                signal = strategy.generate_signal(symbol, ohlcv)
                if signal == "BUY":
                    client.enter_position(symbol, cfg)
                elif signal == "SELL":
                    client.exit_position(symbol, cfg)
                # else HOLD
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
        time.sleep(poll_interval)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["paper", "live", "backtest"], default=os.getenv("LIVE_MODE", "paper"))
    parser.add_argument("--symbol", default=None)
    parser.add_argument("--since-days", type=int, default=30)
    args = parser.parse_args()

    cfg = Config()
    cfg.mode = args.mode

    client = ExchangeClient(cfg)
    strategy = EMACrossoverStrategy(cfg)

    if args.mode == "backtest":
        symbol = args.symbol or cfg.symbols[0]
        bt = Backtester(client, strategy, cfg)
        bt.run(symbol, since_days=args.since_days)
    else:
        run_live_loop(cfg, client, strategy)


if __name__ == "__main__":
    main()
