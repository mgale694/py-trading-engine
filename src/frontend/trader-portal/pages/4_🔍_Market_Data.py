"""
Market Data - Real-time order book and market depth
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from trading import get_orders, get_trader_id, get_trader_name

st.set_page_config(page_title="Market Data", page_icon="🔍", layout="wide")

st.title("🔍 Market Data & Order Book")

# Get trader info
trader_id = get_trader_id()
trader_name = get_trader_name()

# Sidebar
st.sidebar.markdown("### 👤 Your Info")
st.sidebar.write(f"**Name:** {trader_name}")
st.sidebar.write(f"**ID:** `{trader_id[:8]}...`")
st.sidebar.markdown("---")

# Symbol selector
available_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
selected_symbol = st.sidebar.selectbox("Select Symbol", available_symbols, index=0)

# Auto-refresh
auto_refresh = st.sidebar.checkbox("Auto Refresh (5s)", value=False)

if st.sidebar.button("🔄 Refresh Now"):
    st.rerun()

if auto_refresh:
    import time

    time.sleep(5)
    st.rerun()

st.header(f"📊 Order Book - {selected_symbol}")

# Get open orders for this symbol
all_orders = get_orders()

if all_orders:
    df = pd.DataFrame(all_orders)

    # Filter for selected symbol and open orders
    if "symbol" in df.columns and "status" in df.columns:
        symbol_orders = df[(df["symbol"] == selected_symbol) & (df["status"] == "open")].copy()

        # Split into buy and sell orders
        buy_orders = symbol_orders[symbol_orders["side"] == "buy"].copy()
        sell_orders = symbol_orders[symbol_orders["side"] == "sell"].copy()

        # Sort appropriately
        if len(buy_orders) > 0:
            buy_orders = buy_orders.sort_values("price", ascending=False)
        if len(sell_orders) > 0:
            sell_orders = sell_orders.sort_values("price", ascending=True)

        # Order book visualization
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🟢 Buy Orders (Bids)")
            if len(buy_orders) > 0:
                # Aggregate by price level
                buy_book = (
                    buy_orders.groupby("price")["quantity"]
                    .sum()
                    .reset_index()
                    .sort_values("price", ascending=False)
                )
                buy_book.columns = ["Price", "Quantity"]
                buy_book["Cumulative"] = buy_book["Quantity"].cumsum()

                st.dataframe(
                    buy_book.head(20),
                    use_container_width=True,
                    hide_index=True,
                )

                # Best bid
                best_bid = buy_book.iloc[0]["Price"]
                st.metric("Best Bid", f"${best_bid:.2f}")
            else:
                st.info("No buy orders in the book")
                best_bid = None

        with col2:
            st.subheader("🔴 Sell Orders (Asks)")
            if len(sell_orders) > 0:
                # Aggregate by price level
                sell_book = (
                    sell_orders.groupby("price")["quantity"]
                    .sum()
                    .reset_index()
                    .sort_values("price", ascending=True)
                )
                sell_book.columns = ["Price", "Quantity"]
                sell_book["Cumulative"] = sell_book["Quantity"].cumsum()

                st.dataframe(
                    sell_book.head(20),
                    use_container_width=True,
                    hide_index=True,
                )

                # Best ask
                best_ask = sell_book.iloc[0]["Price"]
                st.metric("Best Ask", f"${best_ask:.2f}")
            else:
                st.info("No sell orders in the book")
                best_ask = None

        # Market spread
        st.markdown("---")
        st.subheader("📊 Market Statistics")

        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

        with stat_col1:
            if best_bid and best_ask:
                spread = best_ask - best_bid
                st.metric("Spread", f"${spread:.2f}")
            else:
                st.metric("Spread", "N/A")

        with stat_col2:
            if best_bid and best_ask:
                mid_price = (best_bid + best_ask) / 2
                st.metric("Mid Price", f"${mid_price:.2f}")
            else:
                st.metric("Mid Price", "N/A")

        with stat_col3:
            total_buy_volume = buy_orders["quantity"].sum() if len(buy_orders) > 0 else 0
            st.metric("Total Buy Volume", f"{total_buy_volume:,.0f}")

        with stat_col4:
            total_sell_volume = sell_orders["quantity"].sum() if len(sell_orders) > 0 else 0
            st.metric("Total Sell Volume", f"{total_sell_volume:,.0f}")

        # Market depth visualization
        st.markdown("---")
        st.subheader("📈 Market Depth")

        if len(buy_orders) > 0 or len(sell_orders) > 0:
            import plotly.graph_objects as go

            fig = go.Figure()

            # Buy side (green)
            if len(buy_orders) > 0:
                buy_book_for_plot = (
                    buy_orders.groupby("price")["quantity"].sum().reset_index().sort_values("price")
                )
                buy_book_for_plot["cumulative"] = buy_book_for_plot["quantity"].cumsum()

                fig.add_trace(
                    go.Scatter(
                        x=buy_book_for_plot["price"],
                        y=buy_book_for_plot["cumulative"],
                        fill="tozeroy",
                        name="Buy Orders",
                        line=dict(color="green"),
                        fillcolor="rgba(0, 255, 0, 0.2)",
                    )
                )

            # Sell side (red)
            if len(sell_orders) > 0:
                sell_book_for_plot = (
                    sell_orders.groupby("price")["quantity"]
                    .sum()
                    .reset_index()
                    .sort_values("price")
                )
                sell_book_for_plot["cumulative"] = sell_book_for_plot["quantity"].cumsum()

                fig.add_trace(
                    go.Scatter(
                        x=sell_book_for_plot["price"],
                        y=sell_book_for_plot["cumulative"],
                        fill="tozeroy",
                        name="Sell Orders",
                        line=dict(color="red"),
                        fillcolor="rgba(255, 0, 0, 0.2)",
                    )
                )

            fig.update_layout(
                title=f"Market Depth - {selected_symbol}",
                xaxis_title="Price ($)",
                yaxis_title="Cumulative Volume",
                hovermode="x unified",
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No orders to display market depth")

        # Recent orders table
        st.markdown("---")
        st.subheader("📋 Recent Orders")

        recent_orders = symbol_orders.head(20)
        if len(recent_orders) > 0:
            st.dataframe(
                recent_orders[
                    [
                        col
                        for col in [
                            "order_id",
                            "side",
                            "quantity",
                            "price",
                            "type",
                            "status",
                            "timestamp",
                        ]
                        if col in recent_orders.columns
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No recent orders")

    else:
        st.warning("Order data incomplete")

else:
    st.info("No orders in the system yet. Start trading to see market data!")

# Market overview
st.markdown("---")
st.subheader("🌐 All Symbols Overview")

if all_orders:
    df = pd.DataFrame(all_orders)

    if "symbol" in df.columns and "status" in df.columns:
        # Filter for open orders
        open_orders = df[df["status"] == "open"].copy()

        # Group by symbol
        symbol_stats = []

        for symbol in available_symbols:
            symbol_orders = open_orders[open_orders["symbol"] == symbol]

            if len(symbol_orders) > 0:
                buy_orders = symbol_orders[symbol_orders["side"] == "buy"]
                sell_orders = symbol_orders[symbol_orders["side"] == "sell"]

                best_bid = buy_orders["price"].max() if len(buy_orders) > 0 else None
                best_ask = sell_orders["price"].min() if len(sell_orders) > 0 else None

                symbol_stats.append(
                    {
                        "Symbol": symbol,
                        "Best Bid": f"${best_bid:.2f}" if best_bid else "N/A",
                        "Best Ask": f"${best_ask:.2f}" if best_ask else "N/A",
                        "Spread": f"${best_ask - best_bid:.2f}" if best_bid and best_ask else "N/A",
                        "Buy Volume": buy_orders["quantity"].sum() if len(buy_orders) > 0 else 0,
                        "Sell Volume": sell_orders["quantity"].sum() if len(sell_orders) > 0 else 0,
                        "Total Orders": len(symbol_orders),
                    }
                )

        if symbol_stats:
            overview_df = pd.DataFrame(symbol_stats)
            st.dataframe(overview_df, use_container_width=True, hide_index=True)
        else:
            st.info("No open orders across any symbols")

# Quick actions
st.markdown("---")
st.markdown("### ⚡ Quick Actions")

action_col1, action_col2 = st.columns(2)

with action_col1:
    if st.button("📝 Place Order for " + selected_symbol, use_container_width=True):
        st.switch_page("pages/1_📝_Place_Order.py")

with action_col2:
    if st.button("📈 View Trade History", use_container_width=True):
        st.switch_page("pages/3_📈_Trade_History.py")

# Footer
st.markdown("---")
st.caption(f"Trader: {trader_name} ({trader_id[:16]}...) | Viewing: {selected_symbol}")
