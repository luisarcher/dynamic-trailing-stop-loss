# dynamic-trailing-stop-loss
An experiment on trading crypto using self adjusted trailing stop loss method.

## Requirements

The following Python packages are required and can be installed using pip install -r requirements.txt:

- Flask
- PyBit
- telethon

## Configuration

The bot's configuration is defined in the config.yml file. An example file with the required fields is provided in config.example.yml. The configuration file contains the user data for the Binance API, such as the API key and secret, as well as the setup for strategy parameters, including the wallet percentage, long and short leverage, among other parameters.
One of the major purposes when writing this bot was the ability to receive telegram signals. The Telegram API as well as the configuration of the channels/groups that the bot should be listening to are configured on config.yml as well.

## Usage

To start the application, run **python main.py** in the terminal. The application will start to listen for the upcoming telegram messages. On the first functional tests, I have configured a second telegram account, white-listed the userId that will be sending the messages and proceed from there whitelisted more and more channels that were providing trading signals for the bot to digest.

## Architecture:

The BinanceExchange class provides the methods to buy, sell, check positions, etc.
Once a trading signal is received, it is passed to a decoder. If the decoder was able to interpret the trade signal, a trade object is created and the BinanceExchange is used to open a trade.
All the trades are managed by ExchangeMediator. The mediator will query Binance from time to time to check on trades. The trade information from the exchange is broadcasted internally. Every trade has a strategy and reacts according to the new values.

## Strategy

To write

![Screenshot](docs/stop_loss.png.png)
