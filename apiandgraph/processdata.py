import pandas as pd
import matplotlib.pyplot as plt

stock_data = []
num_tickers = int(input("Enter the number of tickers: "))

# Input data for each ticker
for i in range(num_tickers):
    print(f"\nTicker {i + 1}:")
    ticker = input("Enter the ticker name (e.g., Imperial Fund): ")
    amount_bought = int(input("Enter the amount bought (number of shares): "))
    timestamps = []
    prices = []

    num_timestamps = int(
        input(f"Enter the number of price timestamps for {ticker}: ")
    )

    for j in range(num_timestamps):
        timestamp = input(
            f"Enter timestamp {j + 1} (e.g., YYYY-MM-DD 00:00:00): "
        )
        price = float(input(f"Enter price at {timestamp}: "))
        timestamps.append(timestamp)
        prices.append(price)

    stock_data.append(
        {
            "Ticker": ticker,
            "Amount Bought": amount_bought,
            "Timestamps": timestamps,
            "Prices": prices,
        }
    )

total_pnl = 0
all_dataframes = []

for stock in stock_data:
    data = {"Timestamp": stock["Timestamps"], "Price": stock["Prices"]}
    df = pd.DataFrame(data)

    # Convert Timestamp to datetime
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    # Calculate PnL as the difference between consecutive prices
    df["PnL"] = df["Price"].diff() * stock["Amount Bought"]

    # Calculate percentage PnL relative to the previous price
    df["PnL (%)"] = (
        df["PnL"] / (df["Price"].shift(1) * stock["Amount Bought"])
    ) * 100

    # Display results for the ticker
    print(f"\nPnL for Ticker: {stock['Ticker']}")
    print(df)

    # Add the total PnL for this stock
    stock_pnl = df["PnL"].sum()
    total_pnl += stock_pnl

    # Append DataFrame to the list for later use
    all_dataframes.append((stock["Ticker"], df))

# Display the total PnL across all tickers
print(f"\nTotal PnL across all tickers: {total_pnl:.2f} USD")

# Plot the PnL for each ticker
for ticker, df in all_dataframes:
    plt.figure(figsize=(10, 6))
    plt.plot(df["Timestamp"], df["PnL"], label=f"PnL ({ticker})", marker=":")
    plt.title(f"Profit and Loss Over Time for {ticker}")
    plt.xlabel("Timestamp")
    plt.ylabel("PnL (USD)")
    plt.grid()
    plt.legend()
    plt.show()
