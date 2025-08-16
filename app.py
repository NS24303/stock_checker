from flask import Flask, render_template_string
import yfinance as yf
from datetime import datetime

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
    <title>Stock & ETF Tickers</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; margin: 40px; }
        h2 { color: #333; }
        table { border-collapse: collapse; width: 80%; margin-bottom: 40px; background: #fff; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #4CAF50; color: white; }
        tr:nth-child(even) { background: #f2f2f2; }
        .datetime { font-size: 1.2em; margin-bottom: 20px; color: #555; }
    </style>
</head>
<body>
    <div class="datetime">{{ current_datetime }}</div>
    <h2>ETF Tickers</h2>
    {{ etf_table|safe }}
    <h2>Indexes</h2>
    {{ index_table|safe }}
    <h2>Stock Tickers</h2>
    {{ company_table|safe }}

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
    table = "<table><tr><th>Name</th><th>Symbol</th><th>Current Price</th><th>Day Change</th><th>Day Change (%)</th><th>Volume</th></tr>"
    for row in rows:
        name, symbol, price_str, day_change, day_change_pct, volume_str = row

        # Style for negative changes
        day_change_style = ' style="color:red;"' if isinstance(day_change, (int, float)) and day_change < 0 else ""
        day_change_pct_style = ' style="color:red;"' if isinstance(day_change_pct, (int, float)) and day_change_pct < 0 else ""

        # Make symbol a hyperlink
        symbol_link = f'<a href="https://uk.finance.yahoo.com/quote/{symbol}" target="_blank">{symbol}</a>'

        table += (
            f"<tr>"
            f"<td>{name}</td>"
            f"<td>{symbol_link}</td>"
            f"<td>{price_str}</td>"
            f"<td{day_change_style}>{day_change}</td>"
            f"<td{day_change_pct_style}>{day_change_pct}</td>"
            f"<td>{volume_str}</td>"
            f"</tr>"
        )
    table += "</table>"
    return table

def my_datetime():
    now = datetime.now()
    day = now.strftime("%A")
    day_num = now.day
    # Suffix for day
    if 4 <= day_num <= 20 or 24 <= day_num <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day_num % 10 - 1]
    month = now.strftime("%B")
    time_str = now.strftime("%H:%M:%S")
    return f"{day} {day_num}{suffix} {month} - {time_str}"

app = Flask(__name__)

@app.route("/")
def index():
    index_tickers = [
        # US Indexs
        "^GSPC", "^SP400", "^SP600", "^IXIC", "^DJI",
        # UK Indexes 
        "^FTSE", "^FTMC", "^FTAS", "AIM5.L", "AIM1.L", 
        # European Indexes
        "^GDAXI", "^FCHI"
    ]
    company_tickers = ["MSFT", "NVDA", "AAPL", "GOOGL", "TSLA", "AMZN", "ANET", "CSCO", "HPE", "META", "NKE", "AVGO", "INTC", "AMD", "BLZE" ]

    etf_tickers = ["CSP1.L", "SPX4.L", "ISF.L", "ISFR.L", "VGER.L", "WDEP.L","FSEU.L", "DXJG.L", "EMVL.L", "VEMT.L", "FLO5.L"]

    current_datetime = my_datetime()

    etf_rows = get_stock_data(etf_tickers)
    etf_table = make_table(etf_rows)

    index_rows = get_stock_data(index_tickers)
    index_table = make_table(index_rows)

    company_rows = get_stock_data(company_tickers)
    company_table = make_table(company_rows)


    return render_template_string(
        HTML_TEMPLATE,
        etf_table=etf_table,
        index_table=index_table,
        company_table=company_table,        
        current_datetime=current_datetime
    )

if __name__ == "__main__":
    app.run(debug=False)