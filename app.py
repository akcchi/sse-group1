from flask import Flask, render_template, request, session

# from itertools import zip_longest
import pandas as pd
import akshare as ak
import yfinance as yf
from datetime import datetime, timedelta
import os

from database import database

# Register cli commands
from cli import create_all, drop_all, populate

from functions.functions import (
    check_buy,
    check_sell,
    update_info,
    update_all,
    reset_db,
)


def get_stock_data_with_name(file_path, symbol, start_date, end_date):
    stock_name_data = pd.read_csv(file_path, encoding="latin1")
    company_name = stock_name_data.loc[
        stock_name_data["symbol"] == symbol, "name"
    ].values
    if len(company_name) == 0:
        return 1  # no company
    company_name = company_name[0]

    try:
        stock_data = ak.stock_us_daily(symbol=symbol, adjust="qfq")
        stock_data["date"] = pd.to_datetime(stock_data["date"])
        filtered_data = stock_data[
            (stock_data["date"] >= start_date)
            & (stock_data["date"] <= end_date)
        ]
        filtered_data = filtered_data[["date", "close"]]
    except Exception:
        try:
            stock_data = yf.download(symbol, start=start_date, end=end_date)
            stock_data.reset_index(inplace=True)
            filtered_data = stock_data[["Date", "Close"]]
            filtered_data.rename(
                columns={"Date": "date", "Close": "close"}, inplace=True
            )
        except Exception:
            return 2  # no data

    try:
        date = session.get("datetime")
        formatted_date = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
        session["cost_or_price"] = filtered_data[
            filtered_data["date"] == formatted_date
        ]["close"].iloc[0]
    except Exception:
        return 2

    filtered_data["code"] = symbol
    filtered_data["name"] = company_name
    filtered_data = filtered_data[["name", "code", "date", "close"]]

    session["stock_code"] = symbol
    session["stock_name"] = company_name

    return filtered_data


def update():
    stock_codes = session.get("stock_codes")
    new_stock_price = {}
    new_stock_price1 = []
    date = datetime.strptime(session.get("datetime"), "%Y%m%d").strftime(
        "%Y-%m-%d"
    )
    for code in stock_codes:
        stock_data = ak.stock_us_daily(symbol=code, adjust="qfq")
        price = stock_data[stock_data["date"] == date]["close"].iloc[0]
        new_stock_price[code] = price
        new_stock_price1.append(price)

    session["price"] = new_stock_price1
    lt1, lt2 = update_all(new_stock_price)
    session["total_stock_value"] = lt1[0]
    session["increase"] = lt1[2]


app = Flask(__name__, static_url_path="/assets", static_folder="static/assets")

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tables.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///file::memory:?uri=true"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.urandom(24).hex()

# Set up extensions
database.init_app(app)


with app.app_context():
    app.cli.add_command(create_all)
    app.cli.add_command(drop_all)
    app.cli.add_command(populate)


@app.before_request
def initialize_sessions():
    if not session.get("initialized"):
        session["initialized"] = True
        session["cash"] = 50000
        session["total_stock_value"] = 0
        session["increase"] = 0
        session["stock_names"] = []
        session["stock_codes"] = []
        session["stock_quantity"] = []
        session["price"] = []
        session["average_initial_cost"] = []


@app.route("/")
@app.route("/index")
def lets_play_a_game():
    session.clear()
    reset_db()
    return render_template("index.html")


@app.route("/first_day")
def first_day():
    session["datetime"] = "20220103"
    cash = session.get("cash")
    increase = session.get("increase")
    stock_names = session.get("stock_names")
    stock_codes = session.get("stock_codes")
    stock_quantity = session.get("stock_quantity")
    stock_price = session.get("price")
    average_initial_cost = session.get("average_initial_cost")

    if len(stock_price) == len(stock_quantity) == len(average_initial_cost):
        stock_value = [
            price * quantity
            for price, quantity in zip(stock_price, stock_quantity)
        ]
        profit_num = [
            (price - cost) * quantity
            for price, cost, quantity in zip(
                stock_price, average_initial_cost, stock_quantity
            )
        ]
        profit_per = [
            (price - cost) / cost
            for price, cost in zip(stock_price, average_initial_cost)
        ]
    else:
        stock_value = []
        profit_num = []
        profit_per = []

    total_stock_value = session.get("total_stock_value")
    total_asset = cash + total_stock_value

    return render_template(
        "first_day.html",
        total_asset=total_asset,
        cash=cash,
        total_stock_value=total_stock_value,
        increase=increase,
        stock_name=stock_names,
        stock_code=stock_codes,
        stock_value=stock_value,
        stock_quantity=stock_quantity,
        stock_price=stock_price,
        average_initial_cost=average_initial_cost,
        profit_num=profit_num,
        profit_per=profit_per,
        zip=zip,
    )


