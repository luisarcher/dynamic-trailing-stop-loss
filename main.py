from dtsl.config import Config
from dtsl.decoder import Decoder
from dtsl.models.signal import Signal

if __name__ == '__main__':
    config_filename = 'config.yml'  # Provide your custom filename or leave it as None for the default filename
    config = Config()
    config.print_config()
    value = config.get_config_value('telegram_api.api_id')
    print(value)

    message = "⚡️⚡️ #BTC/USDT ⚡️⚡️\n\nClient: Binance Futures\nTrade Type: Regular (SHORT)\nLeverage: Isolated (10.0X)\n\nEntry Zone:\n37350 - 37000\n\nTake-Profit Targets:\n1) 36670 - 20%\n2) 36220 - 20%\n3) 35800 - 20%\n4) 35400 - 20%\n5) 35000 - 20%\n\nStop Targets:\n1) 39100 - 100.0%"
    decoder = Decoder()
    signal: Signal = decoder.decode(message)
    print(f"pair: {signal.trading_pair}, side: {signal.trade_type}")
