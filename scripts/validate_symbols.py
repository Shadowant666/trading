#!/usr/bin/env python3
"""Validate and prune symbol list against the specified exchange (ccxt).

Usage:
  python scripts/validate_symbols.py --env .env            # read SYMBOLS from .env
  python scripts/validate_symbols.py --symbols BTC-USD,ETH-USD --exchange coinbasepro
  python scripts/validate_symbols.py --env .env --write   # write pruned list to .env.pruned
  python scripts/validate_symbols.py --env .env --write --inplace  # overwrite .env with pruned list (CAUTION)

The script loads exchange markets via ccxt and compares the provided symbols (supports both dash and slash forms).
It prints valid and invalid symbols and optionally writes a pruned symbol list to a new .env.pruned file or overwrites the source env.

Note: Do NOT store API keys in shared repositories. This script only reads/writes the env file you pass in.
"""
import argparse
import os
import sys
from dotenv import dotenv_values, set_key
import ccxt


def load_symbols_from_env(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Env file not found: {path}")
    data = dotenv_values(path)
    raw = data.get('SYMBOLS') or os.environ.get('SYMBOLS') or ''
    return [s.strip() for s in raw.split(',') if s.strip()]


def normalize_variants(symbol: str):
    # produce common variants to check against exchange lists
    s = symbol.strip()
    s_up = s.upper()
    variants = set()
    variants.add(s_up)
    if '/' in s_up:
        variants.add(s_up.replace('/', '-'))
    if '-' in s_up:
        variants.add(s_up.replace('-', '/'))
    return variants


def fetch_exchange_symbols(exchange_id: str):
    try:
        exchange_class = getattr(ccxt, exchange_id)
    except AttributeError:
        raise ValueError(f"Unknown exchange id for ccxt: {exchange_id}")
    ex = exchange_class({'enableRateLimit': True})
    # load markets
    ex.load_markets()
    market_symbols = set()
    for m in ex.markets.values():
        # m['symbol'] is usually like 'BTC/USD'
        sym = m.get('symbol')
        mid = m.get('id')
        if sym:
            market_symbols.add(sym.upper())
        if mid:
            market_symbols.add(mid.upper())
    return market_symbols


def prune_symbols(candidate_symbols, market_symbols):
    valid = []
    invalid = []
    for s in candidate_symbols:
        variants = normalize_variants(s)
        if variants & market_symbols:
            # pick canonical from variants that is in market_symbols
            found = next(iter(variants & market_symbols))
            # prefer market symbol with dash replaced by '-' if present, else original
            valid.append(found)
        else:
            invalid.append(s)
    return valid, invalid


def write_pruned_to_env(env_path, pruned_symbols, inplace=False, out_path=None):
    if inplace:
        # overwrite the SYMBOLS key in the given env file
        # We use set_key from dotenv to update the file
        set_key(env_path, 'SYMBOLS', ','.join(pruned_symbols))
        return env_path
    else:
        out = out_path or (env_path + '.pruned')
        with open(out, 'w') as f:
            f.write('SYMBOLS=' + ','.join(pruned_symbols) + '\n')
        return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--env', help='.env file to read SYMBOLS from (optional)')
    p.add_argument('--symbols', help='Comma-separated symbols to validate (overrides --env)')
    p.add_argument('--exchange', default=os.environ.get('EXCHANGE', 'coinbasepro'))
    p.add_argument('--write', action='store_true', help='Write pruned symbols to a .pruned env file')
    p.add_argument('--inplace', action='store_true', help='Overwrite the env file (use with --env)')
    args = p.parse_args()

    if not args.symbols and not args.env:
        print('Either --symbols or --env must be provided', file=sys.stderr)
        sys.exit(2)

    if args.symbols:
        candidates = [s.strip() for s in args.symbols.split(',') if s.strip()]
    else:
        candidates = load_symbols_from_env(args.env)

    print(f'Checking {len(candidates)} candidate symbols against exchange {args.exchange}...')

    try:
        market_symbols = fetch_exchange_symbols(args.exchange)
    except Exception as e:
        print('Failed to load markets from exchange:', e, file=sys.stderr)
        sys.exit(1)

    valid, invalid = prune_symbols(candidates, market_symbols)

    print('\nValid symbols (matched to exchange formats):')
    for v in valid:
        print('  ', v)
    print('\nInvalid or not found on exchange:')
    for iv in invalid:
        print('  ', iv)

    if args.write:
        if args.env is None:
            print('\n--write requires --env to be provided to determine output path', file=sys.stderr)
            sys.exit(2)
        out = write_pruned_to_env(args.env, valid, inplace=args.inplace)
        print(f'\nWrote pruned symbols to: {out}')


if __name__ == '__main__':
    main()
