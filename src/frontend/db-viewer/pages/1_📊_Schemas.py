"""
Schemas Page - View detailed table schemas
"""

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Database Schemas", page_icon="📊", layout="wide")

st.title("📊 Database Schemas")

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
    selected_table = st.selectbox("Select a table", tables)

    if selected_table:
        st.markdown(f"### Table: `{selected_table}`")

        # Get full CREATE statement
        cursor.execute(
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{selected_table}'"
        )
        create_sql = cursor.fetchone()[0]

        st.markdown("#### 📝 CREATE Statement")
        st.code(create_sql, language="sql")

        # Get table info
        cursor.execute(f"PRAGMA table_info({selected_table})")
        columns_info = cursor.fetchall()

        # Format as DataFrame
        df = pd.DataFrame(
            columns_info,
            columns=["cid", "name", "type", "notnull", "dflt_value", "pk"],
        )

        # Add readable columns
        df["Primary Key"] = df["pk"].apply(lambda x: "✓" if x else "")
        df["Not Null"] = df["notnull"].apply(lambda x: "✓" if x else "")
        df["Default"] = df["dflt_value"].apply(lambda x: x if x else "")

        st.markdown("#### 📋 Column Details")
        st.dataframe(
            df[["name", "type", "Primary Key", "Not Null", "Default"]],
            use_container_width=True,
            hide_index=True,
        )

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {selected_table}")
        row_count = cursor.fetchone()[0]

        # Get indexes
        cursor.execute(f"PRAGMA index_list({selected_table})")
        indexes = cursor.fetchall()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Columns", len(columns_info))

        with col2:
            st.metric("Total Rows", f"{row_count:,}")

        with col3:
            st.metric("Indexes", len(indexes))

        # Show indexes if any
        if indexes:
            st.markdown("#### 🔍 Indexes")
            for idx in indexes:
                idx_name = idx[1]
                cursor.execute(f"PRAGMA index_info({idx_name})")
                idx_cols = cursor.fetchall()
                cols_list = ", ".join([col[2] for col in idx_cols])
                st.text(f"• {idx_name}: ({cols_list})")

        # Foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({selected_table})")
        fks = cursor.fetchall()

        if fks:
            st.markdown("#### 🔗 Foreign Keys")
            for fk in fks:
                st.text(f"• {fk[3]} → {fk[2]}({fk[4]})")

        # Sample data
        st.markdown("#### 👀 Sample Data (First 10 rows)")
        cursor.execute(f"SELECT * FROM {selected_table} LIMIT 10")
        sample_data = cursor.fetchall()

        if sample_data:
            col_names = [desc[0] for desc in cursor.description]
            sample_df = pd.DataFrame(sample_data, columns=col_names)
            st.dataframe(sample_df, use_container_width=True, hide_index=True)
        else:
            st.info("No data in this table yet")

    conn.close()

except Exception as e:
    st.error(f"❌ Error: {e}")

# Footer
st.markdown("---")
st.caption(f"Database: {DB_PATH.name}")
