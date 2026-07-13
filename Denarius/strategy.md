---
name: etrade-strategy
description: Use this skill when reading, changing, or replacing the signal logic in strategy.py (the SMA-crossover strategy used by the E*TRADE bot). Covers what generate_signal() does, its inputs/outputs, and how to safely swap in a different strategy.
---

# strategy.py — SMA Crossover Signal

`strategy.py` is the only file that decides **what** to trade (BUY/SELL/HOLD).
It has no knowledge of order sizing, safety rails, or scheduling — those live
in `trader.py` and `config.py`. Keep it that way: this file should stay a
pure "price data in, signal out" module.

## Functions

- `get_price_history(symbol, days=100) -> pd.DataFrame`
  Pulls daily OHLC data from Yahoo Finance (`yfinance`) — used only for
  historical prices to compute moving averages, not for trading (E*TRADE's
  API handles the actual account/order side, in `etrade_client.py`). Raises
  `RuntimeError` if Yahoo returns no data for the symbol.

- `generate_signal(symbol) -> str`
  Returns `"BUY"`, `"SELL"`, or `"HOLD"`. This is the function `trader.py`
  calls each loop. Logic:
  1. Fetches `config.LONG_WINDOW + 20` days of closes.
  2. Computes a short SMA (`config.SHORT_WINDOW`, default 20 days) and a long
     SMA (`config.LONG_WINDOW`, default 50 days).
  3. Compares the previous bar vs. the current bar:
     - short SMA crosses **above** long SMA → `BUY`
     - short SMA crosses **below** long SMA → `SELL`
     - no crossover, or not enough data yet → `HOLD`

## Gotchas already handled in the code

- `yfinance >= 0.2.31` returns MultiIndex columns even for a single symbol,
  so `data["Close"]` comes back as a 1-column DataFrame, not a Series. The
  code unwraps this with `closes.iloc[:, 0]` — don't remove that check when
  editing, or comparisons downstream will break silently.
- Needs at least 2 non-NaN values in both rolling SMAs before it will emit a
  signal; otherwise returns `HOLD` rather than raising.

## Swapping in a new strategy

Keep the signature identical — `generate_signal(symbol: str) -> str`
returning one of `"BUY"`/`"SELL"`/`"HOLD"` — so `trader.py` doesn't need to
change. Either edit this function directly or add a new file (e.g.
`strategy_rsi.py`) and repoint the import in `trader.py`.

This is a textbook crossover strategy used as a working example, not a
recommendation — it lags price and whipsaws in choppy markets. Flag to the
user that any new strategy logic is unvalidated/not backtested unless they
say otherwise (see `SKILL.md` for the project-wide safety rails this feeds
into, e.g. `MAX_SHARES_PER_ORDER`, `DRY_RUN`).
