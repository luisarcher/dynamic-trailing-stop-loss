from enum import Enum

class TradeSide(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
