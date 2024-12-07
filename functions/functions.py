from database import database as db
from models.tables import Transaction, Asset, Stock

#from sqlalchemy import select


# Check that there is enough cash to buy
#
# Args: single dictionary
#   date=(string; e.g. 20220103)​,
#   stock_code=(string),
#   stock_name=(string)​,
#   action=(string; "buy" or "sell")​,
#   quantity=(int)​,
#   cost_or_price=(double)
#
# Returns: bool
#
def check_buy(dict):
    total_cost = float(dict["quantity"]) * dict["cost_or_price"]
    
    assets = db.session.execute(db.select(Asset)).scalar_one()
    
    if (assets.cash - total_cost) >= 0:
        return(True)
    else:
        return(False)



# Check that sell quantity is <= existing owned
#
# Args: single dictionary
#   date=(string; e.g. 20220103)​,
#   stock_code=(string),
#   stock_name=(string)​,
#   action=(string; "buy" or "sell")​,
#   quantity=(int)​,
#   cost_or_price=(double)
#
# Returns: bool
#
def check_sell(dict):
    owned = db.session.execute(
        db.select(Stock).filter_by(stock_code=dict["stock_code"])).first()

    if owned is not None:
        #owned_quantity = owned.quantity
        if dict["quantity"] <= owned[0].quantity:
            return(True)
        else:
            return(False)
    else:
        return(False)


