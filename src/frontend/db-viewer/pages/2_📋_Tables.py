"""
Tables Page - Browse and filter table data
"""

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Browse Tables", page_icon="📋", layout="wide")

st.title("📋 Browse Tables")

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

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    # Table selector
    selected_table = st.selectbox("Select a table to browse", tables)

    if selected_table:
        st.markdown(f"### Table: `{selected_table}`")

        # Get column names
        cursor.execute(f"PRAGMA table_info({selected_table})")
        columns_info = cursor.fetchall()
        all_columns = [col[1] for col in columns_info]

        # Filters in sidebar
        st.sidebar.markdown("### 🔧 Filters")

        # Row limit
        limit = st.sidebar.slider(
            "Number of rows", min_value=10, max_value=1000, value=100, step=10
        )

        # Column selector
        selected_columns = st.sidebar.multiselect(
            "Select columns to display",
            options=all_columns,
            default=all_columns,
        )

        # Build query
        cols_str = ", ".join(selected_columns) if selected_columns else "*"
        query = f"SELECT {cols_str} FROM {selected_table}"

        # Get available columns for filtering
        if st.sidebar.checkbox("Add WHERE clause"):
            filter_col = st.sidebar.selectbox("Column", all_columns)
            filter_op = st.sidebar.selectbox("Operator", ["=", "!=", ">", "<", ">=", "<=", "LIKE"])
            filter_val = st.sidebar.text_input("Value")

            if filter_val:
                if filter_op == "LIKE":
                    query += f" WHERE {filter_col} LIKE '%{filter_val}%'"
                else:
                    query += f" WHERE {filter_col} {filter_op} '{filter_val}'"

        # Ordering
        order_by = st.sidebar.selectbox("Order by", ["None"] + all_columns)
        if order_by != "None":
            order_dir = st.sidebar.radio("Direction", ["ASC", "DESC"])
            query += f" ORDER BY {order_by} {order_dir}"

        query += f" LIMIT {limit}"

        # Display query
        with st.expander("📝 SQL Query"):
            st.code(query, language="sql")

        # Execute query
        try:
            cursor.execute(query)
            data = cursor.fetchall()

            if data:
                col_names = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(data, columns=col_names)

                # Show stats
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Rows Displayed", len(df))

                with col2:
                    cursor.execute(f"SELECT COUNT(*) FROM {selected_table}")
                    total_rows = cursor.fetchone()[0]
                    st.metric("Total Rows", total_rows)

                with col3:
                    st.metric("Columns", len(col_names))

                # Display data
                st.markdown("---")
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Export options
                st.markdown("---")
                col1, col2 = st.columns(2)

                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"{selected_table}.csv",
                        mime="text/csv",
                    )

                with col2:
                    json_str = df.to_json(orient="records", indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"{selected_table}.json",
                        mime="application/json",
                    )

            else:
                st.info("No data found with current filters")

        except Exception as e:
            st.error(f"❌ Query error: {e}")

    conn.close()

except Exception as e:
    st.error(f"❌ Error: {e}")

# Footer
st.markdown("---")
st.caption(f"Database: {DB_PATH.name}")
