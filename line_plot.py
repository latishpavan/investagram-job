import numpy as np
import pprint
import pandas as pd
import datetime as dt
from collections import defaultdict
import matplotlib.pyplot as plt
from investagram_data_loader.repository.sqlite_dao import SqliteDao

STOCK_CODE = '2GO'
BROKERS = ['BDO', 'ATR']
START_DATE, END_DATE = dt.date(2021, 1, 1), dt.date(2021, 2, 24)

transactions = defaultdict(dict)

with SqliteDao() as dao:
    for trans in dao.get_transactions_by_stock_code(STOCK_CODE, START_DATE, END_DATE):
        transactions[trans.broker_code][trans.date] = trans.net_value

pprint.pprint(transactions)
df = pd.DataFrame(transactions)
# df.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
# df.set_index(['Date'], inplace=True)
df.sort_index(inplace=True)
df.fillna(0, inplace=True)
df = df.cumsum()
df[BROKERS].plot(marker='.')
plt.show()
