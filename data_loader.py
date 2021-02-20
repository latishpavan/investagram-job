from investagram_data_loader.api.ig_api import InvestagramApi


def main():
    data = InvestagramApi().get_stock_transaction_by_stock_id_and_date(146, '2021/02/19', '2021/02/19')
    print(data)


if __name__ == '__main__':
    main()
