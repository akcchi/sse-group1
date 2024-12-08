import requests


API_KEY = "xxxxxxxxxxxx"


def fetch_stock_data(symbol, interval="5min"):
    """
    Returns:
        dict: Parsed JSON data from Alpha Vantage API.
    """
    base_url = "https://www.alphavantage.co/query"

    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None


def process_stock_data(data):

    if not data or "Time Series (5min)" not in data:
        print("No valid data found.")
        return

    time_series = data["Time Series (5min)"]
    for timestamp, metrics in time_series.items():
        open_price = metrics["1. open"]
        high_price = metrics["2. high"]
        low_price = metrics["3. low"]
        close_price = metrics["4. close"]
        volume = metrics["5. volume"]
        print(f"Timestamp: {timestamp}")
        print(
            f"Open: {open_price}, High: {high_price}, Low: {low_price}, "
            f"Close: {close_price}, Volume: {volume}"
        )
        print("-" * 50)