# Update database tables (Stock, Asset, Transaction)
# Give information to update front page data:
#
# Args: single dictionary
#   date=(string; e.g. 20220103)​,
#   stock_code=(string),
#   stock_name=(string)​,
#   action=(string; "buy" or "sell")​,
#   quantity=(int)​,
#   cost_or_price=(double)
#
# Returns: single list
#   Assets.cash (updated assets)
#   Assets.stock_value (updated assets)
#   Transactions.stock_name
#   Transactions.stock_code
#   Transactions.quantity (of the same stock)
#   Average initial cost (for the same stock, i.e. if previously owned)
#
def update_info(dict):
    return_list = []  # store info to be returned

    total_cost = float(dict["quantity"]) * dict["cost_or_price"]

    # See if stock is already owned
    owned_stock = db.session.execute(
        db.select(Stock).filter_by(stock_code=dict["stock_code"])).first()
    
    if owned_stock is not None:  # Already own this stock
        # Update Stock table
        new_quantity = int()
        if dict["action"] == "buy":
            new_quantity = owned_stock[0].quantity + dict["quantity"]
            owned_stock[0].quantity = new_quantity
        elif dict["action"] == "sell":
            new_quantity = owned_stock[0].quantity - dict["quantity"]
            if new_quantity == 0:
                db.session.delete(owned_stock[0])  # Remove entry if all sold
            owned_stock[0].quantity = new_quantity
        db.session.commit()

        # Add row to Transaction table
        if dict["action"] == "buy":
            db.session.add(
                Transaction(
                    date=dict["datetime"],
                    stock_code=dict["stock_code"],
                    stock_name=dict["stock_name"],
                    action="buy",
                    quantity=dict["quantity"],
                    cost_or_price=dict["cost_or_price"]
                )
            )
            db.session.commit()
        elif dict["action"] == "sell":
            db.session.add(
                Transaction(
                    date=dict["datetime"],
                    stock_code=dict["stock_code"],
                    stock_name=dict["stock_name"],
                    action="sell",
                    quantity=dict["quantity"],
                    cost_or_price=dict["cost_or_price"]
                )
            )
            db.session.commit()

        # Update Asset table (cash, stock_value)
        assets = db.session.execute(db.select(Asset)).scalar_one()
        new_cash = float()
        new_stock_value = float()
        if dict["action"] == "buy":
            new_cash = assets.cash - total_cost
            new_stock_value = assets.stock_value + total_cost
        elif dict["action"] == "sell":
            new_cash = assets.cash + total_cost
            new_stock_value = assets.stock_value - total_cost
        assets.cash = new_cash
        assets.stock_value = new_stock_value
        db.session.commit()

        # Calculate average initial cost
        existing_transactions =  db.session.execute(
            db.select(Transaction).filter_by(
                stock_code=dict["stock_code"],
                action="buy")).all()  #.scalars()
        
        running_quantcost = float(0)
        running_quant = float(0)
        for t in existing_transactions:
            running_quantcost += (t[0].quantity * t[0].cost_or_price)
            running_quant += t[0].quantity

        return_list.append(new_cash)
        return_list.append(new_stock_value)
        return_list.append(dict["stock_name"])
        return_list.append(dict["stock_code"])
        return_list.append(new_quantity)
        return_list.append(running_quantcost/running_quant)  # avg initial cost

    else:  # no existing stock owned
        # Only reachable if "buy"; add new row in Stocks table
        db.session.add(
            Stock(
                stock_code=dict["stock_code"],
                stock_name=dict["stock_name"],
                quantity=dict["quantity"]
            )
        )
        db.session.commit()

        # Update Asset table (cash, stock value)
        assets = db.session.execute(db.select(Asset)).scalar_one()
        new_cash = float()
        new_stock_value = float()
        if dict["action"] == "buy":
            new_cash = assets.cash - total_cost
            new_stock_value = assets.stock_value + total_cost
        elif dict["action"] == "sell":
            new_cash = assets.cash + total_cost
            new_stock_value = assets.stock_value - total_cost
        assets.cash = new_cash
        assets.stock_value = new_stock_value
        db.session.commit()

        # Add row to Transaction table
        if dict["action"] == "buy":
            db.session.add(
                Transaction(
                    date=dict["datetime"],
                    stock_code=dict["stock_code"],
                    stock_name=dict["stock_name"],
                    action="buy",
                    quantity=dict["quantity"],
                    cost_or_price=dict["cost_or_price"]
                )
            )
            db.session.commit()
        elif dict["action"] == "sell":
            db.session.add(
                Transaction(
                    date=dict["datetime"],
                    stock_code=dict["stock_code"],
                    stock_name=dict["stock_name"],
                    action="sell",
                    quantity=dict["quantity"],
                    cost_or_price=dict["cost_or_price"]
                )
            )
            db.session.commit()

        return_list.append(new_cash)
        return_list.append(new_stock_value)
        return_list.append(dict["stock_name"])
        return_list.append(dict["stock_code"])
        return_list.append(dict["quantity"])
        return_list.append(dict["cost_or_price"])
    
    print(return_list)    
    return(return_list)


# Get values for current assets
# Return a LIST containing:
#   [0]: float; cash
#   [1]: float; value of all stocks
#   [2]: float; total assets (cash + value of all stocks)
def get_assets():
    return_list = []
    assets = db.session.execute(db.select(Asset)).scalar_one()
    total_assets = assets.cash + assets.stock_value

    return_list.append(assets.cash)
    return_list.append(assets.stock_value)
    return_list.append(total_assets)

    return(return_list)


# Return a LIST containing:
#   stock codes of all owned stocks (string)
def get_owned_stocks():
    return_list = []
    all_stocks = db.session.execute(db.select(Stock)).all()
    for s in all_stocks:
        return_list.append(s.stock_code)
    return(return_list)


