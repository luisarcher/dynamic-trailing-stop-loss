import re
from .models.signal import Signal


class Decoder:

    def __init__(self) -> None:
        pass

    @staticmethod
    def decode(message: str) -> Signal:
        # Parse trading pair
        trading_pair_regex = re.compile(r"[A-Za-z]{1,5}\s*/\s*USDT")
        trading_pair_match = trading_pair_regex.search(message)
        if trading_pair_match:
            trading_pair = trading_pair_match.group().replace(" ", "")

        # Parse trade type
        if "LONG" in message:
            trade_type = "LONG"
        elif "SHORT" in message:
            trade_type = "SHORT"

        signal = Signal(trading_pair, trade_type)
        return signal
