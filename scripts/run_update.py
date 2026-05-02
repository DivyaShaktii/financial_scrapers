from backend.universe import STOCKS
from backend.services.data_updater import update_stock

for stock in STOCKS:
    update_stock(stock)