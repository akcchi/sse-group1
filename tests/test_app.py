from app import get_stock_data_with_name
from datetime import datetime, timedelta

file_path = "./blueprints/us_stock_name1.csv"

date = "2022-01-03"
current_date = datetime.strptime(date, "%Y-%m-%d")
one_year_ago = current_date - timedelta(days=365)
end_date = current_date.strftime("%Y-%m-%d")
start_date = one_year_ago.strftime("%Y-%m-%d")


# Non-existent stock
def test_non_existent_stock():
    assert (
        get_stock_data_with_name(file_path, "ABCDEFG", start_date, end_date)
        == 1
    )


# Real stock GOOGL (Alphabet Inc.)
def test_existing_stock():
    assert (
        get_stock_data_with_name(file_path, "GOOGL", start_date, end_date) == 2
    )
