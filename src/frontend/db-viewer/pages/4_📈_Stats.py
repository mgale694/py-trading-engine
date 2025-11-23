"""
Statistics Page - Database analytics and insights
"""

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Database Statistics", page_icon="📈", layout="wide")

st.title("📈 Database Statistics")

# Get database path
DB_PATH = (
    Path(__file__).parent.parent.parent.parent / "database" / "transactional" / "trading_engine.db"
)

if not DB_PATH.exists():
    st.error("❌ Database not found")
    st.stop()

try:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Overall statistics
    st.subheader("📊 Overall Statistics")

    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM trades")
    trade_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM portfolios")
    portfolio_count = cursor.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Users", user_count)

    with col2:
        st.metric("Total Orders", order_count)

    with col3:
        st.metric("Total Trades", trade_count)

    with col4:
        st.metric("Portfolios", portfolio_count)

    # Orders analysis
    if order_count > 0:
        st.markdown("---")
        st.subheader("📋 Orders Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Orders by status
            cursor.execute("SELECT status, COUNT(*) as count FROM orders GROUP BY status")
            status_data = cursor.fetchall()
            if status_data:
                df_status = pd.DataFrame(status_data, columns=["Status", "Count"])
                fig = px.pie(
                    df_status,
                    values="Count",
                    names="Status",
                    title="Orders by Status",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Orders by side
            cursor.execute("SELECT side, COUNT(*) as count FROM orders GROUP BY side")
            side_data = cursor.fetchall()
            if side_data:
                df_side = pd.DataFrame(side_data, columns=["Side", "Count"])
                fig = px.bar(
                    df_side,
                    x="Side",
                    y="Count",
                    title="Orders by Side (Buy/Sell)",
                    color="Side",
                    color_discrete_map={"buy": "green", "sell": "red"},
                )
                st.plotly_chart(fig, use_container_width=True)

        # Orders by symbol
        cursor.execute(
            "SELECT symbol, COUNT(*) as count FROM orders GROUP BY symbol ORDER BY count DESC"
        )
        symbol_data = cursor.fetchall()
        if symbol_data:
            df_symbol = pd.DataFrame(symbol_data, columns=["Symbol", "Count"])
            fig = px.bar(
                df_symbol,
                x="Symbol",
                y="Count",
                title="Orders by Symbol",
                color="Count",
                color_continuous_scale="viridis",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Trades analysis
    if trade_count > 0:
        st.markdown("---")
        st.subheader("💰 Trades Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Trades by symbol
            cursor.execute(
                "SELECT symbol, COUNT(*) as count, SUM(quantity) as volume FROM trades GROUP BY symbol"
            )
            trade_symbol_data = cursor.fetchall()
            if trade_symbol_data:
                df_trade_symbol = pd.DataFrame(
                    trade_symbol_data, columns=["Symbol", "Count", "Volume"]
                )
                fig = px.bar(
                    df_trade_symbol,
                    x="Symbol",
                    y="Count",
                    title="Trades by Symbol",
                    color="Volume",
                    color_continuous_scale="blues",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Trading volume by symbol
            if trade_symbol_data:
                fig = px.pie(
                    df_trade_symbol,
                    values="Volume",
                    names="Symbol",
                    title="Trading Volume Distribution",
                )
                st.plotly_chart(fig, use_container_width=True)

        # Price analysis
        cursor.execute(
            "SELECT symbol, AVG(price) as avg_price, MIN(price) as min_price, MAX(price) as max_price FROM trades GROUP BY symbol"
        )
        price_data = cursor.fetchall()
        if price_data:
            st.markdown("#### 💵 Price Statistics by Symbol")
            df_price = pd.DataFrame(
                price_data, columns=["Symbol", "Avg Price", "Min Price", "Max Price"]
            )
            st.dataframe(df_price, use_container_width=True, hide_index=True)

        # Trade timeline
        cursor.execute(
            "SELECT DATE(timestamp) as date, COUNT(*) as count FROM trades GROUP BY DATE(timestamp) ORDER BY date"
        )
        timeline_data = cursor.fetchall()
        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data, columns=["Date", "Count"])
            fig = px.line(
                df_timeline,
                x="Date",
                y="Count",
                title="Trading Activity Over Time",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)

    # Table sizes
    st.markdown("---")
    st.subheader("📦 Table Sizes")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    table_sizes = []
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        table_sizes.append({"Table": table, "Rows": count})

    df_sizes = pd.DataFrame(table_sizes)
    fig = px.bar(
        df_sizes,
        x="Table",
        y="Rows",
        title="Records per Table",
        color="Rows",
        color_continuous_scale="teal",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Recent activity
    st.markdown("---")
    st.subheader("🕐 Recent Activity")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Recent Orders**")
        cursor.execute(
            "SELECT id, symbol, side, quantity, price, status FROM orders ORDER BY created_at DESC LIMIT 5"
        )
        recent_orders = cursor.fetchall()
        if recent_orders:
            df_orders = pd.DataFrame(
                recent_orders,
                columns=["ID", "Symbol", "Side", "Quantity", "Price", "Status"],
            )
            st.dataframe(df_orders, use_container_width=True, hide_index=True)
        else:
            st.info("No orders yet")

    with col2:
        st.markdown("**Recent Trades**")
        cursor.execute(
            "SELECT id, symbol, side, quantity, price FROM trades ORDER BY timestamp DESC LIMIT 5"
        )
        recent_trades = cursor.fetchall()
        if recent_trades:
            df_trades = pd.DataFrame(
                recent_trades, columns=["ID", "Symbol", "Side", "Quantity", "Price"]
            )
            st.dataframe(df_trades, use_container_width=True, hide_index=True)
        else:
            st.info("No trades yet")

    conn.close()

    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Statistics", use_container_width=False):
        st.rerun()

except Exception as e:
    st.error(f"❌ Error: {e}")

# Footer
st.markdown("---")
st.caption(f"Database: {DB_PATH.name}")
