# -*- coding: utf-8 -*-

from dtsl.decoder import Decoder

import unittest

import os
import sys

from dtsl.models.signal import Signal
project_root_path = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
)
sys.path.insert(1, os.path.join(project_root_path, 'tests'))


class DecoderTestSuite(unittest.TestCase):
    """Decoder test cases."""

    def test_decoder(self):
        # Read the signal message from the fixture file
        with open(project_root_path + '/tests/fixtures/signal1.txt', 'r', encoding='utf-8') as file:
            signal_message = file.read()

        # Create an instance of the Decoder class
        decoder = Decoder()

        # Call the decode() method with the signal message
        signal: Signal = decoder.decode(signal_message)

        # Perform your assertions based on the expected results
        self.assertEqual(signal.trading_pair, 'BTC/USDT')
        self.assertEqual(signal.ticker, 'BTCUSDT')
        self.assertEqual(signal.trade_type, 'SHORT')

    def test_scalping_300(self):
        # Read the signal message from the fixture file
        with open(project_root_path + '/tests/fixtures/scalping_300.txt', 'r', encoding='utf-8') as file:
            signal_message = file.read()

        # Create an instance of the Decoder class
        decoder = Decoder()

        # Call the decode() method with the signal message
        signal: Signal = decoder.decode(signal_message)

        # Perform your assertions based on the expected results
        self.assertEqual(signal.trading_pair, 'EGLDUSDT')
        self.assertEqual(signal.ticker, 'EGLDUSDT')
        self.assertEqual(signal.trade_type, 'LONG')


if __name__ == '__main__':
    unittest.main()
