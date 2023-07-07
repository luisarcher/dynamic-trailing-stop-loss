import logging
import threading
import time
from dtsl.binance_exchange import BinanceExchange
from dtsl.models.signal import Signal
from dtsl.trade import Trade

logger=logging.getLogger(__name__)


class ExchangeMediator:

    def __init__(self, binance_exchange: BinanceExchange):
        self.binance_exchange = binance_exchange

        from typing import List
        self.trades: List[Trade] = []
        self.is_running = False
        self.import_trades()

    def import_trades(self):
        positions = self.binance_exchange.get_current_positions()
        for position in positions:
            symbol = position['symbol']
            position_side = position['positionSide']
            position_size = float(position['positionAmt'])
            if position_size != 0.0:
                print(position)
                trade = Trade(Signal(symbol, Trade.determine_position_side(position_side, position_size)), self.binance_exchange, True)
                trade.entry_price = float(position['entryPrice'])
                trade.mark_price  = float(position['markPrice'])
                self.add_existing_open_orders(trade)
                self.trades.append(trade)
        print(f'Imported trades: {self.trades}')

    def add_existing_open_orders(self, trade_obj: Trade):
        # We are looking for SELL orders if we are longing and BUY orders if we are shorting
        counter_side = Trade.get_buy_sell_position_side(Trade.get_counter_LS_side(trade_obj.side_LS))
        orders = self.binance_exchange.get_open_orders(trade_obj.symbol)
        logger.info('Seeking existing TP and SL orders...')
        #print(counter_side)
        #print(orders)

        # Check if a take profit limit order exists and store it
        tp_order = next((order for order in orders if order['type'] == 'LIMIT' and order['side'] == counter_side), None)
        if tp_order:
            logger.info(f'Found existing TP limit order for symbol: {trade_obj.symbol}')
            trade_obj.tp_order = tp_order
        else:
            logger.warning(f'Could not find any existing TP limit order for symbol: {trade_obj.symbol}')

        # Check if a STOP_MARKET order exists and store it
        stop_market_order = next((order for order in orders if order['type'] == 'STOP_MARKET'), None)
        if stop_market_order:
            logger.info(f'Found existing SL order for symbol: {trade_obj.symbol}')
            trade_obj.stop_loss_order = stop_market_order
        else:
            logger.warning(f'Could not find any existing SL order for symbol: {trade_obj.symbol}')

    def start(self):
        if not self.is_running:
            self.is_running = True
            threading.Thread(target=self._query_positions).start()

    def stop(self):
        self.is_running = False

    def enter_trade(self, signal: Signal) -> bool:
        symbol = signal.ticker
        if not self.is_symbol_exists(symbol):
            trade = Trade(signal, self.binance_exchange)
            self.trades.append(trade)
            return True
        return False
    
    def is_symbol_exists(self, symbol):
        for trade in self.trades:
            if trade.symbol == symbol:
                return True
        return False

    def _query_positions(self):
        while self.is_running:
            if len(self.trades) == 0:
                # Wait for a little longer, there's no trades ongoing
                time.sleep(8)
            positions = self.binance_exchange.get_current_positions()
            self.update_trades(positions)
            time.sleep(8)

    def update_trades(self, positions):
        trades_to_remove = []  # List to hold trades to be removed

        for trade in self.trades:
            symbol = trade.get_symbol()
            position = self.find_position(positions, symbol)
            if position:
                position_size = float(position['positionAmt'])
                leverage = int(position['leverage'])
                entry_price = float(position['entryPrice'])
                mark_price = float(position['markPrice'])
                unrealized_pnl = float(position['unRealizedProfit'])
                side = position['positionSide']

                trade.update_position(position_size, leverage, entry_price, mark_price, unrealized_pnl, side)

                # Check if position amount is zero and add trade to removal list
                if position_size == 0.0:
                    trades_to_remove.append(trade)
        
        # Remove trades from the trades list
        for trade in trades_to_remove:
            self.trades.remove(trade)

    @staticmethod
    def find_position(positions, symbol):
        for position in positions:
            if position['symbol'] == symbol:
                return position
        return None
