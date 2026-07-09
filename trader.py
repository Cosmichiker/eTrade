"""
Ties everything together: checks the strategy signal for each ticker and
prints a table of SMAs and BUY/SELL/HOLD signals. Does not place any orders.
"""
import datetime
from zoneinfo import ZoneInfo
import config
from strategy import generate_signal, get_current_smas

_EASTERN = ZoneInfo("America/New_York")


def _market_is_open() -> bool:
    """Rough regular-hours check (9:30-16:00 ET, weekdays). Not holiday-aware."""
    now = datetime.datetime.now(_EASTERN)
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close


def _print_sma_table(rows: list):
    """rows: list of (ticker, short_sma, long_sma, signal)."""
    short_header = f"Short SMA ({config.SHORT_WINDOW}d)"
    long_header = f"Long SMA ({config.LONG_WINDOW}d)"
    header = f"{'Ticker':<8}{short_header:>20}{long_header:>20}{'Signal':>10}"
    print(header)
    print("-" * len(header))
    for ticker, short_sma, long_sma, signal in rows:
        print(f"{ticker:<8}{short_sma:>20.2f}{long_sma:>20.2f}{signal:>10}")


def run_once(tickers: list):
    """Checks the signal for each ticker and prints the results. Never places orders."""
    if not _market_is_open():
        print(f"[{datetime.datetime.now()}] Market closed. Skipping.")
        return

    print(f"\n[{datetime.datetime.now()}] Checking {len(tickers)} ticker(s)...")
    rows = [
        (ticker, *get_current_smas(ticker), generate_signal(ticker))
        for ticker in tickers
    ]
    _print_sma_table(rows)
