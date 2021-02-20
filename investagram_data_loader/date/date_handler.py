from datetime import date, timedelta
from investagram_data_loader.constants.mode import DateMode


def generate_date_range(mode: DateMode, from_date: date, to_date: date):
    range_from_date, range_to_date = from_date, from_date + timedelta(days=mode.value)
    yield range_from_date, range_to_date

    while range_to_date <= to_date:
        range_from_date = range_to_date + timedelta(days=1)
        range_to_date = range_from_date + timedelta(days=mode.value)
        yield range_from_date, range_to_date
