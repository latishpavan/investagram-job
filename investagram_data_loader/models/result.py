from dataclasses import dataclass


@dataclass(frozen=True)
class StockBrokerResult:
    StockId: int
    BrokerId: int
    StockCode: str
    StockName: str
    BrokerCode: str
    Date: str
    BuyVolume: int
    BuyValue: float
    BuyAvePrice: float
    BuyMarketValPercent: float
    BuyTradeCount: int
    SellVolume: int
    SellValue: float
    SellAvePrice: float
    SellMarketValPercent: float
    SellTradeCount: int
    NetVolume: int
    NetValue: float
    TotalVolume: int
    TotalValue: int
