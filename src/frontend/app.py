import streamlit as st
import sqlite3
from pathlib import Path
import pandas as pd

def get_db_connection():
    db_path = Path(__file__).parent.parent / 'database' / 'trading_engine.db'
    conn = sqlite3.connect(db_path)
    return conn

def load_table(table_name):
    conn = get_db_connection()
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)
    conn.close()
    return df

st.title('Trading Engine Dashboard')

st.header('Users')
users_df = load_table('users')
st.dataframe(users_df)

st.header('Orders')
orders_df = load_table('orders')
st.dataframe(orders_df)

st.header('Trades')
trades_df = load_table('trades')
st.dataframe(trades_df)
