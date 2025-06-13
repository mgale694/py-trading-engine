from engine import TradingEngine
from strategy.basic import BasicStrategy
import subprocess
import sys
import os
from servers.order_book import OrderBookServer

if __name__ == '__main__':
    # Initialise the trading engine
    # engine = TradingEngine()
    # print('Trading engine ready.')

    # Initialise the basic strategy
    strategy = BasicStrategy()
    print('Basic strategy initialised.')

    server = OrderBookServer(strategy=strategy)  # Pass the strategy instance
    server.run()

    # You can add more logic here if needed
