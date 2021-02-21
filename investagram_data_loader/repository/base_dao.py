from peewee import *
from typing import List
from abc import ABC, abstractmethod


class BaseDao(ABC):
    @abstractmethod
    def insert_stock(self, data: Model):
        pass

    @abstractmethod
    def insert_broker(self, data: Model):
        pass

    @abstractmethod
    def bulk_insert_transactions(self, data: List[Model]):
        pass
