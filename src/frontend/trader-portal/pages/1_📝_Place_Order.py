"""
Place Order - Submit buy/sell orders to the trading engine
"""

import sys
import time
from pathlib import Path

import streamlit as st

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from trading import get_trader_id, get_trader_name, send_order_to_tes

st.set_page_config(page_title="Place Order", page_icon="📝", layout="wide")

st.title("📝 Place Order")

# Get trader info
trader_id = get_trader_id()
trader_name = get_trader_name()

# Check TES connection
if not st.session_state.get("connected_to_tes"):
    st.error("⚠️ Not connected to Trading Engine Server")
    st.info(
        "Orders cannot be submitted without TES connection. Please restart the app or check if TES is running."
    )
    st.stop()

# Trader info in sidebar
st.sidebar.markdown("### 👤 Your Info")
st.sidebar.write(f"**Name:** {trader_name}")
st.sidebar.write(f"**ID:** `{trader_id[:8]}...`")
st.sidebar.markdown("---")

# Available symbols
SYMBOLS = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "JPM", "BAC", "WMT"]

# Symbol price ranges (for reference)
PRICE_RANGES = {
    "AAPL": (150.0, 200.0),
    "GOOGL": (130.0, 180.0),
    "MSFT": (350.0, 450.0),
    "TSLA": (200.0, 300.0),
    "AMZN": (140.0, 180.0),
    "META": (300.0, 400.0),
    "NVDA": (450.0, 550.0),
    "JPM": (140.0, 180.0),
    "BAC": (30.0, 45.0),
    "WMT": (150.0, 180.0),
}

# Order form
st.header("🎯 Order Details")

col1, col2 = st.columns(2)

with col1:
    symbol = st.selectbox(
        "Symbol",
        SYMBOLS,
        help="Select the trading symbol",
    )

    # Show price range for selected symbol
    if symbol in PRICE_RANGES:
        min_price, max_price = PRICE_RANGES[symbol]
        st.caption(f"💡 Typical range: ${min_price:.2f} - ${max_price:.2f}")

    side = st.radio(
        "Side",
        ["buy", "sell"],
        horizontal=True,
        help="Buy or sell order",
    )

with col2:
    quantity = st.number_input(
        "Quantity",
        min_value=1,
        max_value=10000,
        value=100,
        step=10,
        help="Number of shares to trade",
    )

    price = st.number_input(
        "Price ($)",
        min_value=0.01,
        max_value=10000.0,
        value=150.0,
        step=0.01,
        format="%.2f",
        help="Limit price per share",
    )

order_type = st.selectbox(
    "Order Type",
    ["limit", "market"],
    help="Limit orders execute at specified price, market orders execute at best available price",
)

# Order summary
st.markdown("### 📋 Order Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.metric("Action", side.upper())
    st.metric("Symbol", symbol)

with summary_col2:
    st.metric("Quantity", f"{quantity:,}")
    st.metric("Price", f"${price:.2f}")

with summary_col3:
    total_value = quantity * price
    st.metric("Total Value", f"${total_value:,.2f}")
    st.metric("Type", order_type.capitalize())

# Submit button
st.markdown("---")

col1, col2, col3 = st.columns([2, 1, 2])

with col2:
    submit_button = st.button(
        f"🚀 Submit {side.upper()} Order",
        type="primary",
        use_container_width=True,
    )

if submit_button:
    with st.spinner("Sending order to Trading Engine..."):
        # Add small delay for UX
        time.sleep(0.5)

        result = send_order_to_tes(
            symbol=symbol,
            side=side,
            quantity=float(quantity),
            price=float(price),
            order_type=order_type,
        )

        if result["success"]:
            st.success("✅ Order submitted successfully!")

            # Show response details
            response_data = result.get("data", {})

            st.markdown("#### 📨 Order Confirmation")
            conf_col1, conf_col2 = st.columns(2)

            with conf_col1:
                st.json(
                    {
                        "order": {
                            "symbol": symbol,
                            "side": side,
                            "quantity": quantity,
                            "price": price,
                            "type": order_type,
                        }
                    }
                )

            with conf_col2:
                st.json({"response": response_data})

            # Option to place another order
            if st.button("📝 Place Another Order"):
                st.rerun()

        else:
            st.error(f"❌ Order failed: {result.get('error', 'Unknown error')}")
            st.warning("Please check that the Trading Engine Server (TES) is running.")

# Tips section
with st.expander("💡 Trading Tips"):
    st.markdown(
        """
    ### Order Types

    - **Limit Order**: Executes at specified price or better
    - **Market Order**: Executes immediately at best available price

    ### Best Practices

    1. Check the typical price range before placing orders
    2. Start with smaller quantities when testing
    3. Monitor your positions in the Portfolio page
    4. Review trade history for performance analytics

    ### Order Flow

    1. Your order is sent to **TES** (Trading Engine Server)
    2. TES validates and routes to **OBS** (Order Book Server)
    3. OBS matches your order with counter-orders
    4. Trades are recorded in the database
    5. Your portfolio is updated automatically
    """
    )

# Footer
st.markdown("---")
st.caption(f"Trader: {trader_name} ({trader_id[:16]}...)")
