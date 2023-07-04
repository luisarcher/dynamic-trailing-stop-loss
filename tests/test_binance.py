# -*- coding: utf-8 -*-

from dtsl.config import Config
from dtsl.binance_exchange import BinanceExchange

import unittest


class BinanceTestSuite(unittest.TestCase):
    """Config test cases."""

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.binance_exchange = BinanceExchange()

    def test_server_time(self):
        print(self.binance_exchange.client.get_server_time())

    def test_balance(self):
        print(f'Available Balance: {self.binance_exchange.get_wallet_balance()}')

    def test_get_current_positions(self):
        positions = self.binance_exchange.get_current_positions()
        #print(f'Current positions: {positions}')

        for position in positions:
            symbol = position['symbol']
            position_size = float(position['positionAmt'])
            leverage = int(position['leverage'])
            entry_price = float(position['entryPrice'])
            mark_price = float(position['markPrice'])
            unrealized_pnl = float(position['unRealizedProfit'])
            
            if position_size != 0:
                print(f"Symbol: {symbol}")
                print(f"Position Size: {position_size}")
                print(f"Leverage: {leverage}")
                print(f"Entry Price: {entry_price}")
                print(f"Mark Price: {mark_price}")
                print(f"Unrealized PNL: {unrealized_pnl}\n")


if __name__ == '__main__':
    unittest.main()
