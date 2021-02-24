import pandas as pd
from datetime import date
from investagram_data_loader.constants.mode import DateMode


def generate_date_range(mode: DateMode, from_date: date, to_date: date):
    for curr_date in pd.bdate_range(start=from_date, end=to_date, freq=mode.value):
        yield curr_date.date(), curr_date.date()
