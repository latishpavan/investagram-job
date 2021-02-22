import time
from datetime import date
from investagram_data_loader.logger import logging
from investagram_data_loader.repository.ig_api import InvestagramApi
from investagram_data_loader.constants.mode import DateMode
from investagram_data_loader.date.date_handler import generate_date_range
from investagram_data_loader.repository.sqlite_dao import SqliteDao
from investagram_data_loader.reader.data_reader import get_stocks

SLEEP_TIME = 10
FROM_DATE, TO_DATE = date(2021, 2, 15), date(2021, 2, 20)


def load_transactions_by_stock(stock_code: str, mode: DateMode, from_date: date, to_date: date) -> list:
    transactions = []
    logging.info(f'Loading transaction by stock code {stock_code} from {from_date} to {to_date} on a {mode} basis...')

    with InvestagramApi() as api:
        stock = api.get_stock_info(stock_code)

        for range_start, range_end in generate_date_range(mode, from_date, to_date):
            transactions.extend(api.get_stock_transaction_by_stock_id_and_date(stock.stock_id, range_start, range_end))

    return transactions


def load_transactions_by_broker(broker_code: str, mode: DateMode, from_date: date, to_date: date):
    transactions = []
    logging.info(f'Loading transaction by broker code {broker_code} from {from_date} to {to_date} on a {mode} basis...')

    with InvestagramApi() as api:
        broker = api.get_broker_info(broker_code)

        for range_start, range_end in generate_date_range(mode, from_date, to_date):
            transactions.extend(
                api.get_stock_transaction_by_broker_id_and_date(broker.stock_broker_id, range_start, range_end))

    return transactions


def main():
    logging.info("Downloading data from investagram...")
    stocks = get_stocks(size=2)

    with SqliteDao() as dao:
        for stock in stocks:
            transactions = load_transactions_by_stock(stock, DateMode.DAILY, FROM_DATE, TO_DATE)
            dao.bulk_insert_transactions(transactions)

            logging.info(f'Sleeping for {SLEEP_TIME} seconds...')
            time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
