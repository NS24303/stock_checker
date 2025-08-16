from flask import Flask, render_template_string
import yfinance as yf

CURRENCY_SYMBOLS = {
    "USD": "$",
    "GBP": "£",
    "GBp": "£",
    "EUR": "€",
    "JPY": "¥",
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Stock & ETF Prices</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; margin: 40px; }
        h2 { color: #333; }
        table { border-collapse: collapse; width: 80%; margin-bottom: 40px; background: #fff; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #4CAF50; color: white; cursor: pointer; }
        tr:nth-child(even) { background: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Prices for Companies</h2>
    {{ company_table|safe }}
    <h2>Prices for ETFs</h2>
    {{ etf_table|safe }}
</body>
</html>
"""

def get_stock_data(tickers):
    rows = []
    for symbol in tickers:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current_price = info.get("regularMarketPrice", "N/A")
        previous_close = info.get("regularMarketPreviousClose", "N/A")
        volume = info.get("regularMarketVolume", "N/A")
        currency = info.get("currency", "")
        currency_symbol = CURRENCY_SYMBOLS.get(currency, currency)
        name = info.get("longName", symbol)

        # Convert GBp to GBP
        if currency == "GBp":
            if isinstance(current_price, (int, float)):
                current_price = round(current_price / 100, 2)
            if isinstance(previous_close, (int, float)):
                previous_close = round(previous_close / 100, 2)
            currency = "GBP"

        if isinstance(current_price, (int, float)) and isinstance(previous_close, (int, float)):
            day_change = round(current_price - previous_close, 2)
            day_change_pct = round((day_change / previous_close) * 100, 2) if previous_close != 0 else "N/A"
        else:
            day_change = "N/A"
            day_change_pct = "N/A"

        if isinstance(volume, int):
            volume_str = "{:,}".format(volume)
        else:
            volume_str = str(volume)

        price_str = f"{currency_symbol}{current_price}" if isinstance(current_price, (int, float)) else str(current_price)

        rows.append([
            name, symbol, price_str, day_change, day_change_pct, volume_str
        ])
    return rows

def make_table(rows):
    table = '<table><tr><th>Name</th><th>Symbol</th><th>Current Price</th><th>Day Change</th><th>Day Change (%)</th><th>Volume</th></tr>'
    for row in rows:
        name, symbol, price_str, day_change, day_change_pct, volume_str = row

        # Style for negative changes
        day_change_style = ' style="color:red;"' if isinstance(day_change, (int, float)) and day_change < 0 else ""
        day_change_pct_style = ' style="color:red;"' if isinstance(day_change_pct, (int, float)) and day_change_pct < 0 else ""

        table += (
            f"<tr>"
            f"<td>{name}</td>"
            f"<td>{symbol}</td>"
            f"<td>{price_str}</td>"
            f"<td{day_change_style}>{day_change}</td>"
            f"<td{day_change_pct_style}>{day_change_pct}</td>"
            f"<td>{volume_str}</td>"
            f"</tr>"
        )
    table += "</table>"
    return table

app = Flask(__name__)

@app.route("/")
def index():
    company_tickers = ["AAPL", "GOOGL", "MSFT", "NVDA", "TSLA", "CSCO", "META", "ANET", "NKE", "BLZE", "AMZN"]
    etf_tickers = ["DXJG.L", "FLO5.L", "ISF.L", "CSP1.L", "EMVL.L", "ISFR.L", "FSEU.L", "SPX4.L", "VGER.L", "VEMT.L", "WDEP.L"]

    company_rows = get_stock_data(company_tickers)
    etf_rows = get_stock_data(etf_tickers)
    company_table = make_table(company_rows)
    etf_table = make_table(etf_rows)

    return render_template_string(HTML_TEMPLATE, company_table=company_table, etf_table=etf_table)

if __name__ == "__main__":
    app.run(debug=True)