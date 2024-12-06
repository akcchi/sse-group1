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
        elif dict["action"] == "sell":
            new_quantity = owned_stock[0].quantity - dict["quantity"]
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
                action="buy")).scalars()
        
        running_quantcost = float(0)
        running_quant = float(0)
        for t in existing_transactions:
            running_quantcost += (t.quantity * t.cost_or_price)
            running_quant += t.quantity

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

