from datetime import date
from investagram_data_loader.logger import logging
from investagram_data_loader.repository.ig_api import InvestagramApi
from investagram_data_loader.constants.mode import DateMode
from investagram_data_loader.date.date_handler import generate_date_range
from investagram_data_loader.repository.sqlite_dao import SqliteDao


def load_transactions_by_stock(stock_name: str, mode: DateMode, from_date: date, to_date: date) -> list:
    transactions = []

    with InvestagramApi() as api:
        stock = api.get_stock_info(stock_name)

        for range_start, range_end in generate_date_range(mode, from_date, to_date):
            transactions.extend(api.get_stock_transaction_by_stock_id_and_date(stock.stock_id, range_start, range_end))

    return transactions


def load_transactions_by_broker(broker_name: str, mode: DateMode, from_date: date, to_date: date):
    transactions = []

    with InvestagramApi() as api:
        broker = api.get_broker_info(broker_name)

        for range_start, range_end in generate_date_range(mode, from_date, to_date):
            transactions.extend(
                api.get_stock_transaction_by_broker_id_and_date(broker.broker_id, range_start, range_end))

    return transactions


def main():
    with SqliteDao() as dao:
        transactions = load_transactions_by_stock('JFC', DateMode.DAILY, date(2021, 2, 10), date(2021, 2, 20))
        dao.bulk_insert_transactions(transactions)


if __name__ == '__main__':
    main()
