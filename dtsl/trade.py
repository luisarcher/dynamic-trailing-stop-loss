import logging
import math

from dtsl.models.signal import Signal
from dtsl.config import Config
from dtsl.strategy import Strategy


logger=logging.getLogger(__name__)


class Trade:

    from dtsl.binance_exchange import BinanceExchange
    def __init__(self, signal: Signal, exchange: BinanceExchange, importing: bool = False):

        self.config = Config()
        
        self.exchange = exchange
        self.symbol = signal.ticker
        self.side_LS = signal.trade_type
        self.lot_size_filter = next(
            (filter for filter in self.exchange.exchange_info['symbols'] \
                 if filter['symbol'] == self.symbol), None)
        
        self.strategy = Strategy(self.lot_size_filter)

        self.position_size = 0.0
        self.leverage = int(self.config.get_config_value("binance_api").get("leverage"))  # Retrieve leverage from config
        
        # Position data from updates
        self.entry_price = 0.0
        self.mark_price = 0.0

        # Order ids
        self.entry_order = None
        self.tp_order = None
        self.stop_loss_order = None

        if not importing:
            self.init_trade()

    def init_trade(self):
        # Set trading leverage according to configuration
        self.set_leverage(self.leverage)
        # Place market order
        self.entry_order = self.execute_market_order()  # Place market order upon object creation

    def execute_market_order(self):
        logger.info(f'[{self.symbol}] Entering trade...')
        # Obtain the necessary data for placing a market order
        balance = self.exchange.get_wallet_balance() * 0.25
        price = self.exchange.client.futures_symbol_ticker(symbol=self.symbol)['price']
        self.entry_size = self.calculate_entry_size(self.symbol, self.leverage, balance, price)

        # Also update strategy params
        self.strategy.max_price = float(price)

        # Place the market order
        logger.info(f'[{self.symbol}] Market order: price: {price}, side: {self.side_LS}')
        executed_order = self.exchange.place_market_order(self.symbol, Trade.get_buy_sell_position_side(self.side_LS), self.entry_size)
        return executed_order
        
    def place_tp_limit_order(self):
        # Place TP limit order
        side = Trade.get_buy_sell_position_side(Trade.get_counter_LS_side(self.side_LS))
        price = self.strategy.get_tp_price(side, self.entry_price)
        logger.info(f'[{self.symbol}] TP order at: price: {price}')
        self.tp_order = self.exchange.place_limit_tp_order(
            self.symbol,
            side,
            self.position_size,
            price
        )

    def update_stop_loss_order(self):

        try:
            side = Trade.get_buy_sell_position_side(Trade.get_counter_LS_side(self.side_LS))
            if self.stop_loss_order is None:
                # Get initial SL price
                sl_price = self.strategy.get_sl_price(side, self.entry_price)
                logger.info(f'[{self.symbol}] Placing initial SL order at: price: {sl_price}')
            else:
                sl_price = self.strategy.update_sl_price(side, self.entry_price, self.mark_price)
                if sl_price == 0.0:
                    # SL order does not need to be updated
                    return None
                else:
                    #input('DEBUG: about to cancel SL order, continue?')
                    logger.info(f'[{self.symbol}] Cancelling existing SL order...')
                    self.exchange.cancel_order(self.symbol, self.stop_loss_order['orderId'])
                    logger.info(f'[{self.symbol}] Updating SL order to: price: {sl_price}')

            #input('DEBUG: about to place SL order, continue?')
            # Place SL order
            self.stop_loss_order = self.exchange.place_stop_loss_order(
                self.symbol,
                side,
                self.position_size,
                sl_price
            )
        except Exception as e:
            logger.error(f'[ERROR] Exception updating stop loss')
            logger.exception(e)
        

    def __repr__(self) -> str:
        return f'{self.symbol}'
    
    @staticmethod
    def get_buy_sell_position_side(long_short_side: str):
        # Parse trade type
        if 'LONG' in long_short_side.upper():
            return 'BUY'
        elif 'SHORT' in long_short_side.upper():
            return 'SELL'
    
    @staticmethod
    def get_counter_LS_side(side_ls: str):
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

        if self.tp_order is None:
            self.place_tp_limit_order()

        self.update_stop_loss_order()

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