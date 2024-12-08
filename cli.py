import click
from flask.cli import with_appcontext

from database import database
from models.tables import Asset  # ,Transaction, Stock


@click.command("create_all", help="Create all tables in the database")
@with_appcontext
def create_all():
    database.create_all()


@click.command("drop_all", help="Drop all tables in the database")
@with_appcontext
def drop_all():
    database.drop_all()


@click.command("populate", help="Populate the database with dummy data")
@with_appcontext
def populate():

    dummy_transacs = [
        # Transaction(
        #     #transaction_id = db.Column(db.Integer, primary_key=True)
        #     date="20220102",
        #     stock_code="AAPL",
        #     stock_name="Tim Apple",
        #     action="buy",
        #     quantity=5,
        #     cost_or_price=20
        # )
    ]

    dummy_assets = [Asset(cash=50000, stock_value=0)]

    dummy_stocks = [
        # Stock(
        #     stock_code="AAPL",
        #     stock_name="Tim Apple",
        #     quantity=5
        # )
    ]

    for row in dummy_transacs:
        database.session.add(row)

    for row in dummy_assets:
        database.session.add(row)

    for row in dummy_stocks:
        database.session.add(row)

    database.session.commit()
