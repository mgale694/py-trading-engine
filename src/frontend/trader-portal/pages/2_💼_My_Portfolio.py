"""
My Portfolio - View positions and portfolio performance
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from trading import get_orders, get_portfolio, get_positions, get_trader_id, get_trader_name

st.set_page_config(page_title="My Portfolio", page_icon="💼", layout="wide")

st.title("💼 My Portfolio")

# Get trader info
trader_id = get_trader_id()
trader_name = get_trader_name()

# Sidebar
st.sidebar.markdown("### 👤 Your Info")
st.sidebar.write(f"**Name:** {trader_name}")
st.sidebar.write(f"**ID:** `{trader_id[:8]}...`")
st.sidebar.markdown("---")

if st.sidebar.button("🔄 Refresh Portfolio"):
    st.rerun()

# Portfolio Summary
st.header("📊 Portfolio Summary")

try:
    portfolio = get_portfolio(trader_id)

    if portfolio:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            cash = portfolio.get("cash", 0.0)
            st.metric("Cash Balance", f"${cash:,.2f}")

        with col2:
            equity = portfolio.get("equity_value", 0.0)
            st.metric("Equity Value", f"${equity:,.2f}")

        with col3:
            total_value = cash + equity
            st.metric("Total Value", f"${total_value:,.2f}")

        with col4:
            pnl = portfolio.get("realized_pnl", 0.0)
            st.metric("Realized P&L", f"${pnl:,.2f}", delta=f"{pnl:,.2f}")

    else:
        st.info(
            "No portfolio found. Your portfolio will be created when you place your first order."
        )

except Exception as e:
    st.error(f"Error loading portfolio: {e}")

# Current Positions
st.header("📈 Current Positions")

try:
    positions = get_positions(trader_id)

    if positions:
        df = pd.DataFrame(positions)

        # Calculate unrealized P&L if possible
        if "quantity" in df.columns and "average_price" in df.columns:
            st.dataframe(
                df.style.format(
                    {
                        "quantity": "{:,.0f}",
                        "average_price": "${:.2f}",
                        "total_cost": "${:,.2f}",
                        "current_value": "${:,.2f}",
                        "unrealized_pnl": "${:,.2f}",
                    }
                    if "unrealized_pnl" in df.columns
                    else {
                        "quantity": "{:,.0f}",
                        "average_price": "${:.2f}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

            # Position breakdown chart
            st.markdown("### 📊 Position Breakdown")

            import plotly.express as px

            if "symbol" in df.columns and "quantity" in df.columns:
                fig = px.pie(df, values="quantity", names="symbol", title="Positions by Symbol")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        st.info("No positions yet. Place orders to build your portfolio!")

except Exception as e:
    st.error(f"Error loading positions: {e}")

# My Orders
st.header("📝 My Orders")

try:
    my_orders = get_orders(trader_id=trader_id, limit=50)

    if my_orders:
        df = pd.DataFrame(my_orders)

        # Filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=df["status"].unique() if "status" in df.columns else [],
                default=df["status"].unique() if "status" in df.columns else [],
            )

        with col2:
            symbol_filter = st.multiselect(
                "Filter by Symbol",
                options=df["symbol"].unique() if "symbol" in df.columns else [],
                default=df["symbol"].unique() if "symbol" in df.columns else [],
            )

        with col3:
            side_filter = st.multiselect(
                "Filter by Side",
                options=df["side"].unique() if "side" in df.columns else [],
                default=df["side"].unique() if "side" in df.columns else [],
            )

        # Apply filters
        filtered_df = df.copy()
        if status_filter:
            filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]
        if symbol_filter:
            filtered_df = filtered_df[filtered_df["symbol"].isin(symbol_filter)]
        if side_filter:
            filtered_df = filtered_df[filtered_df["side"].isin(side_filter)]

        # Display filtered orders
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
        )

        # Order statistics
        st.markdown("### 📊 Order Statistics")

        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

        with stat_col1:
            st.metric("Total Orders", len(filtered_df))

        with stat_col2:
            filled = len(filtered_df[filtered_df["status"] == "filled"])
            st.metric("Filled Orders", filled)

        with stat_col3:
            pending = len(filtered_df[filtered_df["status"] == "pending"])
            st.metric("Pending Orders", pending)

        with stat_col4:
            cancelled = len(filtered_df[filtered_df["status"] == "cancelled"])
            st.metric("Cancelled Orders", cancelled)

    else:
        st.info("No orders yet. Go to Place Order to submit your first order!")

except Exception as e:
    st.error(f"Error loading orders: {e}")

# Quick actions
st.markdown("---")
st.markdown("### 🎯 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Place New Order", use_container_width=True):
        st.switch_page("pages/1_📝_Place_Order.py")

with col2:
    if st.button("📈 View Trade History", use_container_width=True):
        st.switch_page("pages/3_📈_Trade_History.py")

with col3:
    if st.button("📊 Go to Dashboard", use_container_width=True):
        st.switch_page("pages/0_📊_Dashboard.py")

# Footer
st.markdown("---")
st.caption(f"Trader: {trader_name} ({trader_id[:16]}...)")
