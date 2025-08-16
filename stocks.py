import yfinance as yf

CURRENCY_SYMBOLS = {
    "USD": "$",
    "GBP": "£",
    "GBp": "£",  # Display as pounds after conversion
    "EUR": "€",
    "JPY": "¥",
}

def check_stocks(tickers, group_name):

    print(f"\nPrices for {group_name}:\n" + "=" * (12 + len(group_name)))

    for symbol in tickers:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d")
        if hist.empty:
            print(f"{symbol}: No data found.")
            continue

        name = info.get("longName", symbol)
        current_price = info.get("regularMarketPrice", "N/A")
        previous_close = info.get("regularMarketPreviousClose", "N/A")
        volume = info.get("regularMarketVolume", "N/A")
        currency = info.get("currency", "")
        currency_symbol = CURRENCY_SYMBOLS.get(currency, currency)

        # Convert GBp to GBP
        if currency == "GBp":
            if isinstance(current_price, (int, float)):
                current_price = round(current_price / 100, 2)
            if isinstance(previous_close, (int, float)):
                previous_close = round(previous_close / 100, 2)
            currency = "GBP"  # For display

        if isinstance(current_price, (int, float)):
            price_str = f"{currency_symbol}{current_price}"
        else:
            price_str = str(current_price)

        if isinstance(current_price, (int, float)) and isinstance(previous_close, (int, float)):
            day_change = round(current_price - previous_close, 2)
            if previous_close != 0:
                day_change_pct = round((day_change / previous_close) * 100, 2)
            else:
                day_change_pct = "N/A"
        else:
            day_change = "N/A"
            day_change_pct = "N/A"

        if isinstance(volume, int):
            volume_str = "{:,}".format(volume)
        else:
            volume_str = str(volume)            

        print(f"{name} ({symbol})")
        print(f"  Current Price: {price_str}")
        #print(f"  Currency: {currency}")
        print(f"  Day Change: {day_change}")
        print(f"  Day Change (%): {day_change_pct}")
        print(f"  Volume: {volume_str}")
        print("-" * 40)

if __name__ == "__main__":
    company_tickers = ["AAPL", "GOOGL", "MSFT", "NVDA", "TSLA", "CSCO", "META", "ANET", "NKE", "BLZE", "AMZN"]
    etf_tickers = ["DXJG.L", "FLO5.L", "ISF.L", "CSP1.L", "EMVL.L", "ISFR.L", "FSEU.L", 
                   "SPX4.L","VGER.L", "VEMT.L", "WDEP.L"]

    check_stocks(company_tickers, "companies")
    check_stocks(etf_tickers, "ETFs")