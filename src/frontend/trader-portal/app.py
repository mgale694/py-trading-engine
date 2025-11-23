"""
Trader Portal - Home Page
Multi-page Streamlit app for client traders.
"""

import sys
from pathlib import Path

import streamlit as st

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))

from trading import connect_trader_to_tes, get_trader_id, get_trader_name

# Page configuration
st.set_page_config(
    page_title="Trader Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize trader session
trader_id = get_trader_id()
trader_name = get_trader_name()

# Connect to TES if not already connected
if "connected_to_tes" not in st.session_state:
    with st.spinner("Connecting to Trading Engine..."):
        result = connect_trader_to_tes()
        if result["success"]:
            st.session_state.connected_to_tes = True
        else:
            st.warning(f"Could not connect to TES: {result.get('error', 'Unknown error')}")
            st.info("You can still view data, but order submission will be unavailable.")
            st.session_state.connected_to_tes = False

# Main page content
st.write("# Welcome to the Trading Portal! 💼")

# Sidebar trader info
st.sidebar.success("Select a page above.")
st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Trader Info")
st.sidebar.markdown(f"**Name:** {trader_name}")
st.sidebar.markdown(f"**ID:** `{trader_id[:8]}...`")

if st.session_state.get("connected_to_tes"):
    st.sidebar.success("🟢 Connected to TES")
else:
    st.sidebar.error("🔴 Not connected to TES")

# Welcome content
st.markdown(
    f"""
    This is your personal trading portal for executing trades and monitoring your portfolio.

    ### 👈 Select a page from the sidebar

    **Available pages:**
    - **📊 Dashboard** - View market overview and recent activity
    - **📝 Place Order** - Submit buy/sell orders to the trading engine
    - **💼 My Portfolio** - View your positions and portfolio performance
    - **📈 Trade History** - Review your trading history and analytics
    - **🔍 Market Data** - Real-time market data and order book

    ### 🚀 Getting Started

    1. Navigate to **Place Order** to submit your first trade
    2. Check **My Portfolio** to see your positions
    3. Review **Trade History** for performance analytics

    ### 📊 Your Trader Profile

    You have a unique trader ID that tracks all your orders and trades.
    This ID is persistent across sessions and stored securely.

    ### ⚠️ Important Notes

    - All orders are sent to the **Trading Engine Server (TES)**
    - Orders are matched by the **Order Book Server (OBS)**
    - Real-time data is pulled from the **transactional database**
    - Your trader ID: `{trader_id}`

    ### 🔐 Connection Status

    """
)

# Connection status
col1, col2, col3 = st.columns(3)

with col1:
    if st.session_state.get("connected_to_tes"):
        st.success("✅ Trading Engine Server")
    else:
        st.error("❌ Trading Engine Server")

with col2:
    try:
        from trading import get_db_connection

        conn = get_db_connection()
        conn.close()
        st.success("✅ Database Connection")
    except Exception as e:
        st.error(f"❌ Database Connection: {e}")

with col3:
    import pika

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost", connection_attempts=1, retry_delay=1)
        )
        connection.close()
        st.success("✅ RabbitMQ Broker")
    except Exception:
        st.error("❌ RabbitMQ Broker")

# Quick actions
st.markdown("### 🎯 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Place New Order", use_container_width=True):
        st.switch_page("pages/1_📝_Place_Order.py")

with col2:
    if st.button("💼 View Portfolio", use_container_width=True):
        st.switch_page("pages/2_💼_My_Portfolio.py")

with col3:
    if st.button("📈 Trade History", use_container_width=True):
        st.switch_page("pages/3_📈_Trade_History.py")
