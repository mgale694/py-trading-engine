"""
Simulated trader bots for development and testing.
Automatically generates trading activity for testing the order matching engine.
"""

import json
import logging
import random
import threading
import time
import uuid
from typing import Optional

import pika
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

logger = logging.getLogger(__name__)
console = Console()

RABBITMQ_HOST = "localhost"


class SimulatedTrader:
    """A simulated trader that automatically places orders."""

    # Development symbols (limited set)
    DEV_SYMBOLS = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

    # Price ranges for each symbol (min, max)
    PRICE_RANGES = {
        "AAPL": (150.0, 200.0),
        "GOOGL": (130.0, 180.0),
        "MSFT": (350.0, 450.0),
        "TSLA": (200.0, 300.0),
        "AMZN": (140.0, 180.0),
    }

    def __init__(
        self,
        trader_id: Optional[str] = None,
        name: Optional[str] = None,
        trade_frequency: float = 5.0,
        symbols: Optional[list[str]] = None,
    ):
        """
        Initialize a simulated trader.

        Args:
            trader_id: Unique trader ID (generated if not provided)
            name: Trader name (generated if not provided)
            trade_frequency: Seconds between trades (average)
            symbols: List of symbols to trade (defaults to DEV_SYMBOLS)
        """
        self.trader_id = trader_id or str(uuid.uuid4())
        self.name = name or f"SimTrader_{self.trader_id[:8]}"
        self.trade_frequency = trade_frequency
        self.symbols = symbols or self.DEV_SYMBOLS
        self.is_running = False
        self.thread = None

        # RabbitMQ connection
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.response = None
        self.corr_id = None

        # Trading statistics
        self.orders_sent = 0
        self.responses_received = 0

    def connect(self):
        """Connect to RabbitMQ."""
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            self.channel = self.connection.channel()

            # Setup callback queue for responses
            result = self.channel.queue_declare(queue="", exclusive=True)
            self.callback_queue = result.method.queue

            self.channel.basic_consume(
                queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True
            )

            logger.info(f"[{self.name}] Connected to RabbitMQ")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Failed to connect to RabbitMQ: {e}")
            return False

    def on_response(self, ch, method, props, body):
        """Handle response from TES."""
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)
            self.responses_received += 1

    def send_order(self, symbol: str, side: str, quantity: float, price: float):
        """Send an order to the TES."""
        self.response = None
        self.corr_id = str(uuid.uuid4())

        order = {
            "action": "place_order",
            "trader_id": self.trader_id,
            "symbol": symbol,
            "side": side,  # 'buy' or 'sell'
            "quantity": quantity,
            "price": price,
            "type": "limit",
            "timestamp": time.time(),
        }

        try:
            self.channel.basic_publish(
                exchange="",
                routing_key="tes_requests",
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                ),
                body=json.dumps(order),
            )
            self.orders_sent += 1
            logger.debug(f"[{self.name}] Sent {side} order: {symbol} {quantity}@{price}")
        except Exception as e:
            logger.error(f"[{self.name}] Failed to send order: {e}")

    def generate_random_order(self):
        """Generate and send a random order."""
        symbol = random.choice(self.symbols)
        side = random.choice(["buy", "sell"])

        # Get price range for symbol
        min_price, max_price = self.PRICE_RANGES.get(symbol, (100.0, 200.0))

        # Generate random price within range
        price = round(random.uniform(min_price, max_price), 2)

        # Generate random quantity (multiples of 10)
        quantity = random.choice([10, 25, 50, 100, 150, 200]) * 1.0

        self.send_order(symbol, side, quantity, price)

    def trading_loop(self):
        """Main trading loop that runs in a separate thread."""
        logger.info(f"[{self.name}] Starting trading loop...")

        # Send initial connect message
        self.response = None
        self.corr_id = str(uuid.uuid4())

        connect_msg = {
            "action": "connect",
            "trader_id": self.trader_id,
            "timestamp": time.time(),
            "description": f"Simulated trader {self.name} connecting",
        }

        try:
            self.channel.basic_publish(
                exchange="",
                routing_key="tes_requests",
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                ),
                body=json.dumps(connect_msg),
            )
        except Exception as e:
            logger.error(f"[{self.name}] Failed to send connect message: {e}")
            return

        # Trading loop
        while self.is_running:
            try:
                # Process any pending messages
                self.connection.process_data_events(time_limit=0.1)

                # Place a random order
                self.generate_random_order()

                # Wait for a random interval (around trade_frequency seconds)
                sleep_time = random.uniform(self.trade_frequency * 0.5, self.trade_frequency * 1.5)
                time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"[{self.name}] Error in trading loop: {e}")
                time.sleep(1)

        logger.info(f"[{self.name}] Trading loop stopped. Sent {self.orders_sent} orders.")

    def start(self):
        """Start the simulated trader."""
        if self.is_running:
            logger.warning(f"[{self.name}] Already running")
            return

        if not self.connect():
            logger.error(f"[{self.name}] Cannot start - connection failed")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self.trading_loop, daemon=True)
        self.thread.start()
        logger.info(f"[{self.name}] Started")

    def stop(self):
        """Stop the simulated trader."""
        if not self.is_running:
            return

        logger.info(f"[{self.name}] Stopping...")
        self.is_running = False

        if self.thread:
            self.thread.join(timeout=5)

        if self.connection and self.connection.is_open:
            self.connection.close()

        logger.info(
            f"[{self.name}] Stopped. Stats: {self.orders_sent} orders sent, {self.responses_received} responses received"
        )

    def get_stats(self):
        """Get trading statistics."""
        return {
            "name": self.name,
            "trader_id": self.trader_id,
            "orders_sent": self.orders_sent,
            "responses_received": self.responses_received,
            "is_running": self.is_running,
        }


