"""
Configuration for the trading bot.

All secrets come from a local .env file (never hardcoded, never sent anywhere
by this code). Copy .env.example to .env and fill in your own values.
"""
import os
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.getenv("ETRADE_CONSUMER_KEY", "")
CONSUMER_SECRET = os.getenv("ETRADE_CONSUMER_SECRET", "")
ACCOUNT_ID_KEY = os.getenv("ETRADE_ACCOUNT_ID_KEY", "")
ENV = os.getenv("ETRADE_ENV", "sandbox").lower()  # "sandbox" or "live"

# ---- Safety rails -----------------------------------------------------
# These exist so a bug or bad signal can't do unlimited damage.
# Tune them, but don't remove them.

DRY_RUN = True          # If True, orders are logged but NEVER actually sent.
                         # Flip to False only after you've watched DRY_RUN
                         # output and are confident in the logic.

MAX_SHARES_PER_ORDER = 10     # Hard cap on order size, regardless of strategy output.
MAX_ORDERS_PER_DAY = 3        # Circuit breaker on total orders per day.
TICKER = "AAPL"                # Symbol this example strategy trades.

# Strategy parameters (simple moving average crossover)
SHORT_WINDOW = 20   # days
LONG_WINDOW = 50    # days

if ENV not in ("sandbox", "live"):
    raise ValueError("ETRADE_ENV must be 'sandbox' or 'live'")

if ENV == "live" and DRY_RUN is False:
    print(
        "\n"
        "!!! WARNING: ETRADE_ENV=live and DRY_RUN=False !!!\n"
        "This configuration will place REAL orders with REAL money.\n"
        "Make sure that is really what you intend.\n"
    )
