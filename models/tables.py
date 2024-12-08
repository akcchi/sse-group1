from database import database as db


class Transaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    stock_code = db.Column(db.String, nullable=False)
    stock_name = db.Column(db.String, nullable=False)
    action = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cost_or_price = db.Column(db.Float, nullable=False)


class Asset(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    cash = db.Column(db.Float, nullable=False)
    stock_value = db.Column(db.Float, nullable=False)


class Stock(db.Model):
    stock_id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String, nullable=False)
    stock_name = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
