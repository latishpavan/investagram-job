import keyring
import requests
from investagram_data_loader.constants.app import *
from investagram_data_loader.constants.user import *
from investagram_data_loader.constants.endpoints import *


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

    def get_stock_transaction_by_stock_id_and_date(self, stock_id: int, from_date: str, to_date: str):
        params = {
            'stockId': stock_id,
            'fromDate': from_date,
            'toDate': to_date
        }

        response = self._http_client.post(f'{BASE_HOST}{STOCK_TRANSACTION}', params=params)
        return response.json()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._http_client.close()
