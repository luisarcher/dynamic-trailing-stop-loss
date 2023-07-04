

class Signal:
    def __init__(self, trading_pair: str, trade_type: str) -> None:
        self.trading_pair = trading_pair
        self.trade_type = trade_type
        self.ticker     = self.trading_pair.replace('/', '')
