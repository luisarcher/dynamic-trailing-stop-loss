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
            trading_pair = ""
            trade_type = ""
            trading_pair_regex = re.compile(r"[A-Z]{1,5}\s*\/?\s*USDT")
            trading_pair_match = trading_pair_regex.search(message)
            if trading_pair_match:
                trading_pair = trading_pair_match.group().replace(" ", "")

            # Detects trade results and avoid entering a trade when results are published
            if "ACHIEVED" in message \
                or "Achieved" in message \
                or "achieved" in message \
                or "ATINGIDO" in message:
                return None

            # Parse trade type
            if "LONG" in message \
                or "Long" in message \
                or "long" in message \
                or "Compra" in message:
                trade_type = "LONG"
            elif "SHORT" in message \
                or "Short" in message \
                or "short" in message \
                or "Venda" in message:
                trade_type = "SHORT"

            if trading_pair == "" \
                or trading_pair is None\
                or trade_type == "":
                return None
            signal = Signal(trading_pair, trade_type)
            return signal
        except Exception as e:
            logger.error(f'[ERROR] Error decoding message: ')
            logger.exception(e)
