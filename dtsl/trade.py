import logging
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
        
        # Position data from updates
        self.entry_price = 0.0
        self.mark_price = 0.0
        self.unrealized_pnl = 0.0
        self.max_mark_price = float('-inf')
        self.min_mark_price = float('inf')

        # Order ids
        self.entry_order = None
        self.tp_order = None
        self.stop_loss_order = None

        self.lot_size_filter = next(
            (filter for filter in self.exchange.exchange_info['symbols'] \
                 if filter['symbol'] == self.symbol), None)

        if not importing:
            self.init_trade()

    def init_trade(self):
        # Set trading leverage according to configuration
        self.set_leverage(self.leverage)
        # Place market order
        self.entry_order = self.execute_market_order()  # Place market order upon object creation

    def execute_market_order(self):
        # Obtain the necessary data for placing a market order
        balance = self.exchange.get_wallet_balance() * 0.25
        price = self.exchange.client.futures_symbol_ticker(symbol=self.symbol)['price']
        self.entry_size = self.calculate_entry_size(self.symbol, self.leverage, balance, price)
        # Place the market order
        executed_order = self.exchange.place_market_order(self.symbol, self.get_buy_sell_position_side(self.side_LS), self.entry_size)
        return executed_order
        
    def place_tp_limit_order(self):
        # Place TP limit order
        tp_order_price = self.entry_price * (1 + 0.05)  # Calculate TP order price with 5% increase
        tp_order_price = Trade.round_to_tick_size(tp_order_price, self.lot_size_filter)  # Adjust price based on lot size filter
        logging.info(f'Placing TP: Current position side: {self.side_LS}')
        self.tp_order = self.exchange.place_limit_tp_order(
            self.symbol,
            self.get_buy_sell_position_side(self.get_counter_LS_side(self.side_LS)),
            self.position_size,
            tp_order_price
        )

    def update_stop_loss_order(self):
        # Place SL order
        sl_order_price = self.entry_price * (1 - 0.025)  # Calculate SL order price with 2.5% margin
        sl_order_price = Trade.round_to_tick_size(sl_order_price, self.lot_size_filter)  # Adjust price based on lot size filter
        logging.info(f'Placing SL: Current position side: {self.side_LS}')
        self.stop_loss_order = self.exchange.place_stop_loss_order(
            self.symbol,
            self.get_buy_sell_position_side(self.get_counter_LS_side(self.side_LS)),
            self.position_size,
            sl_order_price
        )

    def __repr__(self) -> str:
        return f'{self.symbol}: qty: {self.position_size}'
    
    def get_buy_sell_position_side(self, long_short_side: str):
        # Parse trade type
        if 'LONG' in long_short_side.upper():
            return 'BUY'
        elif 'SHORT' in long_short_side.upper():
            return 'SELL'
        
    def get_counter_LS_side(self, side_ls: str):
        if 'LONG' in side_ls.upper():
            return 'SHORT'
        elif 'SHORT' in side_ls.upper():
            return 'LONG'

    def update_position(self, position_size, leverage, entry_price, mark_price, unrealized_pnl, position_side):
        self.position_size = position_size
        self.leverage = leverage
        self.entry_price = float(entry_price)
        self.mark_price = mark_price
        self.unrealized_pnl = unrealized_pnl
        self.side_LS = Trade.determine_position_side(position_side, position_size)
        self.update_max_min_mark_price(mark_price)

        if self.tp_order is None:
            self.place_tp_limit_order()

    def update_max_min_mark_price(self, mark_price):
        if mark_price > self.max_mark_price:
            self.max_mark_price = mark_price
        if mark_price < self.min_mark_price:
            self.min_mark_price = mark_price

    def get_symbol(self):
        return self.symbol
    
    def calculate_entry_size(self, pair: str, leverage: int, balance: float, price: float):
        
        non_rounded_entry_size = (
            float(balance) / float(price)
            * float(leverage) * float(0.1)
            * (1 - (0.0004 * 2))
        )

        # properly round according to tick size, dont use "3"

        qty_step = float(self.lot_size_filter['filters'][0]['tickSize'])
        precision = int(self.lot_size_filter['quantityPrecision'])
        rounded_entry_size = round(Trade.round_down(non_rounded_entry_size, qty_step), precision)
        print('Estimated entry size:', rounded_entry_size)
        return rounded_entry_size
    
    def set_leverage(self, leverage: int) -> dict:
        return self.exchange.client.futures_change_leverage(
            symbol=self.symbol,
            leverage=leverage
        )

    @staticmethod
    def round_down(non_rounded_entry_size: float, step: float) -> float:
        """
        This function rounds down a given number to the nearest multiple of a given step.
        :param non_rounded_entry_size: the number to be rounded down.
        :param step: the step to which the number should be rounded down.
        :return: the rounded down number.
        """
        return math.floor(non_rounded_entry_size / step) * step
    
    @staticmethod
    def round_to_tick_size(price: float, lot_size_filter: dict) -> float:
        tick_size = float(lot_size_filter['filters'][0]['tickSize'])
        return round(price / tick_size) * tick_size
    
    @staticmethod
    def determine_position_side(position_side: str, position_amount: float) -> str:
        if position_side == "BOTH":
            if position_amount > 0:
                position_direction = "LONG"
            elif position_amount < 0:
                position_direction = "SHORT"
            else:
                position_direction = "UNKNOWN"
        else:
            position_direction = position_side
        return position_direction