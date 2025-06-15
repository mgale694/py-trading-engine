from config.logger import setup_logger
import logging
from clients.trader import TraderClient
from servers.trading_engine import TradingEngineServer
from strategy.basic import BasicStrategy
from servers.order_book import OrderBookServer
import argparse

setup_logger()
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Trading Engine Entry Point")
    parser.add_argument(
        "-s", "--server", choices=["TES", "OBS"], help="Server to start (TES or OBS)"
    )
    parser.add_argument(
        "-c",
        "--client",
        choices=["trader", "algotrader"],
        help="Client to start (trader or algotrader)",
    )
    args = parser.parse_args()

    if args.server:
        if args.server == "TES":
            logger.info("Starting Trading Engine Server (TES)")
            engine = TradingEngineServer()
            engine.run()
        elif args.server == "OBS":
            logger.info("Starting Order Book Server (OBS)")
            # You can add strategy selection logic here if needed
            server = OrderBookServer()
            server.run()
    elif args.client:
        if args.client == "trader":
            logger.info("Starting Trader Client")
            client = TraderClient()
            client.run()
    #     elif args.client == 'algotrader':
    #         logger.info("Starting AlgoTrader Client")
    #         from clients.test_client import AlgoTraderClient
    #         client = AlgoTraderClient()
    #         client.run()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
