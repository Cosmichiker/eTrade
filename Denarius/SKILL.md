---
name: etrade-bot
description: Use this skill whenever working on the E*TRADE moving-average trading bot project (files like main.py, config.py, strategy.py, trader.py, etrade_client.py in this folder). Covers how to add/change strategies, adjust safety rails, add new tickers, and understand the sandbox/live and dry-run switches. Trigger this whenever the user asks to modify the bot's strategy, trading logic, order behavior, scheduling, or safety limits.
---

# E*TRADE Moving-Average Bot

A local Python bot that watches one stock, computes an SMA crossover signal,
and places orders through E*TRADE's API. Built as a learning skeleton — see
`README.md` in this folder for setup/run instructions.

## File map

- `config.py` — all tunable settings and safety rails live here. Read this
  first before changing behavior.
- `strategy.py` — `generate_signal(symbol)` returns `"BUY"`, `"SELL"`, or
  `"HOLD"`. This is the only function that needs to change to swap strategies.
- `etrade_client.py` — E*TRADE OAuth login, quotes, and order placement.
  Rarely needs edits unless adding new order types (limit orders, options,
  etc.) or new API calls.
- `trader.py` — the decision loop: market-hours check, daily order cap,
  calls `generate_signal()`, calls `client.place_order()`.
- `main.py` — entry point; authenticates once, then runs `trader.run_once()`
  on a schedule (default every 15 min).

## Safety rails — never remove, only loosen deliberately

These live in `config.py`:

| Setting | Purpose |
|---|---|
| `DRY_RUN` | When `True`, orders are logged, never sent. Default `True`. |
| `ETRADE_ENV` (.env) | `sandbox` (fake money) vs `live` (real money). |
| `MAX_SHARES_PER_ORDER` | Hard cap regardless of what strategy computes. |
| `MAX_ORDERS_PER_DAY` | Circuit breaker in `trader.py`. |

**Rule of thumb when editing:** any change that could increase order size,
frequency, or switch environments should be called out explicitly to the
user before applying it — don't silently loosen a safety rail while making
an unrelated change.

## Common modification tasks

**Add a new strategy** — write a new function in `strategy.py` (or a new
file, e.g. `strategy_rsi.py`) that returns `"BUY"`/`"SELL"`/`"HOLD"`, then
point `trader.py`'s import at it. Keep the signature the same
(`generate_signal(symbol) -> str`) so nothing else needs to change.

**Trade multiple tickers** — `config.TICKER` is currently a single string.
To support a list, change it to `TICKERS = ["AAPL", "MSFT"]`, loop over them
in `trader.run_once()`, and give each ticker its own entry in the daily
order-count tracking (currently a single global counter).

**Add position tracking** — the bot currently fires signals without knowing
if it already holds shares (noted as a known gap in the README). To add
this: call `client.accounts.get_account_balance()` or track fills locally
in a small JSON/SQLite file, and check current position before sending a
BUY/SELL.

**Change the schedule** — `CHECK_INTERVAL_MINUTES` in `main.py`.

**Add stop-loss / take-profit** — this needs position + entry-price
tracking (see above) plus a check each loop comparing current price to
entry price, independent of the SMA signal.

## Things to flag to the user, don't just do silently

- Any edit that would flip `DRY_RUN` to `False` or `ETRADE_ENV` to `live`.
- Any edit that increases `MAX_SHARES_PER_ORDER` or `MAX_ORDERS_PER_DAY`.
- Any new strategy logic — remind the user this is still not investment
  advice and hasn't been backtested unless they've done so themselves.
