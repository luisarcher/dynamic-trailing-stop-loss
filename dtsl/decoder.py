import logging
import re
from .models.signal import Signal

logger=logging.getLogger(__name__)


class Decoder:

    def __init__(self) -> None:
        pass

    @staticmethod
    def decode(message: str) -> Signal:
        try:
            # Parse trading pair
            trading_pair_regex = re.compile(r"[A-Za-z]{1,5}\s*/\s*USDT")
            trading_pair_match = trading_pair_regex.search(message)
            if trading_pair_match:
                trading_pair = trading_pair_match.group().replace(" ", "")

            # Parse trade type
            if "LONG" in message \
                or "Long" in message \
                or "long" in message:
                trade_type = "LONG"
            elif "SHORT" in message \
                or "Short" in message \
                or "short" in message:
                trade_type = "SHORT"

            signal = Signal(trading_pair, trade_type)
            return signal
        except Exception as e:
            logger.error(f'[ERROR] Error decoding message: ')
            logger.exception(e)