@app.route("/middle_day")
def middle_day():
    session["datetime"] = "20220603"
    update()
    cash = session.get("cash")
    increase = session.get("increase")
    stock_names = session.get("stock_names")
    stock_codes = session.get("stock_codes")
    stock_quantity = session.get("stock_quantity")
    stock_price = session.get("price")
    average_initial_cost = session.get("average_initial_cost")

    if len(stock_price) == len(stock_quantity) == len(average_initial_cost):
        stock_value = [
            price * quantity
            for price, quantity in zip(stock_price, stock_quantity)
        ]
        profit_num = [
            (price - cost) * quantity
            for price, cost, quantity in zip(
                stock_price, average_initial_cost, stock_quantity
            )
        ]
        profit_per = [
            (price - cost) / cost
            for price, cost in zip(stock_price, average_initial_cost)
        ]
    else:
        stock_value = []
        profit_num = []
        profit_per = []

    total_stock_value = session.get("total_stock_value")
    total_asset = cash + total_stock_value

    return render_template(
        "middle_day.html",
        total_asset=total_asset,
        cash=cash,
        total_stock_value=total_stock_value,
        increase=increase,
        stock_name=stock_names,
        stock_code=stock_codes,
        stock_value=stock_value,
        stock_quantity=stock_quantity,
        stock_price=stock_price,
        average_initial_cost=average_initial_cost,
        profit_num=profit_num,
        profit_per=profit_per,
        zip=zip,
    )


@app.route("/last_day")
def last_day():
    session["datetime"] = "20230103"
    update()
    cash = session.get("cash")
    increase = session.get("increase")
    stock_names = session.get("stock_names")
    stock_codes = session.get("stock_codes")
    stock_quantity = session.get("stock_quantity")
    stock_price = session.get("price")
    average_initial_cost = session.get("average_initial_cost")

    if len(stock_price) == len(stock_quantity) == len(average_initial_cost):
        stock_value = [
            price * quantity
            for price, quantity in zip(stock_price, stock_quantity)
        ]
        profit_num = [
            (price - cost) * quantity
            for price, cost, quantity in zip(
                stock_price, average_initial_cost, stock_quantity
            )
        ]
        profit_per = [
            (price - cost) / cost
            for price, cost in zip(stock_price, average_initial_cost)
        ]
    else:
        stock_value = []
        profit_num = []
        profit_per = []

    total_stock_value = session.get("total_stock_value")
    total_asset = cash + total_stock_value

    return render_template(
        "last_day.html",
        total_asset=total_asset,
        cash=cash,
        total_stock_value=total_stock_value,
        increase=increase,
        stock_name=stock_names,
        stock_code=stock_codes,
        stock_value=stock_value,
        stock_quantity=stock_quantity,
        stock_price=stock_price,
        average_initial_cost=average_initial_cost,
        profit_num=profit_num,
        profit_per=profit_per,
        zip=zip,
    )


@app.route("/settlement")
def settlement():
    cash = session.get("cash")
    total_stock_value = session.get("total_stock_value")
    total_asset = cash + total_stock_value
    earning = total_asset - 50000.0
    return render_template("settlement.html", earning=earning)


