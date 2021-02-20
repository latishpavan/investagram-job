import keyring
import requests
from typing import List
from datetime import date
from investagram_data_loader.constants.app import *
from investagram_data_loader.constants.user import *
from investagram_data_loader.constants.endpoints import *
from investagram_data_loader.models.stock import Stock
from investagram_data_loader.models.result import StockBrokerResult


def _load_password():
    return keyring.get_password(BASE_HOST, USER_NAME)


def construct_login_body():
    return {
        'AccessToken': '',
        'AppId': None,
        'ApplicationType': 1,
        'DeviceId': DEVICE_ID,
        'DeviceName': "Chrome 88.0.4324.182",
        'IsRememberMe': True,
        'Password': _load_password(),
        'RequestComingFromType': 3,
        'Username': USER_NAME
    }


class InvestagramApi:
    _instance = None

    def __init__(self):
        self._http_client = requests.Session()
        self._setup_client()

    def _setup_client(self):
        self._http_client.headers.update({'Origin': ORIGIN, 'Referer': REFERER})
        self._authenticate()

    def _authenticate(self):
        response = self._http_client.post(f'{BASE_HOST}{AUTHENTICATION_ENDPOINT}', data=construct_login_body())
        self._http_client.cookies = response.cookies

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)

        return cls._instance

    def get_stock_info(self, stock_name: str) -> Stock:
        params = {
            'limit': 0,
            'keyword': stock_name.lower(),
            'userDefaultExchangeType': 1,
            'selectedExchangeType': 1,
        }

        response = self._http_client.get(f'{BASE_HOST}{STOCK_ID}', params=params)
        return Stock.from_dict(response.json()[0])

    def _get_transactions(self, url: str, params: dict, from_date: date, to_date: date) -> List[StockBrokerResult]:
        date_format = '%Y/%m/%d'

        params = {
            'fromDate': from_date.strftime(date_format),
            'toDate': to_date.strftime(date_format),
            **params,
        }

        response = self._http_client.post(url, params=params)
        ret = [StockBrokerResult(**data) for data in response.json()]

        return ret

    def get_stock_transaction_by_stock_id_and_date(self, stock_id: int, from_date: date, to_date: date) -> List[
                                                                                                    StockBrokerResult]:
        return self._get_transactions(
            f'{BASE_HOST}{STOCK_TRANSACTION_BY_STOCK_ID}',
            {'stockId': stock_id},
            from_date,
            to_date
        )

    def get_stock_transaction_by_broker_id_and_date(self, broker_id: int, from_date: date, to_date: date) -> List[
                                                                                                    StockBrokerResult]:
        return self._get_transactions(
            f'{BASE_HOST}{STOCK_TRANSACTION_BY_BROKER_ID}',
            {'brokerId': broker_id},
            from_date,
            to_date
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._http_client.close()
