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
        raise RuntimeError(f"Network error: {e}") from e
    except ValueError as e:
        raise RuntimeError(f"Data error: {e}") from e


def process_stock_data(data, limit=10):
    if not data or "Time Series (5min)" not in data:
        raise ValueError("No valid data found.")

    time_series = data["Time Series (5min)"]
    processed_data = []

    for i, (timestamp, metrics) in enumerate(time_series.items()):
        if i >= limit:
            break
        try:
            processed_data.append(
                {
                    "timestamp": timestamp,
                    "open": float(metrics["1. open"]),
                    "high": float(metrics["2. high"]),
                    "low": float(metrics["3. low"]),
                    "close": float(metrics["4. close"]),
                    "volume": int(metrics["5. volume"]),
                }
            )
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Error at {timestamp}: {e}") from e

    return processed_data


if __name__ == "__main__":
    symbol = "AAPL"
    interval = "5min"
    try:
        data = fetch_stock_data(symbol, interval)
        stock_data = process_stock_data(data, limit=10)
        for entry in stock_data:
            print(
                f"Timestamp: {entry['timestamp']}, Open: 
                {entry['open']}, "
                f"High: {entry['high']}, Low: {entry['low']}, 
                Close: {entry['close']}, "
                f"Volume: {entry['volume']}"
            )
            print("-" * 50)
    except RuntimeError as e:
        print(f"An error occurred: {e}")