@app.route("/search", methods=["POST"])
def search():
    labels = []
    values = []
    symbol = ""
    company_name = ""
    latest_price = None

    file_path = "./blueprints/us_stock_name1.csv"
    symbol = request.form.get("symbol")
    date = request.form.get("date")  # Get stock symbol from form input
    current_date = datetime.strptime(date, "%Y-%m-%d")
    one_year_ago = current_date - timedelta(days=365)
    end_date = current_date.strftime("%Y-%m-%d")
    start_date = one_year_ago.strftime("%Y-%m-%d")

    if date == "2022-01-03":
        session["day_page"] = "/first_day"
    elif date == "2022-06-03":
        session["day_page"] = "/middle_day"

    day_page = session.get("day_page")

    stock_data = get_stock_data_with_name(
        file_path, symbol, start_date, end_date
    )

    if isinstance(stock_data, int):
        if stock_data == 1:
            return render_template(
                "error.html",
                error_code="error code: 400",
                error_message="There is no such code in the US stock market.",
                # return_url = previous_page
            )
        elif stock_data == 2:
            return render_template(
                "error.html",
                error_code="error code: 404",
                error_message="Sorry, we don't find price of this stock.",
                # return_url = previous_page
            )
    else:
        labels = stock_data["date"].dt.strftime("%Y-%m-%d").tolist()
        values = stock_data["close"].tolist()
        company_name = session.get("stock_name")
        latest_price = values[-1] if values else None

    return render_template(
        "chartjs-example.html",
        labels=labels,
        values=values,
        symbol=symbol,
        company_name=company_name,
        latest_price=latest_price,
        return_url=day_page,
    )


def update_session(info):
    # [46421.8, 3578.2, 'Apple, Inc.', 'AAPL', 20, 178.91]
    print(info)
    session["cash"] = info[0]
    session["total_stock_value"] = info[1]

    stock_names = session.get("stock_names")
    stock_codes = session.get("stock_codes")
    stock_quantity = session.get("stock_quantity")
    prices = session.get("price")
    average_initial_cost = session.get("average_initial_cost")
    price = session.get("cost_or_price")

    if info[3] in stock_codes:
        index = stock_codes.index(info[3])
        if info[4] != 0:
            stock_quantity[index] = info[4]
            average_initial_cost[index] = info[5]
            prices[index] = price
        else:
            stock_names.pop(index)
            stock_codes.pop(index)
            stock_quantity.pop(index)
            prices.pop(index)
            average_initial_cost.pop(index)

    else:
        stock_names.append(info[2])
        stock_codes.append(info[3])
        stock_quantity.append(info[4])
        average_initial_cost.append(info[5])
        prices.append(price)

    session["stock_names"] = stock_names
    session["stock_codes"] = stock_codes
    session["stock_quantity"] = stock_quantity
    session["price"] = prices
    session["average_initial_cost"] = average_initial_cost

    print("update successfully")


@app.route("/buy_or_sell", methods=["GET"])
def buy_or_sell():
    number = request.args.get("number")
    # price =
    action = request.args.get("action")
    day_page = session.get("day_page")

    para = {}
    para["datetime"] = session.get("datetime")
    para["stock_name"] = session.get("stock_name")
    para["stock_code"] = session.get("stock_code")
    para["action"] = action
    para["quantity"] = int(number)
    para["cost_or_price"] = session.get("cost_or_price")

    try:
        if not number:
            return render_template(
                "error_back_to_day.html",
                error_code="error code: 400",
                error_message="Number is required",
                return_url=day_page,
            )

        if action == "buy":

            if check_buy(para):
                info = update_info(para)
                update_session(info)
                return render_template(
                    "result.html",
                    message=f"Bought {number} shares",
                    return_url=day_page,
                )
            else:
                return render_template(
                    "error_back_to_day.html",
                    error_code="error code: 400",
                    error_message="You don't have enough money",
                    return_url=day_page,
                )

        elif action == "sell":
            if check_sell(para):
                info = update_info(para)
                update_session(info)
                return render_template(
                    "result.html",
                    message=f"Sold {number} shares",
                    return_url=day_page,
                )
            else:
                return render_template(
                    "error_back_to_day.html",
                    error_code="error code: 400",
                    error_message="You don't have enough stocks",
                    return_url=day_page,
                )

    except Exception as e:
        return render_template(
            "error_back_to_day.html",
            error_code="error code: 500",
            error_message=str(e),
            return_url=day_page,
        )


if __name__ == "__main__":
    app.run(debug=True)
