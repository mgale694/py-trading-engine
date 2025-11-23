"""
Main entry point for the trading system.
Provides CLI interface to start servers and clients.
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from shared.logging import setup_logger
from servers.tes import TradingEngineServer
from servers.obs import OrderBookServer
from clients import TraderClient

# Setup logging
logger = setup_logger(name='main', log_file='trading_system.log')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Trading Engine System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -s OBS              Start Order Book Server
  python main.py -s TES              Start Trading Engine Server
  python main.py -c trader           Start Trader Client
  
  python main.py --frontend trader   Start Trader Portal (Streamlit)
  python main.py --frontend analytics Start Analytics Dashboard
        """
    )
    
    parser.add_argument(
        "-s", "--server",
        choices=["TES", "OBS"],
        help="Server to start (TES=Trading Engine Server, OBS=Order Book Server)"
    )
    
    parser.add_argument(
        "-c", "--client",
        choices=["trader"],
        help="Client to start"
    )
    
    parser.add_argument(
        "--frontend",
        choices=["trader", "analytics"],
        help="Frontend application to start"
    )
    
    args = parser.parse_args()
    
    # Validate that only one option is provided
    options_provided = sum([
        args.server is not None,
        args.client is not None,
        args.frontend is not None
    ])
    
    if options_provided == 0:
        parser.print_help()
        return
    
    if options_provided > 1:
        logger.error("Please provide only one option: --server, --client, or --frontend")
        parser.print_help()
        return
    
    # Start the appropriate component
    if args.server:
        if args.server == "TES":
            logger.info("Starting Trading Engine Server (TES)")
            server = TradingEngineServer()
            server.run()
        elif args.server == "OBS":
            logger.info("Starting Order Book Server (OBS)")
            server = OrderBookServer()
            server.run()
    
    elif args.client:
        if args.client == "trader":
            logger.info("Starting Trader Client")
            client = TraderClient()
            client.run()
    
    elif args.frontend:
        import subprocess
        if args.frontend == "trader":
            logger.info("Starting Trader Portal")
            subprocess.run([
                "streamlit", "run",
                "src/frontend/trader-portal/app.py"
            ])
        elif args.frontend == "analytics":
            logger.info("Starting Analytics Dashboard")
            subprocess.run([
                "streamlit", "run",
                "src/frontend/analytics/app.py"
            ])


if __name__ == "__main__":
    main()
