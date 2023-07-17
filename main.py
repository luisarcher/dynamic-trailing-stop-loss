import multiprocessing
import threading
from telethon import TelegramClient, events
from dtsl.binance_exchange import BinanceExchange


from dtsl.config import Config
from dtsl.decoder import Decoder
from dtsl.exchange_mediator import ExchangeMediator
from dtsl.models.signal import Signal



# Initializing...
config = Config()
decoder = Decoder()
exchange_mediator = ExchangeMediator(BinanceExchange())
exchange_mediator.start()

# Create a lock to synchronize access to the queue
#queue_lock = threading.Lock()

# Initialize the telegram message queue
#message_queue = multiprocessing.Queue()

# Initialize the Telegram client
client = TelegramClient(
    'session_read', 
    config.get_config_value("telegram_api").get("api_id"), 
    config.get_config_value("telegram_api").get("api_hash")
)

# Extract user IDs from YAML data
user_ids = config.get_config_value("telegram_api").get("user_ids")
channel_ids = config.get_config_value("telegram_api").get("channel_ids")
#print(user_ids)

# chats=("GroupName", "Group2")

# Register the event handler
@client.on(events.NewMessage())
async def my_event_handler(event):
    # Put the event in the message queue
    #with queue_lock:
        #message_queue.put(event)
    #sender = await event.get_sender()
    #print(sender)
    #print(sender.username)

    #if (event.message.peer_id.user_id and event.message.peer_id.user_id in user_ids):

    if (
        (hasattr(event.message.peer_id, 'user_id') and event.message.peer_id.user_id in user_ids)
        or (hasattr(event.message.peer_id, 'channel_id') and event.message.peer_id.channel_id in channel_ids)
    ):
        # use or for channels
        # or (event.message.peer_id.channel_id and event.message.peer_id.channel_id in channel_ids):
        print(event)
        signal: Signal = decoder.decode(event.message.message)
        if signal is None:
            return
        exchange_mediator.enter_trade(signal)


# Start the Telegram client and run until disconnected
client.start()
client.run_until_disconnected()
