import keyring
import requests
from typing import List
from http import HTTPStatus
from dynaconf import settings
from functools import lru_cache
from stringcase import snakecase
from datetime import datetime, date
from investagram_data_loader.logger import logging
from investagram_data_loader.constants.app import *
from investagram_data_loader.constants.user import *
from investagram_data_loader.constants.endpoints import *
from investagram_data_loader.exceptions import NoDataFoundException
from investagram_data_loader.repository.sqlite_dao import Stock, Broker, Transaction, upsert_stock, upsert_broker


def process_response(response: dict) -> dict:
    processed_response = {}

    for key, value in response.items():
        processed_response[snakecase(key)] = value

    return processed_response


def _load_password():
    return keyring.get_password(BASE_HOST, settings.USER_NAME)


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
        'Username': settings.USER_NAME
    }


class InvestagramApi:
    _instance = None

    def __init__(self):
        self._http_client = requests.Session()
        self._setup_client()

    def _setup_client(self):
        def response_hook(response, **kwargs):
            response.raise_for_status()

        self._http_client.headers.update({'Origin': ORIGIN, 'Referer': REFERER})
        self._http_client.hooks['response'].append(response_hook)
        self.authenticate()

    def authenticate(self):
        login_body = construct_login_body()
        logging.info(f'Authenticating user...')
        response = self._http_client.post(f'{BASE_HOST}{AUTHENTICATION_ENDPOINT}', data=login_body)
        self._http_client.cookies = response.cookies

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)

        return cls._instance

    @lru_cache(maxsize=200)
    @upsert_broker
    def get_broker_info(self, broker_code: str) -> Broker:
        data = {
            "ExchangeType": 1,
            "IsAnalytics": False,
            "IsByBroker": True,
            "IsGetData": True,
            "Keyword": broker_code.lower()
        }

        response = self._http_client.post(f'{BASE_HOST}{BROKER_ID}', data=data)
        response_json = response.json()

        logging.info(f'Received response from the api with status {response.status_code} for the broker code '
                     f'{broker_code}: {response_json}')

        if len(response_json) == 0:
            raise NoDataFoundException(f'No data found for broker code {broker_code}.')

        broker_info = process_response(response_json[0])
        return Broker.create(**broker_info)

    @lru_cache(maxsize=300)
    @upsert_stock
    def get_stock_info(self, stock_code: str) -> Stock:
        params = {
            'limit': 0,
            'keyword': stock_code.lower(),
            'userDefaultExchangeType': 1,
            'selectedExchangeType': 1,
        }

        response = self._http_client.get(f'{BASE_HOST}{STOCK_ID}', params=params)
        response_json = response.json()

        logging.info(f'Received response from the api with status {response.status_code} '
                     f'for the stock code {stock_code}: {response_json}')

        if len(response_json) == 0:
            raise NoDataFoundException(f'No data found for stock code {stock_code}.')

        stock_info = process_response(response_json[0])
        return Stock.create(**stock_info)

    def _get_transactions(self, url: str, params: dict, from_date: date, to_date: date) -> List[Transaction]:
        date_format = '%Y/%m/%d'

        params = {
            'fromDate': from_date.strftime(date_format),
            'toDate': to_date.strftime(date_format),
            **params,
        }

        logging.info(f'Loading transactions with parameters: {params}...')
        response = self._http_client.post(url, params=params)
        transactions = []

        for raw_transaction in response.json():
            raw_transaction['Date'] = datetime.fromisoformat(raw_transaction['Date']).date()
            transaction = Transaction.create(**process_response(raw_transaction))
            transactions.append(transaction)

        logging.info(f'Loaded {len(transactions)} transactions for {params}.')
        return transactions

    def get_stock_transaction_by_stock_id_and_date(self, stock_id: int, from_date: date, to_date: date) -> List[
                                                                                                    Transaction]:
        return self._get_transactions(
            f'{BASE_HOST}{STOCK_TRANSACTION_BY_STOCK_ID}',
            {'stockId': stock_id},
            from_date,
            to_date
        )

    def get_stock_transaction_by_broker_id_and_date(self, broker_id: int, from_date: date, to_date: date) -> List[
                                                                                                    Transaction]:
        return self._get_transactions(
            f'{BASE_HOST}{STOCK_TRANSACTION_BY_BROKER_ID}',
            {'brokerId': broker_id},
            from_date,
            to_date
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Closing the http connection...")
        self._http_client.close()
