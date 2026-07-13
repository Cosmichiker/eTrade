"""
Thin wrapper around pyetrade for authentication, price history, and orders.

E*TRADE uses OAuth 1.0a with a manual step: you'll open a URL, log into
E*TRADE in your browser, and paste back a verification code. This has to
happen once per session (the token expires at midnight ET or after 2 hours
of inactivity), so this script will prompt you for it each time you run it.
"""
import webbrowser
import pyetrade
import config


class ETradeClient:
    def __init__(self):
        if not config.CONSUMER_KEY or not config.CONSUMER_SECRET:
            raise RuntimeError(
                "Missing ETRADE_CONSUMER_KEY / ETRADE_CONSUMER_SECRET. "
                "Copy .env.example to .env and fill in your own credentials "
                "from https://developer.etrade.com/"
            )
        self.env = config.ENV
        self._authenticate()

    def _authenticate(self):
        oauth = pyetrade.ETradeOAuth(
            config.CONSUMER_KEY,
            config.CONSUMER_SECRET,
        )
        auth_url = oauth.get_request_token()

        print(f"\n1. Opening (or copy/paste) this URL in your browser:\n{auth_url}\n")
        try:
            webbrowser.open(auth_url)
        except Exception:
            pass

        verifier_code = input("2. Log in, authorize the app, then paste the verification code here: ").strip()
        tokens = oauth.get_access_token(verifier_code)

        self.market = pyetrade.ETradeMarket(
            config.CONSUMER_KEY,
            config.CONSUMER_SECRET,
            tokens["oauth_token"],
            tokens["oauth_token_secret"],
            dev=(self.env == "sandbox"),
        )
        self.accounts = pyetrade.ETradeAccounts(
            config.CONSUMER_KEY,
            config.CONSUMER_SECRET,
            tokens["oauth_token"],
            tokens["oauth_token_secret"],
            dev=(self.env == "sandbox"),
        )
        self.orders = pyetrade.ETradeOrder(
            config.CONSUMER_KEY,
            config.CONSUMER_SECRET,
            tokens["oauth_token"],
            tokens["oauth_token_secret"],
            dev=(self.env == "sandbox"),
        )
        print(f"Authenticated. Running in '{self.env}' mode.\n")

    def list_accounts(self):
        """Helper to find your ACCOUNT_ID_KEY the first time you run this."""
        return self.accounts.list_accounts(resp_format="json")

    # securityType values this bot will fetch. "EQ" = equity, "MF" = mutual
    # fund. NOTE: place_order() only calls E*TRADE's equity order endpoints
    # (preview_equity_order/place_equity_order). Mutual funds actually need
    # E*TRADE's separate Mutual Fund order API (different fields, cutoff
    # times, minimums) which isn't implemented here -- if DRY_RUN is ever
    # False, a live MF order routed through the equity endpoint is untested
    # and may be rejected or behave unexpectedly. Included anyway per user
    # request; flag this to the user again before turning DRY_RUN off.
    SUPPORTED_SECURITY_TYPES = ("EQ", "MF")

    def get_positions(self) -> list:
        """
        Returns the list of ticker symbols currently held in the account
        (config.ACCOUNT_ID_KEY) whose securityType is in
        SUPPORTED_SECURITY_TYPES, via E*TRADE's portfolio API. Other types
        (options, bonds, etc.) are skipped and reported, since neither the
        strategy nor place_order() supports them.
        """
        portfolio = self.accounts.get_account_portfolio(
            account_id_key=config.ACCOUNT_ID_KEY, count=200, resp_format="json"
        )
        response = (portfolio or {}).get("PortfolioResponse") or {}

        # E*TRADE's JSON collapses a single-item list to a lone dict, so
        # normalize both AccountPortfolio and Position to lists.
        account_portfolios = response.get("AccountPortfolio", [])
        if isinstance(account_portfolios, dict):
            account_portfolios = [account_portfolios]

        symbols = []
        skipped = []
        for account_portfolio in account_portfolios:
            positions = account_portfolio.get("Position", [])
            if isinstance(positions, dict):
                positions = [positions]

            for position in positions:
                product = position.get("Product") or {}
                symbol = product.get("symbol")
                security_type = product.get("securityType")
                if not symbol:
                    continue
                if security_type not in (None,) + self.SUPPORTED_SECURITY_TYPES:
                    skipped.append(f"{symbol} ({security_type})")
                    continue
                if symbol not in symbols:
                    symbols.append(symbol)

        if skipped:
            print(f"Skipped unsupported positions (not tradeable by this bot): {', '.join(skipped)}")

        return symbols

    def get_daily_closes(self, symbol: str, days: int = 60):
        """Fetch recent daily closing prices for a symbol."""
        quote = self.market.get_quote([symbol], resp_format="json")
        # NOTE: E*TRADE's free quote endpoint gives live/delayed quotes,
        # not full historical OHLC series. For real backtesting/strategy
        # data, plug in a market-data provider (e.g. yfinance) here instead.
        return quote

    def place_order(self, symbol: str, quantity: int, action: str):
        """
        action: 'BUY' or 'SELL'
        Places a market order. Respects DRY_RUN from config.
        """
        if config.DRY_RUN:
            print(f"[DRY RUN] Would place order: {action} {quantity} {symbol}")
            return {"dry_run": True, "action": action, "quantity": quantity, "symbol": symbol}

        preview = self.orders.preview_equity_order(
            account_id_key=config.ACCOUNT_ID_KEY,
            symbol=symbol,
            order_action=action,
            client_order_id="bot-" + symbol,
            price_type="MARKET",
            quantity=quantity,
            order_term="GOOD_FOR_DAY",
            market_session="REGULAR",
        )
        print(f"Order preview: {preview}")

        result = self.orders.place_equity_order(
            account_id_key=config.ACCOUNT_ID_KEY,
            symbol=symbol,
            order_action=action,
            client_order_id="bot-" + symbol,
            price_type="MARKET",
            quantity=quantity,
            order_term="GOOD_FOR_DAY",
            market_session="REGULAR",
            preview_id=preview["PreviewOrderResponse"]["PreviewIds"][0]["previewId"],
        )
        print(f"Order placed: {result}")
        return result
