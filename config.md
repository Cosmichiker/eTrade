---
name: etrade-config
description: Use this skill when reading or changing config.py — credentials/env loading, the sandbox-vs-live switch, DRY_RUN, or any of the safety-rail constants (MAX_SHARES_PER_ORDER, MAX_ORDERS_PER_DAY, TICKER, SHORT_WINDOW, LONG_WINDOW). Trigger when the user asks to add a config value, change a limit, add a ticker, or touch .env handling.
---

# config.py — Settings & Safety Rails

`config.py` is the single source of truth for tunable values. Every other
file (`strategy.py`, `trader.py`, `etrade_client.py`, `main.py`) reads from
here rather than hardcoding values — keep it that way when adding new
settings.

## Sections

**Credentials (from `.env`, never hardcoded)**
- `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCOUNT_ID_KEY` — E*TRADE OAuth values,
  loaded via `python-dotenv`'s `load_dotenv()`. Default to `""` if missing
  from `.env` — no validation here, so a missing key surfaces later as an
  auth failure in `etrade_client.py`, not at startup.
- `ENV` — `"sandbox"` or `"live"`, read from `ETRADE_ENV`, lower-cased.
  Validated at import time (see below).

**Safety rails** — exist so a bug or bad signal can't do unlimited damage.
Tune, don't remove:

| Setting | Default | Purpose |
|---|---|---|
| `DRY_RUN` | `True` | Orders are logged, never sent, while `True`. |
| `MAX_SHARES_PER_ORDER` | `10` | Hard cap on order size regardless of strategy output. |
| `MAX_ORDERS_PER_DAY` | `3` | Circuit breaker enforced in `trader.py`. |
| `TICKER` | `"AAPL"` | Single symbol the example strategy trades. |

**Strategy parameters**
- `SHORT_WINDOW` (20 days), `LONG_WINDOW` (50 days) — SMA windows consumed
  by `strategy.py`'s `generate_signal()` / `get_current_smas()`.

## Import-time validation

This module has side effects on import, not just constant definitions:
- Raises `ValueError` immediately if `ENV` isn't `"sandbox"` or `"live"` —
  fails fast before any network/auth code runs.
- Prints a loud warning banner if `ENV == "live"` **and** `DRY_RUN is False`
  simultaneously — the one combination that places real orders with real
  money. This is a print, not a hard stop; it doesn't block execution.

## Common modification tasks

**Add a new tunable** — add the constant here with an inline comment
explaining it, not scattered as a magic number in another file.

**Trade multiple tickers** — Let TICKERS be an array of all the stocks that I own on eTrade
`TICKERS = ["AAPL", "MSFT"]`; `trader.py` needs matching changes to loop
per-symbol and track per-symbol daily order counts (see `trader.md`).

**Add a new safety rail** — add it to the table above and enforce it in
`trader.py::run_once()`, the same place the existing rails are checked.

**Add new required credentials** — add `os.getenv(...)` here, and add a
matching entry to `.env.example` so setup instructions stay accurate.

## Things to flag to the user, don't just do silently

- Flipping `DRY_RUN` to `False`.
- Changing `ETRADE_ENV` (or its default) toward `"live"`.
- Raising `MAX_SHARES_PER_ORDER` or `MAX_ORDERS_PER_DAY`.
- Weakening or removing the `ENV`/`DRY_RUN` validation checks at the bottom
  of the file — they're the last line of defense against an accidental
  live-money misconfiguration.
