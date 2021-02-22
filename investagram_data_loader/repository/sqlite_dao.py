from peewee import *
from typing import List
from dynaconf import settings
from investagram_data_loader.logger import logging
from investagram_data_loader.repository.base_dao import BaseDao


class Stock(Model):
    stock_id = IntegerField(primary_key=True)
    stock_code = CharField(max_length=20, index=True)
    stock_name = CharField()
    exchange_type = CharField()
    exchange_string = CharField()
    stock_code_and_exchange = CharField()
    sector_string = CharField()
    subsector_string = CharField()
    is_active = BooleanField()
    stock_type = IntegerField()
    stock_category = CharField()
    stock_category_id = IntegerField()


class Broker(Model):
    stock_broker_id = IntegerField(primary_key=True, db_column='broker_id')
    exchange_type = IntegerField()
    broker_name = CharField()
    broker_classification = IntegerField()
    broker_status = IntegerField()
    broker_code = CharField(index=True)
    broker_number = IntegerField()
    broker_status_name = CharField()
    broker_classification_name = CharField()


class Transaction(Model):
    stock_id = ForeignKeyField(Stock, db_column='stock_id')
    broker_id = ForeignKeyField(Broker, to_field='stock_broker_id', db_column='broker_id')
    stock_code = CharField()
    stock_name = CharField()
    broker_code = CharField()
    date = DateField()
    buy_volume = IntegerField()
    buy_value = FloatField()
    buy_ave_price = FloatField()
    buy_market_val_percent = FloatField()
    buy_trade_count = IntegerField()
    sell_volume = IntegerField()
    sell_value = FloatField()
    sell_ave_price = FloatField()
    sell_market_val_percent = FloatField()
    sell_trade_count = IntegerField()
    net_volume = IntegerField()
    net_value = FloatField()
    total_volume = IntegerField()
    total_value = IntegerField()


# singleton instance
class SqliteDao(BaseDao):
    models = [Stock, Broker, Transaction]
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)

        return cls._instance

    def __init__(self):
        self._database = SqliteDatabase(settings.DATABASE_FILE)
        self._set_db_on_models()
        self._setup()

    def _setup(self):
        self._database.connect(reuse_if_open=True)
        self._database.create_tables(SqliteDao.models)

    def _set_db_on_models(self):
        for model in SqliteDao.models:
            model._meta.database = self._database

    def insert_stock(self, data: Stock) -> int:
        num_inserted = data.save()
        logging.info(f'Inserted {num_inserted} records into stock table.')
        return num_inserted

    def insert_broker(self, data: Broker) -> int:
        num_inserted = data.save()
        logging.info(f'Inserted {num_inserted} records into broker table.')
        return num_inserted

    def bulk_insert_transactions(self, transactions: List[Transaction]):
        with self._database.atomic():
            Transaction.bulk_create(transactions, batch_size=50)

        logging.info(f'Inserted {len(transactions)} transaction records in the database.')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._database.close()


def upsert_stock(stock_getter):
    dao = SqliteDao()

    def wrapper(_self, stock_code: str):
        try:
            logging.info(f"Retrieving {stock_code} stock data from database..")
            entry = Stock.get(Stock.stock_code == stock_code)
            return entry

        except DoesNotExist:
            logging.info(f'{stock_code} data not found in database, querying the api...')
            stock_info = stock_getter(_self, stock_code)
            dao.insert_stock(stock_info)
            return stock_info

    return wrapper


def upsert_broker(broker_getter):
    dao = SqliteDao()

    def wrapper(_self, broker_code: str):
        try:
            logging.info(f"Retrieving {broker_code} broker data from database..")
            entry = Broker.get(Broker.broker_code == broker_code)
            return entry

        except DoesNotExist:
            logging.info(f'{broker_code} data not found in database, querying the api...')
            broker_info = broker_getter(_self, broker_code)
            dao.insert_broker(broker_info)
            return broker_info

    return wrapper
