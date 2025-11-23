"""
Trade History - Review trading history and analytics
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from trading import get_trader_id, get_trader_name, get_trades

st.set_page_config(page_title="Trade History", page_icon="📈", layout="wide")

st.title("📈 Trade History & Analytics")

# Get trader info
trader_id = get_trader_id()
trader_name = get_trader_name()

# Sidebar
st.sidebar.markdown("### 👤 Your Info")
st.sidebar.write(f"**Name:** {trader_name}")
st.sidebar.write(f"**ID:** `{trader_id[:8]}...`")
st.sidebar.markdown("---")

# View toggle
view_mode = st.sidebar.radio("View Mode", ["My Trades Only", "All Market Trades"], index=0)

if st.sidebar.button("🔄 Refresh"):
    st.rerun()

# Get trades based on view mode
if view_mode == "My Trades Only":
    trades = get_trades(trader_id=trader_id, limit=100)
    st.header(f"📊 My Trade History ({len(trades)} trades)")
else:
    trades = get_trades(limit=100)
    st.header(f"📊 Market Trade History ({len(trades)} trades)")

# Display trades
if trades:
    df = pd.DataFrame(trades)

    # Trade statistics
    st.subheader("📈 Summary Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Trades", len(df))

    with col2:
        total_volume = df["quantity"].sum() if "quantity" in df.columns else 0
        st.metric("Total Volume", f"{total_volume:,.0f}")

    with col3:
        avg_price = df["price"].mean() if "price" in df.columns else 0
        st.metric("Avg Price", f"${avg_price:.2f}")

    with col4:
        total_value = (
            (df["quantity"] * df["price"]).sum()
            if "quantity" in df.columns and "price" in df.columns
            else 0
        )
        st.metric("Total Value", f"${total_value:,.2f}")

    # Trades table
    st.subheader("📋 Trade Details")

    # Filter options
    col1, col2 = st.columns(2)

    with col1:
        if "symbol" in df.columns:
            symbol_filter = st.multiselect(
                "Filter by Symbol",
                options=sorted(df["symbol"].unique()),
                default=sorted(df["symbol"].unique()),
            )
        else:
            symbol_filter = None

    with col2:
        # Date range filter
        show_latest = st.slider("Show latest N trades", min_value=10, max_value=100, value=50)

    # Apply filters
    filtered_df = df.copy()
    if symbol_filter and "symbol" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["symbol"].isin(symbol_filter)]

    filtered_df = filtered_df.head(show_latest)

    # Display table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

    # Analytics
    st.subheader("📊 Trade Analytics")

    tab1, tab2, tab3 = st.tabs(["Volume by Symbol", "Price Distribution", "Trade Timeline"])

    with tab1:
        if "symbol" in filtered_df.columns and "quantity" in filtered_df.columns:
            import plotly.express as px

            symbol_volume = filtered_df.groupby("symbol")["quantity"].sum().reset_index()
            symbol_volume.columns = ["Symbol", "Total Volume"]

            fig = px.bar(
                symbol_volume,
                x="Symbol",
                y="Total Volume",
                title="Trading Volume by Symbol",
                color="Total Volume",
                color_continuous_scale="viridis",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for volume analysis")

    with tab2:
        if "price" in filtered_df.columns and "symbol" in filtered_df.columns:
            import plotly.express as px

            fig = px.box(
                filtered_df,
                x="symbol",
                y="price",
                title="Price Distribution by Symbol",
                color="symbol",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for price distribution")

    with tab3:
        if "timestamp" in filtered_df.columns and "quantity" in filtered_df.columns:
            import plotly.express as px

            # Convert timestamp if needed
            timeline_df = filtered_df.copy()
            if "timestamp" in timeline_df.columns:
                timeline_df["timestamp"] = pd.to_datetime(timeline_df["timestamp"])

            fig = px.scatter(
                timeline_df,
                x="timestamp",
                y="price",
                size="quantity",
                color="symbol" if "symbol" in timeline_df.columns else None,
                title="Trade Timeline",
                labels={"timestamp": "Time", "price": "Price ($)"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for timeline analysis")

    # Performance metrics (for "My Trades Only" mode)
    if view_mode == "My Trades Only" and len(filtered_df) > 0:
        st.subheader("💼 My Performance")

        perf_col1, perf_col2, perf_col3 = st.columns(3)

        with perf_col1:
            # Count buy vs sell
            if "buy_trader_id" in filtered_df.columns and "sell_trader_id" in filtered_df.columns:
                buy_count = (filtered_df["buy_trader_id"] == trader_id).sum()
                sell_count = (filtered_df["sell_trader_id"] == trader_id).sum()

                st.metric("Buy Trades", buy_count)
                st.metric("Sell Trades", sell_count)

        with perf_col2:
            # Average trade size
            if "quantity" in filtered_df.columns:
                avg_quantity = filtered_df["quantity"].mean()
                st.metric("Avg Trade Size", f"{avg_quantity:,.0f}")

                total_quantity = filtered_df["quantity"].sum()
                st.metric("Total Volume", f"{total_quantity:,.0f}")

        with perf_col3:
            # Trading activity
            if "symbol" in filtered_df.columns:
                unique_symbols = filtered_df["symbol"].nunique()
                st.metric("Symbols Traded", unique_symbols)

                most_traded = filtered_df["symbol"].mode()[0] if len(filtered_df) > 0 else "N/A"
                st.metric("Most Traded", most_traded)

else:
    st.info("No trades yet. Place orders to start trading!")

    if st.button("📝 Place Your First Order", use_container_width=False):
        st.switch_page("pages/1_📝_Place_Order.py")

# Export option
if trades:
    st.markdown("---")
    st.markdown("### 💾 Export Data")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"trades_{trader_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    with col2:
        json_str = filtered_df.to_json(orient="records", indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_str,
            file_name=f"trades_{trader_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

# Footer
st.markdown("---")
st.caption(f"Trader: {trader_name} ({trader_id[:16]}...)")
