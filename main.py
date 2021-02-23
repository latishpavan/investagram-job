import time
import json
from datetime import date
from dynaconf import settings
from requests.exceptions import HTTPError
from investagram_data_loader.logger import logging
from investagram_data_loader.repository.ig_api import InvestagramApi
from investagram_data_loader.constants.mode import DateMode
from investagram_data_loader.date.date_handler import generate_date_range
from investagram_data_loader.repository.sqlite_dao import SqliteDao
from investagram_data_loader.reader.data_reader import get_stocks
from investagram_data_loader.exceptions import NoDataFoundException

# global settings here
SLEEP_TIME = 10
FROM_DATE, TO_DATE = date(2020, 1, 1), date(2021, 2, 20)


def load_transactions_by_stock(api: InvestagramApi, stock_code: str, mode: DateMode, from_date: date,
                               to_date: date) -> list:
    transactions = []
    logging.info(f'Loading transaction by stock code {stock_code} from {from_date} to {to_date} on a {mode} basis...')

    stock = api.get_stock_info(stock_code)

    for range_start, range_end in generate_date_range(mode, from_date, to_date):
        transactions.extend(api.get_stock_transaction_by_stock_id_and_date(stock.stock_id, range_start, range_end))

    return transactions


def load_transactions_by_broker(api: InvestagramApi, broker_code: str, mode: DateMode, from_date: date, to_date: date):
    transactions = []
    logging.info(f'Loading transaction by broker code {broker_code} from {from_date} to {to_date} on a {mode} basis...')

    broker = api.get_broker_info(broker_code)

    for range_start, range_end in generate_date_range(mode, from_date, to_date):
        transactions.extend(api.get_stock_transaction_by_broker_id_and_date(
            broker.stock_broker_id, range_start, range_end)
        )

    return transactions


def main():
    logging.info("Downloading data from investagram...")
    # replace with 'size=-1' to download all the stocks data
    stocks, unprocessed = get_stocks(size=-1), []

    with SqliteDao() as dao:
        with InvestagramApi() as api:
            for stock in stocks:
                try:
                    transactions = load_transactions_by_stock(api, stock, DateMode.DAILY, FROM_DATE, TO_DATE)
                    dao.bulk_insert_transactions(transactions)

                    logging.info(f'Sleeping for {SLEEP_TIME} seconds...')
                    time.sleep(SLEEP_TIME)

                except NoDataFoundException as exp:
                    logging.error(f'No data found for stock code {stock}.')
                    unprocessed.append(stock)

                except HTTPError as exp:
                    logging.error(f'Non-zero http status found {exp}.')
                    unprocessed.append(stock)

    if len(unprocessed) != 0:
        logging.error(f'Found {len(unprocessed)} unprocessed stock codes: {unprocessed}. Dumping to a file.')

        with open(settings.UNPROCESSED_CODES_FILE, 'w') as fd:
            fd.writelines(unprocessed)


if __name__ == '__main__':
    main()
