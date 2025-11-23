#!/usr/bin/env python
"""Quick test of the enhanced CLI with typer and rich."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def test_panels():
    """Test rich panels."""
    console.print("\n[bold cyan]1. Testing Panels[/bold cyan]\n")
    
    console.print(Panel(
        "[bold green]Order Book Server (OBS)[/bold green]\n"
        "Order matching • Strategy execution • Trade recording",
        title="🚀 Starting Server",
        border_style="green"
    ))
    
    console.print(Panel(
        "[bold cyan]Mock Data Generator[/bold cyan]\n"
        "• 20 test users with balances\n"
        "• 100 historical orders\n"
        "• 50 executed trades\n"
        "• 10 trading instruments",
        title="📊 Initializing Mock Data",
        border_style="cyan"
    ))


def test_tables():
    """Test rich tables."""
    console.print("\n[bold cyan]2. Testing Statistics Table[/bold cyan]\n")
    
    table = Table(
        title="🤖 Simulated Traders Statistics",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="cyan"
    )
    
    table.add_column("Trader", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Orders", justify="right", style="green")
    table.add_column("Responses", justify="right", style="blue")
    table.add_column("Response Rate", justify="right", style="yellow")
    
    # Sample data
    traders = [
        ("SimTrader_1", "🟢 [green]Running[/green]", 45, 45),
        ("SimTrader_2", "🟢 [green]Running[/green]", 43, 43),
        ("SimTrader_3", "🟢 [green]Running[/green]", 47, 47),
        ("SimTrader_4", "🔴 [red]Stopped[/red]", 30, 30),
        ("SimTrader_5", "🟢 [green]Running[/green]", 46, 46),
    ]
    
    total_orders = 0
    total_responses = 0
    
    for name, status, orders, responses in traders:
        rate = f"{(responses / orders * 100):.1f}%" if orders > 0 else "0.0%"
        table.add_row(name, status, str(orders), str(responses), rate)
        total_orders += orders
        total_responses += responses
    
    # Summary
    table.add_section()
    overall_rate = f"{(total_responses / total_orders * 100):.1f}%"
    table.add_row(
        "[bold]TOTAL (4 active)[/bold]",
        "",
        f"[bold green]{total_orders}[/bold green]",
        f"[bold blue]{total_responses}[/bold blue]",
        f"[bold yellow]{overall_rate}[/bold yellow]"
    )
    
    console.print(table)


def test_status():
    """Test status indicators."""
    console.print("\n[bold cyan]3. Testing Status Indicators[/bold cyan]\n")
    
    import time
    
    with console.status("[bold cyan]Loading mock data...", spinner="dots"):
        time.sleep(1.5)
    
    console.print("[bold green]✓[/bold green] Mock data loaded successfully!")
    
    with console.status("[yellow]Stopping all traders...", spinner="dots"):
        time.sleep(1.5)
    
    console.print("[bold green]✓[/bold green] All traders stopped")


def test_colors():
    """Test color scheme."""
    console.print("\n[bold cyan]4. Testing Color Scheme[/bold cyan]\n")
    
    console.print("[bold cyan]Cyan:[/bold cyan] Servers (TES)")
    console.print("[bold green]Green:[/bold green] OBS, Success messages")
    console.print("[bold yellow]Yellow:[/bold yellow] Warnings, Clients")
    console.print("[bold magenta]Magenta:[/bold magenta] Frontends")
    console.print("[bold red]Red:[/bold red] Errors, Stop indicators")
    console.print("[bold blue]Blue:[/bold blue] Responses, Secondary info")


def main():
    """Run all tests."""
    console.print(Panel.fit(
        "[bold]Rich & Typer CLI Enhancement Test[/bold]\n\n"
        "This script tests the visual improvements to the trading engine CLI.",
        border_style="magenta",
        title="🎨 CLI Test Suite"
    ))
    
    test_panels()
    test_tables()
    test_status()
    test_colors()
    
    console.print("\n" + "="*60)
    console.print("[bold green]All tests completed! ✨[/bold green]")
    console.print("="*60 + "\n")
    
    console.print("[dim]Run 'python main.py --help' to see the full CLI in action![/dim]\n")


if __name__ == "__main__":
    main()
