# E*TRADE Moving-Average Bot (starter)

A minimal automated trading bot for E*TRADE, built as a learning example.
It watches one stock, computes a 20/50-day simple moving average (SMA)
crossover, and places a market order when the SMAs cross.

**This is a teaching example, not a profitable strategy.** SMA crossover is
one of the simplest, most well-known strategies out there — it lags price
and tends to whipsaw (buy-sell-buy-sell with small losses) in sideways
markets. Treat it as a working skeleton to learn on and replace with your
own logic once you're comfortable with how the pieces fit together.

## Safety defaults (read this before changing anything)

- `DRY_RUN = True` in `config.py` — orders are logged to your terminal but
  **never actually sent**. Leave this on until you've watched it run for a
  while and understand exactly what it would have done.
- `ETRADE_ENV=sandbox` in `.env` — even once you flip `DRY_RUN` off, this
  keeps you on E*TRADE's fake-money sandbox rather than your real account.
- `MAX_SHARES_PER_ORDER` and `MAX_ORDERS_PER_DAY` — hard caps so a bug can't
  spiral into a runaway sequence of orders.
- The bot only trades during regular market hours (9:30am-4pm ET, weekdays).

**Recommended path:** run in `sandbox` + `DRY_RUN=True` first → then
`sandbox` + `DRY_RUN=False` (real fake-money orders in the sandbox) → only
then consider `live`. Go slowly. Automated trading bugs cost real money
fast, and there's no "undo" on a filled order.

## Setup

1. **Get E*TRADE API keys**: register a free app at
   https://developer.etrade.com/ — you'll get a sandbox consumer key/secret
   immediately; live keys require an approved brokerage account.

2. **Install dependencies** (Python 3.9+):
   ```
   pip install -r requirements.txt
   ```

3. **Configure credentials**:
   ```
   cp .env.example .env
   ```
   Open `.env` and fill in `ETRADE_CONSUMER_KEY` and `ETRADE_CONSUMER_SECRET`.
   Leave `ETRADE_ACCOUNT_ID_KEY` blank for now — you'll fill that in next.

4. **Find your account ID key** (one-time):
   In `main.py`, uncomment the two lines under "If you don't yet have your
   ACCOUNT_ID_KEY...". Run `python main.py`, complete the browser login step,
   and copy the `accountIdKey` value from the printed output into your `.env`.
   Then re-comment those two lines.

5. **Run it**:
   ```
   python main.py
   ```
   The first time, it'll open a browser tab for you to log into E*TRADE and
   authorize the app, then ask you to paste back a verification code shown
   on that page. This has to be repeated each time you restart the script
   (E*TRADE tokens expire after inactivity or at midnight ET).

## How it works

- `strategy.py` — pulls recent daily closes (via Yahoo Finance, since
  E*TRADE's free quote API doesn't give historical OHLC bars) and checks
  for a 20/50-day SMA crossover.
- `etrade_client.py` — handles E*TRADE login and order placement.
- `trader.py` — the decision loop: checks market hours, daily order limits,
  and the strategy signal, then calls the client to (dry-run or actually)
  place an order.
- `main.py` — authenticates once, then re-checks every 15 minutes while the
  market is open.

## Customizing the strategy

Everything strategy-related lives in `strategy.py`'s `generate_signal()`
function. It just needs to return `"BUY"`, `"SELL"`, or `"HOLD"` — swap the
SMA logic for anything you like (RSI, breakout levels, multi-asset rules,
whatever). `config.py` holds the tunable parameters (`SHORT_WINDOW`,
`LONG_WINDOW`, `TICKER`, position sizing).

## What this doesn't do (yet)

- No stop-losses or position tracking across restarts (it doesn't know if
  it currently holds shares — it just fires signals blindly).
- No portfolio management — single ticker, fixed size.
- No error/retry handling for network hiccups or API rate limits.
- No logging to a file — everything just prints to the terminal.

These are natural next steps once the basic loop feels solid. I'm happy to
help build any of them out when you're ready.

## Disclaimer

This code is provided for educational purposes. It is not financial advice,
and I'm not a financial advisor. Trading involves risk of loss. You are
responsible for testing this thoroughly and understanding exactly what it
does before connecting it to a live account.
