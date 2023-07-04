import math

from dtsl.models.signal import Signal
from dtsl.config import Config


class Trade:

    from dtsl.binance_exchange import BinanceExchange
    def __init__(self, signal: Signal, exchange: BinanceExchange, importing: bool = False):

        self.config = Config()
        
        self.exchange = exchange
        self.symbol = signal.ticker
        self.side_LS = signal.trade_type
        self.position_size = 0.0
        self.leverage = int(self.config.get_config_value("binance_api").get("leverage"))  # Retrieve leverage from config
        self.entry_price = 0.0
        self.mark_price = 0.0
        self.unrealized_pnl = 0.0
        self.max_mark_price = float('-inf')
        self.min_mark_price = float('inf')

        if not importing:
            self.entry_order = self.execute_market_order()  # Place market order upon object creation

    def __repr__(self) -> str:
        return f'{self.symbol}: qty: {self.position_size}'
    
    def get_buy_sell_position_side(self, long_short_side: str):
        # Parse trade type
        if 'LONG' in long_short_side.upper():
            return 'BUY'
        elif 'SHORT' in long_short_side.upper():
            return 'SELL'

    def execute_market_order(self):
        # Obtain the necessary data for placing a market order
        balance = self.exchange.get_wallet_balance() * 0.25
        price = self.exchange.client.futures_symbol_ticker(symbol=self.symbol)['price']
        entry_size = self.calculate_entry_size(self.symbol, self.leverage, balance, price)
        
        # Place the market order
        executed_order = self.exchange.place_market_order(self.symbol, self.get_buy_sell_position_side(self.side_LS), entry_size)
        return executed_order

    def update_position(self, position_size, leverage, entry_price, mark_price, unrealized_pnl):
        self.position_size = position_size
        self.leverage = leverage
        self.entry_price = entry_price
        self.mark_price = mark_price
        self.unrealized_pnl = unrealized_pnl
        self.update_max_min_mark_price(mark_price)

    def update_max_min_mark_price(self, mark_price):
        if mark_price > self.max_mark_price:
            self.max_mark_price = mark_price
        if mark_price < self.min_mark_price:
            self.min_mark_price = mark_price

    def get_symbol(self):
        return self.symbol
    
    def calculate_entry_size(self, pair: str, leverage: int, balance: float, price: float):
        lot_size_filter = next(
            (filter for filter in self.exchange.exchange_info['symbols'] \
                 if filter['symbol'] == pair), None)

        #if lot_size_filter:
            #print(f"Symbol: {pair}")
            #print(f"Lot Size Filter: {lot_size_filter}")
        #else:
            #print(f"Lot Size Filter not found for {pair}")

        non_rounded_entry_size = (
            float(balance) / float(price)
            * float(leverage) * float(0.1)
            * (1 - (0.0004 * 2))
        )

        # properly round according to tick size, dont use "3"

        qty_step = float(lot_size_filter['filters'][0]['tickSize'])
        precision = int(lot_size_filter['quantityPrecision'])
        rounded_entry_size = round(Trade.round_down(non_rounded_entry_size, qty_step), precision)
        print('Estimated entry size:', rounded_entry_size)
        return rounded_entry_size

    @staticmethod
    def round_down(non_rounded_entry_size: float, step: float) -> float:
        """
        This function rounds down a given number to the nearest multiple of a given step.
        :param non_rounded_entry_size: the number to be rounded down.
        :param step: the step to which the number should be rounded down.
        :return: the rounded down number.
        """
        return math.floor(non_rounded_entry_size / step) * step