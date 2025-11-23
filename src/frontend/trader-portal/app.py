"""Trader Portal - Frontend for client traders to execute trades and view analytics."""
import streamlit as st
import sqlite3
from pathlib import Path
import pandas as pd


def get_db_connection():
    """Get database connection."""
    db_path = Path(__file__).parent.parent.parent / 'database' / 'transactional' / 'trading_engine.db'
    conn = sqlite3.connect(db_path)
    return conn


def load_table(table_name):
    """Load table data."""
    conn = get_db_connection()
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)
    conn.close()
    return df


st.set_page_config(page_title="Trader Portal", layout="wide")

st.title('🏦 Trading Engine - Trader Portal')

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Dashboard", "Order Entry", "Positions", "Analytics"])

if page == "Dashboard":
    st.header('📊 Dashboard')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('Recent Orders')
        try:
            orders_df = load_table('orders')
            st.dataframe(orders_df.tail(10), use_container_width=True)
        except Exception as e:
            st.error(f"Error loading orders: {e}")
    
    with col2:
        st.subheader('Recent Trades')
        try:
            trades_df = load_table('trades')
            st.dataframe(trades_df.tail(10), use_container_width=True)
        except Exception as e:
            st.error(f"Error loading trades: {e}")

elif page == "Order Entry":
    st.header('📝 Order Entry')
    
    with st.form("order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Symbol", "AAPL")
            side = st.selectbox("Side", ["buy", "sell"])
            quantity = st.number_input("Quantity", min_value=1, value=100)
        
        with col2:
            price = st.number_input("Price", min_value=0.01, value=100.0, step=0.01)
            order_type = st.selectbox("Order Type", ["limit", "market"])
        
        submitted = st.form_submit_button("Submit Order")
        
        if submitted:
            st.success(f"Order submitted: {side.upper()} {quantity} {symbol} @ ${price}")
            # TODO: Connect to TES API

elif page == "Positions":
    st.header('💼 Positions')
    
    try:
        # TODO: Load positions from database
        st.info("Positions view coming soon...")
    except Exception as e:
        st.error(f"Error loading positions: {e}")

elif page == "Analytics":
    st.header('📈 Analytics')
    
    tab1, tab2 = st.tabs(["Performance", "Trade History"])
    
    with tab1:
        st.subheader("Performance Metrics")
        # TODO: Add performance metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Trades", "0")
        col2.metric("P&L", "$0.00")
        col3.metric("Win Rate", "0%")
    
    with tab2:
        st.subheader("Trade History")
        try:
            trades_df = load_table('trades')
            st.dataframe(trades_df, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading trades: {e}")
