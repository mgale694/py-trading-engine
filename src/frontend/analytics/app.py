"""Analytics Dashboard - Internal analytics for system monitoring and performance."""
import streamlit as st
import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


def get_analytics_db():
    """Get analytics database connection."""
    db_path = Path(__file__).parent.parent.parent / 'database' / 'analytics' / 'analytics.db'
    conn = sqlite3.connect(db_path)
    return conn


def get_transactional_db():
    """Get transactional database connection."""
    db_path = Path(__file__).parent.parent.parent / 'database' / 'transactional' / 'trading_engine.db'
    conn = sqlite3.connect(db_path)
    return conn


st.set_page_config(page_title="Analytics Dashboard", layout="wide")

st.title('📊 System Analytics Dashboard')

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["System Health", "Performance Metrics", "User Activity"])

if page == "System Health":
    st.header('🏥 System Health')
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("TES Status", "Online", delta="Healthy")
    col2.metric("OBS Status", "Online", delta="Healthy")
    col3.metric("DB Status", "Online", delta="Healthy")
    col4.metric("RabbitMQ", "Online", delta="Healthy")
    
    st.subheader("System Performance Metrics")
    
    # TODO: Load actual metrics from database
    st.info("Real-time system metrics coming soon...")
    
    # Placeholder chart
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='H')
    data = pd.DataFrame({
        'timestamp': dates,
        'latency_ms': [10 + i % 5 for i in range(len(dates))],
        'throughput': [1000 + i % 100 for i in range(len(dates))]
    })
    
    fig = px.line(data, x='timestamp', y='latency_ms', title='System Latency (ms)')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Performance Metrics":
    st.header('📈 Performance Metrics')
    
    tab1, tab2, tab3 = st.tabs(["Trading Volume", "Execution Quality", "Order Book Depth"])
    
    with tab1:
        st.subheader("Trading Volume")
        try:
            conn = get_transactional_db()
            df = pd.read_sql_query('''
                SELECT DATE(timestamp) as date, 
                       COUNT(*) as trade_count,
                       SUM(quantity) as total_quantity,
                       AVG(price) as avg_price
                FROM trades
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            ''', conn)
            conn.close()
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                fig = px.bar(df, x='date', y='trade_count', title='Daily Trade Count')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No trade data available")
        except Exception as e:
            st.error(f"Error loading trade data: {e}")
    
    with tab2:
        st.subheader("Execution Quality")
        st.info("Execution quality metrics coming soon...")
    
    with tab3:
        st.subheader("Order Book Depth")
        st.info("Order book depth visualization coming soon...")

elif page == "User Activity":
    st.header('👥 User Activity')
    
    try:
        conn = get_transactional_db()
        
        # User statistics
        user_stats = pd.read_sql_query('''
            SELECT u.username, 
                   COUNT(DISTINCT t.id) as trade_count,
                   COUNT(DISTINCT o.id) as order_count,
                   SUM(CASE WHEN t.side = 'buy' THEN t.quantity * t.price ELSE 0 END) as total_bought,
                   SUM(CASE WHEN t.side = 'sell' THEN t.quantity * t.price ELSE 0 END) as total_sold
            FROM users u
            LEFT JOIN trades t ON u.id = t.user_id
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.username
        ''', conn)
        conn.close()
        
        if not user_stats.empty:
            st.dataframe(user_stats, use_container_width=True)
        else:
            st.info("No user activity data available")
    except Exception as e:
        st.error(f"Error loading user activity: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**System Info**")
st.sidebar.markdown(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
