from typing import List
from pathlib import Path
from dynaconf import settings
from definitions import ROOT_DIR
from investagram_data_loader.logger import logging


def _read_file(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f'File not found at path {path}')

    return path.read_text().split('\n')


def get_stocks(size: int = -1) -> List[str]:
    file_path = Path(ROOT_DIR) / settings.STOCKS_FILE
    stocks = _read_file(file_path)

    logging.info(f'Read {len(stocks)} stocks from file at path {file_path}')

    size = size if size != -1 else len(stocks)
    return stocks[:size]


def get_brokers(size: int = -1) -> List[str]:
    file_path = Path(ROOT_DIR) / settings.BROKERS_FILE
    brokers = _read_file(file_path)

    logging.info(f'Read {len(brokers)} brokers from file at path {file_path}')

    size = size if size != -1 else len(brokers)
    return brokers[:size]
