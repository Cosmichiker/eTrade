"""
Entry point.

Run with: python main.py

This authenticates with E*TRADE once, then checks the strategy signal every
N minutes during market hours. Ctrl+C to stop at any time.
"""
import time
import schedule
import config
from etrade_client import ETradeClient
from trader import run_once

CHECK_INTERVAL_MINUTES = 5


def main():
    print("=" * 60)
    print(f"E*TRADE bot starting | env={config.ENV} | DRY_RUN={config.DRY_RUN}")
    print(f"Ticker: {config.TICKER} | SMA {config.SHORT_WINDOW}/{config.LONG_WINDOW}")
    print("=" * 60)

    if config.DRY_RUN:
        print("Running in DRY RUN mode: no real orders will be placed.\n")
    else:
        print("!! LIVE ORDER PLACEMENT IS ENABLED !!\n")

    client = ETradeClient()

    # If you don't yet have your ACCOUNT_ID_KEY, uncomment the next two lines,
    # run once, copy the accountIdKey from the printed output into your .env,
    # then comment them back out.
    #print(client.list_accounts())
    #return

    if not config.ACCOUNT_ID_KEY and not config.DRY_RUN:
        raise RuntimeError(
            "ETRADE_ACCOUNT_ID_KEY is not set in .env. "
            "Run with the list_accounts() lines uncommented above to find it."
        )

    run_once(client)  # check immediately on startup
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(run_once, client)

    print(f"\nWill re-check every {CHECK_INTERVAL_MINUTES} minutes. Press Ctrl+C to stop.\n")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
