"""
Ties everything together: checks the strategy signal for each ticker and
prints a table of SMAs and BUY/SELL/HOLD signals. Does not place any orders.
"""
import datetime
import config
from strategy import generate_signal, get_current_smas


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
    print(f"\n[{datetime.datetime.now()}] Checking {len(tickers)} ticker(s)...")
    rows = [
        (ticker, *get_current_smas(ticker), generate_signal(ticker))
        for ticker in tickers
    ]
    _print_sma_table(rows)
