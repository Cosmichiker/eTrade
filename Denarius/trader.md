---
name: etrade-trader
description: Use this skill when reading or changing trader.py (the decision loop of the E*TRADE bot) — market-hours gating, the daily order-count circuit breaker, or how strategy signals turn into order calls. Trigger when the user asks to change scheduling behavior, order sizing, the daily order cap, or market-hours logic.
---

# trader.py — Decision Loop

`trader.py` is the orchestrator: it does not decide *what* to trade (that's
`strategy.py`) or *how orders are placed* (that's `etrade_client.py`). Its
only job is deciding **whether** to act on a signal right now, given time-of-day
and daily-limit constraints, then forwarding to the client.

## Functions

- `_reset_daily_counter_if_needed()` — resets the module-level `_orders_today`
  counter when the calendar date rolls over. Uses two module globals
  (`_orders_today`, `_orders_today_date`) as in-memory state — this resets to
  zero on every process restart, it is **not** persisted to disk.

- `_market_is_open() -> bool` — regular-hours check, 9:30–16:00, Mon–Fri.
  **Not holiday-aware** and uses `datetime.datetime.now()`, i.e. the host
  machine's local time zone — it assumes the machine is running in US
  Eastern time. If deploying somewhere else (e.g. a UTC cloud VM), this will
  silently gate trading at the wrong hours.

- `run_once(client: ETradeClient)` — called on a schedule by `main.py`.
  Order of checks each call:
  1. Reset daily counter if the date changed.
  2. Skip if market is closed.
  3. Skip if `_orders_today >= config.MAX_ORDERS_PER_DAY`.
  4. Call `generate_signal(config.TICKER)`.
  5. If `BUY`/`SELL`: place the order via `client.place_order()` and
     increment `_orders_today`. If `HOLD`: no-op.

## Known quirk

`quantity = min(config.MAX_SHARES_PER_ORDER, config.MAX_SHARES_PER_ORDER)`
(trader.py:50) — both arguments are the same constant, so this always just
evaluates to `MAX_SHARES_PER_ORDER`. There's no dynamic position sizing yet;
every BUY/SELL trades the full cap. If you add sizing logic (e.g. scale by
signal strength or available cash), this is the line to change — but call it
out to the user since it changes order size behavior.

## Common modification tasks

**Change the daily order cap or market hours** — cap lives in
`config.MAX_ORDERS_PER_DAY`; hours are hardcoded in `_market_is_open()`.
Flag any increase to the cap per the project safety-rail rules in `SKILL.md`.

**Add per-ticker order tracking** — `_orders_today` is a single global
counter. If `config.TICKER` becomes a list (see `SKILL.md`), this needs to
become a dict keyed by symbol, and `run_once()` needs to loop over tickers.

**Persist the daily counter** — currently in-memory only, so a crash/restart
mid-day resets the circuit breaker. If that matters, write `_orders_today`
and `_orders_today_date` to a small file/SQLite row after each order.

**Add position awareness** — `run_once()` currently fires BUY/SELL blindly
off the signal with no check of current holdings (documented gap, see
`SKILL.md` → "Add position tracking").

## Things to flag to the user, don't just do silently

- Any change to `_market_is_open()` that widens the trading window.
- Any change to order quantity logic (the quirk above) — this directly
  changes how much money moves per trade.
- Raising `MAX_ORDERS_PER_DAY` or otherwise weakening the circuit breaker.
## Outputs
- Display all the SMAs in terminal