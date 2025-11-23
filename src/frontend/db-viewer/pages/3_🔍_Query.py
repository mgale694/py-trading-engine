"""
Query Builder Page - Run custom SQL queries
"""

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Query Builder", page_icon="🔍", layout="wide")

st.title("🔍 SQL Query Builder")

# Get database path
DB_PATH = (
    Path(__file__).parent.parent.parent.parent / "database" / "transactional" / "trading_engine.db"
)

if not DB_PATH.exists():
    st.error("❌ Database not found")
    st.stop()

# Safety warning
st.warning(
    "⚠️ **Read-Only Mode**: Only SELECT queries are allowed for safety. "
    "INSERT, UPDATE, DELETE operations are disabled."
)

try:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Get all tables for reference
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    # Sidebar: Show available tables
    st.sidebar.markdown("### 📋 Available Tables")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        st.sidebar.text(f"• {table} ({count} rows)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 Common Queries")

    # Predefined queries
    query_templates = {
        "All Orders": "SELECT * FROM orders LIMIT 100",
        "All Trades": "SELECT * FROM trades LIMIT 100",
        "All Users": "SELECT * FROM users",
        "Open Orders": "SELECT * FROM orders WHERE status = 'open' LIMIT 100",
        "Recent Trades": "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 50",
        "Orders by Symbol": "SELECT symbol, COUNT(*) as count, SUM(quantity) as total_qty FROM orders GROUP BY symbol",
        "Trades by Symbol": "SELECT symbol, COUNT(*) as count, SUM(quantity) as total_qty FROM trades GROUP BY symbol",
        "Portfolio Summary": """
            SELECT
                p.name,
                pos.symbol,
                pos.quantity,
                pos.avg_price,
                pos.quantity * pos.avg_price as total_value
            FROM portfolios p
            JOIN positions pos ON p.id = pos.portfolio_id
        """,
    }

    selected_template = st.sidebar.selectbox(
        "Quick Query Templates", ["Custom"] + list(query_templates.keys())
    )

    # Query input
    if selected_template == "Custom":
        default_query = "SELECT * FROM orders LIMIT 10"
    else:
        default_query = query_templates[selected_template]

    query = st.text_area(
        "Enter SQL Query",
        value=default_query,
        height=150,
        help="Only SELECT queries are allowed",
    )

    col1, col2 = st.columns([1, 5])

    with col1:
        execute_btn = st.button("▶️ Execute Query", type="primary", use_container_width=True)

    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.rerun()

    if execute_btn:
        # Safety check: only allow SELECT queries
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            st.error("❌ Only SELECT queries are allowed for safety")
        elif any(
            keyword in query_upper
            for keyword in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]
        ):
            st.error("❌ Modifying queries are not allowed")
        else:
            try:
                # Execute query
                cursor.execute(query)
                results = cursor.fetchall()

                if results:
                    # Get column names
                    col_names = [desc[0] for desc in cursor.description]
                    df = pd.DataFrame(results, columns=col_names)

                    # Display results
                    st.success(f"✅ Query executed successfully! {len(df)} rows returned")

                    # Stats
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Rows", len(df))

                    with col2:
                        st.metric("Columns", len(col_names))

                    with col3:
                        # Estimate memory
                        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
                        st.metric("Memory", f"{memory_mb:.2f} MB")

                    # Display data
                    st.markdown("---")
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    # Export options
                    st.markdown("---")
                    col1, col2 = st.columns(2)

                    with col1:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv",
                        )

                    with col2:
                        json_str = df.to_json(orient="records", indent=2)
                        st.download_button(
                            label="📥 Download as JSON",
                            data=json_str,
                            file_name="query_results.json",
                            mime="application/json",
                        )

                else:
                    st.info("Query executed successfully but returned no results")

            except Exception as e:
                st.error(f"❌ Query error: {e}")

    # Query tips
    with st.expander("💡 SQL Query Tips"):
        st.markdown(
            """
        ### Basic Query Structure
        ```sql
        SELECT column1, column2 FROM table_name WHERE condition LIMIT 100
        ```

        ### Useful Patterns
        - **Filter by date**: `WHERE created_at > '2024-01-01'`
        - **Count records**: `SELECT COUNT(*) FROM table_name`
        - **Group by**: `SELECT column, COUNT(*) FROM table GROUP BY column`
        - **Order results**: `ORDER BY column_name DESC`
        - **Limit results**: `LIMIT 100`

        ### Join Example
        ```sql
        SELECT o.*, u.username
        FROM orders o
        JOIN users u ON o.user_id = u.id
        LIMIT 50
        ```
        """
        )

    conn.close()

except Exception as e:
    st.error(f"❌ Error: {e}")

# Footer
st.markdown("---")
st.caption(f"Database: {DB_PATH.name}")
