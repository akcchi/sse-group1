import requests
from requests.exceptions import RequestException

API_KEY = "xxxxxxxxxxxx"

def fetch_stock_data(symbol, interval="5min"):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY,
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "Time Series (5min)" not in data:
            raise ValueError("Invalid response format or API limit reached.")
        return data
    except RequestException as e:
        print(f"Network error: {e}")
        return None
    except ValueError as e:
        print(f"Data error: {e}")
        return None

def process_stock_data(data, limit=10):
    if not data or "Time Series (5min)" not in data:
        print("No valid data found.")
        return

    time_series = data["Time Series (5min)"]
    count = 0

    for timestamp, metrics in time_series.items():
        if count >= limit:
            break
        try:
            open_price = float(metrics["1. open"])
            high_price = float(metrics["2. high"])
            low_price = float(metrics["3. low"])
            close_price = float(metrics["4. close"])
            volume = int(metrics["5. volume"])
            print(f"Timestamp: {timestamp}")
            print(
                f"Open: {open_price}, High: {high_price}, Low: {low_price}, "
                f"Close: {close_price}, Volume: {volume}"
            )
            print("-" * 50)
            count += 1
        except (KeyError, ValueError) as e:
            print(f"Error processing data at {timestamp}: {e}")

if __name__ == "__main__":
    symbol = "AAPL"
    interval = "5min"
    data = fetch_stock_data(symbol, interval)
    process_stock_data(data, limit=10)
