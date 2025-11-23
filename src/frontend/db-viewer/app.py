"""
Database Viewer - Home page
Lightweight multipage app for viewing database schemas and data
"""

import sqlite3
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Database Viewer",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🗄️ Trading Engine Database Viewer")
st.markdown("### Explore database schemas, tables, and data")

# Get database path
DB_PATH = Path(__file__).parent.parent.parent / "database" / "transactional" / "trading_engine.db"

# Check if database exists
if not DB_PATH.exists():
    st.error(f"❌ Database not found at: {DB_PATH}")
    st.info("💡 Run `python main.py init-mock-data` to initialize the database")
    st.stop()

st.success(f"✅ Connected to database: `{DB_PATH.name}`")

# Get database info
try:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    # Display overview
    st.markdown("---")
    st.subheader("📊 Database Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Tables", len(tables))

    with col2:
        # Get total rows across all tables
        total_rows = 0
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_rows += cursor.fetchone()[0]
            except sqlite3.Error:
                # Skip tables that can't be queried
                pass
        st.metric("Total Records", f"{total_rows:,}")

    with col3:
        # Get database size
        db_size = DB_PATH.stat().st_size / 1024  # KB
        st.metric("Database Size", f"{db_size:.1f} KB")

    # Tables list
    st.markdown("---")
    st.subheader("📋 Tables")

    for table in tables:
        with st.expander(f"**{table}**"):
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]

            # Get schema
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            col1, col2 = st.columns([1, 3])

            with col1:
                st.metric("Rows", f"{row_count:,}")

            with col2:
                st.markdown("**Columns:**")
                for col in columns:
                    col_name, col_type = col[1], col[2]
                    pk = "🔑 " if col[5] else ""
                    not_null = "⚠️ NOT NULL" if col[3] else ""
                    st.text(f"{pk}{col_name}: {col_type} {not_null}")

    conn.close()

    # Quick navigation
    st.markdown("---")
    st.markdown("### 📑 Navigation")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📊 View Schemas", use_container_width=True):
            st.switch_page("pages/1_📊_Schemas.py")

    with col2:
        if st.button("📋 Browse Tables", use_container_width=True):
            st.switch_page("pages/2_📋_Tables.py")

    with col3:
        if st.button("🔍 Query Builder", use_container_width=True):
            st.switch_page("pages/3_🔍_Query.py")

    with col4:
        if st.button("📈 Statistics", use_container_width=True):
            st.switch_page("pages/4_📈_Stats.py")

except Exception as e:
    st.error(f"❌ Error connecting to database: {e}")

# Footer
st.markdown("---")
st.caption(f"Database: {DB_PATH}")
