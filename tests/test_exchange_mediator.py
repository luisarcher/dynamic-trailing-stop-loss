# -*- coding: utf-8 -*-

import logging
from dtsl.binance_exchange import BinanceExchange
from dtsl.config import Config

import unittest

from dtsl.exchange_mediator import ExchangeMediator
from dtsl.models.signal import Signal


class ExchangeMediatorTestSuite(unittest.TestCase):
    """Config test cases."""

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.binance_exchange = BinanceExchange()
        self.exchange_mediator = ExchangeMediator(self.binance_exchange)
        self.exchange_mediator.start()

    def test_enter_trade(self):
        signal: Signal = Signal('CHZUSDT', 'LONG')
        trade = self.exchange_mediator.enter_trade(signal)
        assert trade is True

    #def test_import_trades(self):
    #    assert len(self.exchange_mediator.trades) > 0

    #def test_stop_loss_placement(self):
    #    signal: Signal = Signal('MATIC/USDT', 'LONG')
    #    trade = self.exchange_mediator.enter_trade(signal)


if __name__ == '__main__':
    unittest.main()
