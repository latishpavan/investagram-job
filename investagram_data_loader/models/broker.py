from dataclasses import dataclass


@dataclass(frozen=True)
class Broker:
    StockBrokerId: int
    ExchangeType: int
    BrokerName: str
    BrokerClassification: int
    BrokerStatus: int
    BrokerCode: str
    BrokerNumber: int
    BrokerStatusName: str
    BrokerClassificationName: str
