from dataclasses import dataclass


@dataclass(frozen=True)
class Stock:
    StockId: int
    StockCode: str
    StockName: str
    ExchangeType: str
    ExchangeString: str
    StockCodeAndExchange: str
    SectorString: str
    SubsectorString: str
    IsActive: bool
    StockType: int
    DisplayPhotoUrl: str
    StockCategoryId: int
    StockCategory: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
