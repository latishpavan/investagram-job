from enum import Enum


class DateMode(Enum):
    DAILY = 'B'
    WEEKLY = 'W'
    MONTHLY = 'BM'
    YEARLY = 'BY'
