import sys
from datetime import date
from investagram_data_loader.repository.ig_api import InvestagramApi
from investagram_data_loader.constants.mode import DateMode
from investagram_data_loader.date.date_handler import generate_date_range


def load_stock_data(stock_name: str, mode: DateMode, from_date: date, to_date: date) -> list:
    data = []

    with InvestagramApi() as api:
        stock = api.get_stock_info(stock_name)

        for range_start, range_end in generate_date_range(mode, from_date, to_date):
            data.extend(api.get_stock_transaction_by_stock_id_and_date(stock.StockId, range_start, range_end))

    print(sys.getsizeof(data))
    return data


def main():
    print(load_stock_data('JFC', DateMode.DAILY, date(2021, 1, 19), date(2021, 2, 19)))


if __name__ == '__main__':
    main()
