"""
Dashboard - Market overview and recent activity
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from trading import get_orders, get_trader_id, get_trades

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Market Dashboard")

# Get trader info
trader_id = get_trader_id()

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto-refresh (every 5s)", value=False)
if auto_refresh:
    import time

    time.sleep(5)
    st.rerun()

# Refresh button
if st.sidebar.button("🔄 Refresh Now"):
    st.rerun()

# Market Overview
st.header("📈 Market Overview")

col1, col2, col3, col4 = st.columns(4)

try:
    # Get recent data
    all_orders = get_orders(limit=1000)
    all_trades = get_trades(limit=1000)

    with col1:
        st.metric("Total Orders", len(all_orders))

    with col2:
        st.metric("Total Trades", len(all_trades))

    with col3:
        active_orders = [o for o in all_orders if o.get("status") == "pending"]
        st.metric("Active Orders", len(active_orders))

    with col4:
        # Calculate total volume
        total_volume = sum(t.get("quantity", 0) for t in all_trades)
        st.metric("Total Volume", f"{total_volume:,.0f}")

except Exception as e:
    st.error(f"Error loading market overview: {e}")

# Recent Activity
st.header("🔄 Recent Activity")

tab1, tab2 = st.tabs(["Recent Orders", "Recent Trades"])

with tab1:
    st.subheader("Latest Orders")
    try:
        orders = get_orders(limit=20)
        if orders:
            df = pd.DataFrame(orders)
            # Format columns
            if not df.empty:
                display_cols = [
                    "timestamp",
                    "order_id",
                    "trader_id",
                    "symbol",
                    "side",
                    "quantity",
                    "price",
                    "status",
                ]
                # Only show columns that exist
                display_cols = [col for col in display_cols if col in df.columns]
                df = df[display_cols]
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("No orders yet. Place your first order!")
    except Exception as e:
        st.error(f"Error loading orders: {e}")

with tab2:
    st.subheader("Latest Trades")
    try:
        trades = get_trades(limit=20)
        if trades:
            df = pd.DataFrame(trades)
            if not df.empty:
                display_cols = [
                    "timestamp",
                    "trade_id",
                    "symbol",
                    "quantity",
                    "price",
                    "buy_trader_id",
                    "sell_trader_id",
                ]
                # Only show columns that exist
                display_cols = [col for col in display_cols if col in df.columns]
                df = df[display_cols]
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("No trades yet. Submit orders to start trading!")
    except Exception as e:
        st.error(f"Error loading trades: {e}")

# Symbol Activity
st.header("💹 Symbol Activity")

try:
    trades = get_trades(limit=100)
    if trades:
        df = pd.DataFrame(trades)

        # Group by symbol
        if "symbol" in df.columns and "quantity" in df.columns:
            symbol_stats = (
                df.groupby("symbol")
                .agg({"quantity": "sum", "trade_id": "count", "price": ["min", "max", "mean"]})
                .reset_index()
            )

            symbol_stats.columns = [
                "Symbol",
                "Total Volume",
                "Trade Count",
                "Min Price",
                "Max Price",
                "Avg Price",
            ]

            st.dataframe(
                symbol_stats.style.format(
                    {
                        "Total Volume": "{:,.0f}",
                        "Trade Count": "{:,.0f}",
                        "Min Price": "${:.2f}",
                        "Max Price": "${:.2f}",
                        "Avg Price": "${:.2f}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Not enough trade data to show symbol statistics")
    else:
        st.info("No trades yet")
except Exception as e:
    st.error(f"Error calculating symbol activity: {e}")

# Footer
st.markdown("---")
st.caption(f"Trader ID: {trader_id[:16]}... | Dashboard auto-refreshes when enabled")
