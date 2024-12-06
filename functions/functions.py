from database import database as db
from models.tables import Transaction, Asset, Stock

#from sqlalchemy import select


# Check that there is enough cash to buy
# Args: dict
#   date=(datetime)​,
#   stock_code=(string),
#   stock_name=(string)​,
#   action=(string "buy" or "sell")​,
#   quantity=(int)​,
#   cost_or_price=(double)
# Return: bool
def check_buy(dict):
    total_cost = float(dict["quantity"]) * dict["cost_or_price"]
    
    assets = db.session.execute(db.select(Asset)).scalar_one()
    
    if (assets.cash - total_cost) >= 0:
        return(True)
    else:
        return(False)



# Check that sell quantity is <= existing owned
# Args: dict
#   date=(datetime)​,
#   stock_code=(string),
#   stock_name=(string)​,
#   action=(string "buy" or "sell")​,
#   quantity=(int)​,
#   cost_or_price=(int)
# Returns: bool
def check_sell(dict):
    sell_quantity = dict["quantity"]
    stock_code = dict["stock_code"]
    

    owned = db.session.execute(
        db.select(Stock).filter_by(stock_code=stock_code)).first()

    if owned is not None:
        owned_quantity = owned.quantity
        if sell_quantity <= owned_quantity:
            return(True)
        else:
            return(False)
    else:
        return(False)

# Give informationupdate front page data:
# Args: dict
#   date=(datetime)​,
#   stock_code=(string),
#   stock_name=(string)​,
#   action=(string "buy" or "sell")​,
#   quantity=(int)​,
#   cost_or_price=(int)
# Returns: list
# (updated assets)
#   Assets.cash
#   Assets.stock_value
# (for the same stock)
#   Transactions.stock_name
#   Transactions.stock_code
#   Transactions.quantity
#   Average initial cost
def update_info(dict):
    return_list = []  # store info to be returned

    new_stock_code = dict["stock_code"]
    add_quantity = dict["quantity"]
    total_cost = float(dict["quantity"]) * dict["cost_or_price"]

    owned_stock = db.session.execute(
        db.select(Stock).filter_by(stock_code=new_stock_code)).first()
    
    if owned_stock is not None:
        # Update Stocks table
        new_quantity = owned_stock.quantity + add_quantity
        owned_stock.quantity = new_quantity

        # Update Assets table (cash, stock value)
        assets = db.session.execute(db.select(Asset)).scalar_one()
        new_cash = assets.cash - total_cost
        new_stock_value = assets.stock_value + total_cost
        assets.cash = new_cash
        assets.stock_value = new_stock_value

        # Add row to Transactions table
        if dict["action"] == "buy":
            db.session.add(
                Transaction(
                    date=dict["datetime"],
                    stock_code=new_stock_code,
                    stock_name=dict["stock_name"],
                    action="buy",
                    quantity=add_quantity,
                    cost_or_price=dict["cost_or_price"]
                )
            )
        elif dict["action"] == "sell":
            db.session.add(
                Transaction(
                    date=dict["datetime"],
                    stock_code=new_stock_code,
                    stock_name=dict["stock_name"],
                    action="sell",
                    quantity=add_quantity,
                    cost_or_price=dict["cost_or_price"]
                )
            )
        
        # Calculate average initial cost
        existing_transactions =  db.session.execute(
            db.select(Transaction).filter_by(
                stock_code=new_stock_code,
                action="buy")).scalars()
        
        running_quantcost = 0
        running_quant = 0
        for t in existing_transactions:
            running_quantcost += (t.quantity * t.cost_or_price)
            running_quant += t.quantity

        db.session.commit()

        return_list.append(new_cash)
        return_list.append(new_stock_value)
        return_list.append(dict["stock_name"])
        return_list.append(dict["stock_code"])
        return_list.append(new_quantity)
        return_list.append(running_quantcost/running_quant)  # avg initial cost

    else:  # no existing stock owned
        # New row in Stocks table
        db.session.add(
            Stock(
                stock_code=new_stock_code,
                stock_name=dict["stock_name"],
                quantity=add_quantity
            )
        )

        # Update Assets table (cash, stock value)
        assets = db.session.execute(db.select(Asset)).scalar_one()
        new_cash = assets.cash - total_cost
        new_stock_value = assets.stock_value + total_cost
        assets.cash = new_cash
        assets.stock_value = new_stock_value

        # Add row to Transactions table
        if dict["action"] == "buy":
            db.session.add(
                Transaction(
                    date=dict["datetime"],
                    stock_code=new_stock_code,
                    stock_name=dict["stock_name"],
                    action="buy",
                    quantity=add_quantity,
                    cost_or_price=dict["cost_or_price"]
                )
            )
        elif dict["action"] == "sell":
            db.session.add(
                Transaction(
                    date=dict["datetime"],
                    stock_code=new_stock_code,
                    stock_name=dict["stock_name"],
                    action="sell",
                    quantity=add_quantity,
                    cost_or_price=dict["cost_or_price"]
                )
            )

        db.session.commit()

        return_list.append(new_cash)
        return_list.append(new_stock_value)
        return_list.append(dict["stock_name"])
        return_list.append(dict["stock_code"])
        return_list.append(add_quantity)
        return_list.append(dict["cost_or_price"])
    print(return_list)    
    return(return_list)