# Update Asset table with new stock prices (new day)
# AND
# Return informaion to display, including profit/loss etc. for all stocks
# READ BELOW!!
#
# Arguments: one DICTIONARY containing
#   stock_code: new_price (float)
#
# Returns: one LIST, containing two LISTS
# [0]: LIST size 3, containing 
#   [0]: (float) updated total stock value
#   [1]: (float) updated total assets
#   [2]: (float) percentage change in total assets <-- show top of page!
# [1]: LIST of multiple DICTIONARIES, see below
#   EACH dictionary is for each stock, containing:
#   stock_name: (string)
#   stock_code: (string)
#   total_value: (float)
#   quantity: (int)
#   price: (float) price for new day, same as argument
#   cost: (float) average intial cost
#   pnl_raw: (float) raw difference in total value compared to last day
#   pnl_percent: (float) percentage difference in total value
def update_all(arg_list):
    # Update Asset.stock_value
    # Calculate percentage change
    # Return info
    master_list = []
    assets_values_list = []
    owned_stocks_list = []

    # Update Asset table and generate info for assets_values_list[]
    new_stock_value = float(0)

    codes = list(arg_list.keys())
    for code in codes:
        # Get owned quantity
        owned_stock = db.session.execute(
            db.select(Stock).filter_by(stock_code=code)).first()
        new_stock_value += float(owned_stock[0].quantity) * arg_list[code]

    assets = db.session.execute(db.select(Asset)).scalar_one()
    current_cash = assets.cash
    old_stock_value = assets.stock_value
    
    assets.stock_value = new_stock_value
    db.session.commit()  # Update Asset table

    old_total_assets = old_stock_value + current_cash
    new_total_assets = new_stock_value + current_cash
    total_percent_change = 100 * (
        (new_total_assets - old_total_assets)/old_total_assets
    )

    assets_values_list.append(new_stock_value)
    assets_values_list.append(new_total_assets)
    assets_values_list.append(total_percent_change)
    master_list.append(assets_values_list)

    # Now get info for owned_stocks_list[]

    # Query Stock table
    for code in codes:
        temp_dict = {}
        owned = db.session.execute(
            db.select(Stock).filter_by(stock_code=code)).first()
        
        new_indv_total_value = float(owned[0].quantity) * arg_list[code]

        temp_dict.update({"stock_name": owned[0].stock_name})
        temp_dict.update({"stock_code": code})
        temp_dict.update({"total_value": new_indv_total_value})
        temp_dict.update({"quantity": owned[0].quantity})
        temp_dict.update({"price": arg_list[code]})
        
        # Calc avg initial cost using Transaction table
        existing_transactions =  db.session.execute(
            db.select(Transaction).filter_by(
                stock_code=code,
                action="buy")).all()  #.scalars()
        running_quantcost = float(0)
        running_quant = float(0)
        for t in existing_transactions:
            running_quantcost += (t[0].quantity * t[0].cost_or_price)
            running_quant += t[0].quantity
        avg_initial_cost = running_quantcost/running_quant

        temp_dict.update({"cost": avg_initial_cost})

        old_indv_total_value = avg_initial_cost * float(temp_dict["quantity"])

        temp_dict.update(
            {"pnl_raw": new_indv_total_value - old_indv_total_value})
        
        pnl_percent = 100 * (
            (new_indv_total_value - old_indv_total_value)/old_indv_total_value
        )

        temp_dict.update({"pnl_percent": pnl_percent})

        owned_stocks_list.append(temp_dict)
    
    master_list.append(owned_stocks_list)

    return(master_list)


# Get information on all previous transactions
# Returns one list, containing multiple dictionaries
# Each dictionary is for each transaction, containing:
#   id: (int) transaction ID
#   date: (string) in format e.g. 20220103 (2022 Jan 03)
#   stock_code: (string)
#   stock_name: (string)
#   action: (string) either "buy" or "sell"
#   quantity: (int)
#   cost_or_price: (float)
def get_all_transactions():
    master_list = []
    all_transactions = db.session.execute(db.select(Transaction)).all()

    for t in all_transactions:
        temp_dict = {}
        temp_dict.update({"id": t.transaction_id})
        temp_dict.update({"date": t.date})
        temp_dict.update({"stock_code": t.stock_code})
        temp_dict.update({"stock_name": t.stock_name})
        temp_dict.update({"action": t.action})
        temp_dict.update({"quantity": t.quantity})
        temp_dict.update({"cost_or_price": t.cost_or_price})
        master_list.append(temp_dict)
    
    return(master_list)
