"""
Ties everything together: checks the strategy signal, applies safety rails,
and places (or dry-run logs) orders through the E*TRADE client.
"""
import datetime
import config
from etrade_client import ETradeClient
from strategy import generate_signal

# Tracks how many orders we've placed today, to enforce the circuit breaker.
_orders_today = 0
_orders_today_date = None


def _reset_daily_counter_if_needed():
    global _orders_today, _orders_today_date
    today = datetime.date.today()
    if _orders_today_date != today:
        _orders_today = 0
        _orders_today_date = today


def _market_is_open() -> bool:
    """Rough regular-hours check (9:30-16:00 ET, weekdays). Not holiday-aware."""
    now = datetime.datetime.now()
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close


def run_once(client: ETradeClient):
    """Checks the signal one time and acts on it if conditions allow."""
    global _orders_today
    _reset_daily_counter_if_needed()

    if not _market_is_open():
        print(f"[{datetime.datetime.now()}] Market closed. Skipping.")
        return

    if _orders_today >= config.MAX_ORDERS_PER_DAY:
        print(f"[{datetime.datetime.now()}] Daily order limit reached ({config.MAX_ORDERS_PER_DAY}). Skipping.")
        return

    signal = generate_signal(config.TICKER)
    print(f"[{datetime.datetime.now()}] Signal for {config.TICKER}: {signal}")

    if signal in ("BUY", "SELL"):
        quantity = min(config.MAX_SHARES_PER_ORDER, config.MAX_SHARES_PER_ORDER)
        client.place_order(config.TICKER, quantity, signal)
        _orders_today += 1
    else:
        print("No action taken (HOLD).")