class SimulatedTradersManager:
    """Manages multiple simulated traders."""

    def __init__(self):
        """Initialize the traders manager."""
        self.traders: list[SimulatedTrader] = []

    def spawn_traders(
        self, count: int = 5, trade_frequency: float = 5.0, symbols: Optional[list[str]] = None
    ):
        """
        Spawn multiple simulated traders.

        Args:
            count: Number of traders to spawn
            trade_frequency: Average seconds between trades per trader
            symbols: List of symbols to trade
        """
        logger.info(f"Spawning {count} simulated traders...")

        for i in range(count):
            trader = SimulatedTrader(
                name=f"SimTrader_{i+1}", trade_frequency=trade_frequency, symbols=symbols
            )
            trader.start()
            self.traders.append(trader)
            time.sleep(0.2)  # Small delay between starting traders

        logger.info(f"✅ Spawned {count} simulated traders")

    def stop_all(self):
        """Stop all simulated traders."""
        logger.info(f"Stopping {len(self.traders)} simulated traders...")

        for trader in self.traders:
            trader.stop()

        self.traders.clear()
        logger.info("✅ All simulated traders stopped")

    def get_all_stats(self):
        """Get statistics for all traders."""
        return [trader.get_stats() for trader in self.traders]

    def generate_stats_table(self):
        """Generate a rich table with trader statistics."""
        stats = self.get_all_stats()

        table = Table(
            title="🤖 Simulated Traders Statistics",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
            border_style="cyan",
        )

        table.add_column("Trader", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Orders", justify="right", style="green")
        table.add_column("Responses", justify="right", style="blue")
        table.add_column("Response Rate", justify="right", style="yellow")

        total_orders = 0
        total_responses = 0
        active_count = 0

        for s in stats:
            status = "🟢 [green]Running[/green]" if s["is_running"] else "🔴 [red]Stopped[/red]"
            response_rate = (
                f"{(s['responses_received'] / s['orders_sent'] * 100):.1f}%"
                if s["orders_sent"] > 0
                else "0.0%"
            )

            table.add_row(
                s["name"],
                status,
                str(s["orders_sent"]),
                str(s["responses_received"]),
                response_rate,
            )

            total_orders += s["orders_sent"]
            total_responses += s["responses_received"]
            if s["is_running"]:
                active_count += 1

        # Add summary row
        if stats:
            table.add_section()
            overall_rate = (
                f"{(total_responses / total_orders * 100):.1f}%" if total_orders > 0 else "0.0%"
            )
            table.add_row(
                f"[bold]TOTAL ({active_count} active)[/bold]",
                "",
                f"[bold green]{total_orders}[/bold green]",
                f"[bold blue]{total_responses}[/bold blue]",
                f"[bold yellow]{overall_rate}[/bold yellow]",
            )

        return table

    def print_stats(self):
        """Print statistics for all traders using rich formatting."""
        table = self.generate_stats_table()
        console.print()
        console.print(table)
        console.print()


def run_simulated_traders(count: int = 5, trade_frequency: float = 5.0):
    """
    Run simulated traders (blocking).

    Args:
        count: Number of simulated traders
        trade_frequency: Average seconds between trades
    """
    manager = SimulatedTradersManager()

    try:
        # Display startup info
        console.print()
        console.print(
            Panel.fit(
                f"[bold green]Starting {count} Simulated Traders[/bold green]\n\n"
                f"📊 [cyan]Trade Frequency:[/cyan] ~{trade_frequency}s\n"
                f"📈 [cyan]Symbols:[/cyan] AAPL, GOOGL, MSFT, TSLA, AMZN\n"
                f"⏱️  [cyan]Stats Update:[/cyan] Every 30 seconds\n\n"
                f"[yellow]Press Ctrl+C to stop[/yellow]",
                border_style="green",
                title="🤖 Simulated Traders",
            )
        )
        console.print()

        manager.spawn_traders(count=count, trade_frequency=trade_frequency)

        console.print("[bold green]✓[/bold green] All traders started and placing orders...\n")
        logger.info("Simulated traders running. Press Ctrl+C to stop...")

        # Keep running and print stats periodically
        start_time = time.time()
        while True:
            time.sleep(30)
            elapsed = int(time.time() - start_time)
            console.print(f"[dim]Elapsed time: {elapsed}s[/dim]")
            manager.print_stats()

    except KeyboardInterrupt:
        console.print("\n[yellow]Received shutdown signal...[/yellow]")
        logger.info("\nShutting down simulated traders...")

        with console.status("[yellow]Stopping all traders...", spinner="dots"):
            manager.stop_all()

        # Final stats
        console.print("\n[bold cyan]Final Statistics:[/bold cyan]")
        manager.print_stats()

        console.print("[bold green]✓[/bold green] Simulated traders shutdown complete\n")

    logger.info("Simulated traders shutdown complete")
