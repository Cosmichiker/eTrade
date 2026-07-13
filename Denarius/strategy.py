"""
A simple moving-average crossover strategy, used here purely as a working
example of how signals -> orders flow through the bot. This is a textbook
strategy, not a recommendation — it is well known to lag price and whipsaw
in choppy markets. Swap in your own logic once you understand this one.

Rule:
- short-term SMA crosses ABOVE long-term SMA  -> BUY signal
- short-term SMA crosses BELOW long-term SMA  -> SELL signal
- no crossover -> HOLD (do nothing)
"""
import pandas as pd
import yfinance as yf
import config


def get_price_history(symbol: str, days: int = 100) -> pd.DataFrame:
    """
    Pulls daily closes from Yahoo Finance for strategy calculations.
    (E*TRADE's API is used for the actual account/order actions; this is
    just for historical price data to compute the moving averages.)
    """
    data = yf.download(symbol, period=f"{days}d", interval="1d", progress=False)
    if data.empty:
        raise RuntimeError(f"No price data returned for {symbol}")
    return data


def _compute_smas(symbol: str) -> tuple[pd.Series, pd.Series]:
    data = get_price_history(symbol, days=config.LONG_WINDOW + 20)
    closes = data["Close"]
    if isinstance(closes, pd.DataFrame):
        # yfinance >=0.2.31 returns MultiIndex columns (field, ticker) even
        # for a single symbol, so data["Close"] is a 1-column DataFrame here.
        closes = closes.iloc[:, 0]

    short_sma = closes.rolling(window=config.SHORT_WINDOW).mean()
    long_sma = closes.rolling(window=config.LONG_WINDOW).mean()
    return short_sma, long_sma


def get_current_smas(symbol: str) -> tuple[float, float]:
    """Returns the latest (short_sma, long_sma) values, for display purposes."""
    short_sma, long_sma = _compute_smas(symbol)
    return short_sma.iloc[-1], long_sma.iloc[-1]


def generate_signal(symbol: str) -> str:
    """Returns 'BUY', 'SELL', or 'HOLD' based on the current SMA crossover state."""
    short_sma, long_sma = _compute_smas(symbol)

    if len(short_sma.dropna()) < 2 or len(long_sma.dropna()) < 2:
        return "HOLD"  # not enough data yet

    prev_short, prev_long = short_sma.iloc[-2], long_sma.iloc[-2]
    curr_short, curr_long = short_sma.iloc[-1], long_sma.iloc[-1]

    crossed_up = prev_short <= prev_long and curr_short > curr_long
    crossed_down = prev_short >= prev_long and curr_short < curr_long

    if crossed_up:
        return "BUY"
    elif crossed_down:
        return "SELL"
    return "HOLD"
