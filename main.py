"""
Main entry point for the trading system.
Provides CLI interface to start servers and clients.
"""
import sys
import os
from pathlib import Path
from typing import Optional
import subprocess

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from shared.logging import setup_logger
from shared.config import Config
from servers.tes import TradingEngineServer
from servers.obs import OrderBookServer
from clients import TraderClient

# Setup CLI app and console
app = typer.Typer(
    name="Trading Engine",
    help="🚀 Python Trading Engine System - Microservices trading platform",
    add_completion=False,
    rich_markup_mode="rich"
)
console = Console()

# Setup logging
logger = setup_logger(name='main', log_file='trading_system.log')

# Get environment (default to dev)
ENV = os.getenv('ENV', 'dev')


@app.command()
def server(
    name: str = typer.Argument(
        ...,
        help="Server to start: [bold cyan]TES[/bold cyan] (Trading Engine Server) or [bold cyan]OBS[/bold cyan] (Order Book Server)"
    ),
    env: str = typer.Option(
        ENV,
        help="Environment: dev or prod"
    )
):
    """
    🖥️  Start a trading server (TES or OBS).
    
    [bold cyan]TES[/bold cyan]: Trading Engine Server - manages clients and portfolios
    [bold cyan]OBS[/bold cyan]: Order Book Server - handles order matching
    """
    config = Config(env=env)
    
    name = name.upper()
    if name not in ["TES", "OBS"]:
        console.print(f"[bold red]Error:[/bold red] Server must be TES or OBS, got '{name}'")
        raise typer.Exit(1)
    
    if name == "TES":
        console.print(Panel(
            "[bold cyan]Trading Engine Server (TES)[/bold cyan]\n"
            "Client management • Portfolio tracking • Order routing",
            title="🚀 Starting Server",
            border_style="cyan"
        ))
        logger.info("Starting Trading Engine Server (TES)")
        server = TradingEngineServer()
        server.run()
    
    elif name == "OBS":
        console.print(Panel(
            "[bold green]Order Book Server (OBS)[/bold green]\n"
            "Order matching • Strategy execution • Trade recording",
            title="🚀 Starting Server",
            border_style="green"
        ))
        logger.info("Starting Order Book Server (OBS)")
        server = OrderBookServer()
        server.run()


@app.command()
def client(
    name: str = typer.Argument(
        "trader",
        help="Client to start: [bold yellow]trader[/bold yellow]"
    ),
    env: str = typer.Option(
        ENV,
        help="Environment: dev or prod"
    )
):
    """
    👤 Start a trading client.
    """
    config = Config(env=env)
    
    if name == "trader":
        console.print(Panel(
            "[bold yellow]Trader Client[/bold yellow]\n"
            "Interactive terminal client for placing orders",
            title="👤 Starting Client",
            border_style="yellow"
        ))
        logger.info("Starting Trader Client")
        client = TraderClient()
        client.run()
    else:
        console.print(f"[bold red]Error:[/bold red] Unknown client '{name}'")
        raise typer.Exit(1)


@app.command()
def frontend(
    name: str = typer.Argument(
        ...,
        help="Frontend to start: [bold magenta]trader[/bold magenta] or [bold magenta]analytics[/bold magenta]"
    ),
    env: str = typer.Option(
        ENV,
        help="Environment: dev or prod"
    )
):
    """
    🎨 Start a frontend application (Streamlit).
    
    [bold magenta]trader[/bold magenta]: Trader Portal - Order entry and portfolio view
    [bold magenta]analytics[/bold magenta]: Analytics Dashboard - Performance metrics and charts
    """
    config = Config(env=env)
    
    if name == "trader":
        console.print(Panel(
            "[bold magenta]Trader Portal[/bold magenta]\n"
            "Web interface for order entry and portfolio management\n"
            "URL: [link]http://localhost:8501[/link]",
            title="🎨 Starting Frontend",
            border_style="magenta"
        ))
        logger.info("Starting Trader Portal")
        subprocess.run(["streamlit", "run", "src/frontend/trader-portal/app.py"])
    
    elif name == "analytics":
        console.print(Panel(
            "[bold magenta]Analytics Dashboard[/bold magenta]\n"
            "Internal analytics and performance metrics\n"
            "URL: [link]http://localhost:8502[/link]",
            title="🎨 Starting Frontend",
            border_style="magenta"
        ))
        logger.info("Starting Analytics Dashboard")
        subprocess.run(["streamlit", "run", "src/frontend/analytics/app.py"])
    
    else:
        console.print(f"[bold red]Error:[/bold red] Unknown frontend '{name}'")
        raise typer.Exit(1)


@app.command()
def init_mock_data(
    env: str = typer.Option(
        ENV,
        help="Environment (must be dev)"
    )
):
    """
    📊 Initialize database with mock data (dev only).
    
    Creates test users, orders, trades, and instruments for development.
    """
    if env != 'dev':
        console.print("[bold red]Error:[/bold red] Mock data initialization is only available in [bold cyan]dev[/bold cyan] environment")
        raise typer.Exit(1)
    
    config = Config(env=env)
    
    console.print(Panel(
        "[bold cyan]Mock Data Generator[/bold cyan]\n"
        "• 20 test users with balances\n"
        "• 100 historical orders\n"
        "• 50 executed trades\n"
        "• 10 trading instruments\n"
        "• Portfolio positions and analytics",
        title="📊 Initializing Mock Data",
        border_style="cyan"
    ))
    
    logger.info("Initializing mock data...")
    
    from shared.mock_data import initialize_mock_data
    from database.transactional import TransactionalDB
    from database.analytics import AnalyticsDB
    from database.utilities import ModelParamsDB
    
    with console.status("[bold cyan]Loading mock data...", spinner="dots"):
        trans_db = TransactionalDB()
        analytics_db = AnalyticsDB()
        utilities_db = ModelParamsDB()
        
        initialize_mock_data(trans_db, analytics_db, utilities_db)
        
        trans_db.close()
        analytics_db.close()
        utilities_db.close()
    
    console.print("\n[bold green]✅ Mock data initialization complete![/bold green]")
    logger.info("✅ Mock data initialization complete")


@app.command()
def simulated_traders(
    count: int = typer.Argument(
        ...,
        help="Number of simulated traders to start"
    ),
    env: str = typer.Option(
        ENV,
        help="Environment (must be dev)"
    )
):
    """
    🤖 Start simulated traders (dev only).
    
    Automated bots that place random orders for testing the system.
    """
    if env != 'dev':
        console.print("[bold red]Error:[/bold red] Simulated traders are only available in [bold cyan]dev[/bold cyan] environment")
        raise typer.Exit(1)
    
    config = Config(env=env)
    dev_config = config.get_dev_config()
    trade_freq = dev_config.get('simulated_traders', {}).get('trade_frequency', 5.0)
    
    console.print(Panel(
        f"[bold green]Simulated Traders[/bold green]\n"
        f"• Count: {count} traders\n"
        f"• Trade Frequency: ~{trade_freq}s between trades\n"
        f"• Symbols: AAPL, GOOGL, MSFT, TSLA, AMZN\n"
        f"• Press [bold red]Ctrl+C[/bold red] to stop",
        title="🤖 Starting Simulated Traders",
        border_style="green"
    ))
    
    logger.info(f"Starting {count} simulated traders...")
    
    from clients.simulated_traders import run_simulated_traders
    
    run_simulated_traders(count=count, trade_frequency=trade_freq)



if __name__ == "__main__":
    app()
