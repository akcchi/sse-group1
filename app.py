from flask import Flask, render_template, request
import pandas as pd
import akshare as ak
import yfinance as yf

app = Flask(__name__)


def get_stock_data_with_name(file_path, symbol, start_date, end_date):
    stock_name_data = pd.read_csv(file_path, encoding="latin1")
    company_name = stock_name_data.loc[stock_name_data['symbol'] == symbol, 'name'].values
    if len(company_name) == 0:
        return None
    company_name = company_name[0]

    try:
        stock_data = ak.stock_us_daily(symbol=symbol, adjust="qfq")
        stock_data['date'] = pd.to_datetime(stock_data['date'])
        filtered_data = stock_data[(stock_data['date'] >= start_date) & (stock_data['date'] <= end_date)]
        filtered_data = filtered_data[['date', 'close']]
    except:
        try:
            stock_data = yf.download(symbol, start=start_date, end=end_date)
            stock_data.reset_index(inplace=True)
            filtered_data = stock_data[['Date', 'Close']]
            filtered_data.rename(columns={'Date': 'date', 'Close': 'close'}, inplace=True)
        except:
            return None

    filtered_data['code'] = symbol
    filtered_data['name'] = company_name
    filtered_data = filtered_data[['name', 'code', 'date', 'close']]
    return filtered_data


@app.route("/", methods=["GET", "POST"])
def homepage():
    labels = []
    values = []
    symbol = ""
    company_name = ""

    if request.method == "POST":
        file_path = '/Users/zhouyixun/Desktop/SSH/us_stock_name1.csv'
        symbol = request.form.get("symbol")  # Get stock symbol from form input
        start_date = "2021-01-01"
        end_date = "2022-01-01"

        stock_data = get_stock_data_with_name(file_path, symbol, start_date, end_date)

        if stock_data is not None:
            labels = stock_data['date'].dt.strftime('%Y-%m-%d').tolist()
            values = stock_data['close'].tolist()
            company_name = stock_data['name'].iloc[0]  # Get company name

    return render_template(
        'chartjs-example.html',
        labels=labels,
        values=values,
        symbol=symbol,
        company_name=company_name
    )


if __name__ == '__main__':
    app.run(debug=True)
