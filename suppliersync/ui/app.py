
import sqlite3, os, pandas as pd, streamlit as st

st.title("SupplierSync — Agentic Orchestrator")
db_path = os.getenv("SQLITE_PATH", "suppliersync.db")
conn = sqlite3.connect(db_path)

st.subheader("Catalog")
st.dataframe(pd.read_sql_query("SELECT * FROM products", conn))

st.subheader("Recent Price Events")
st.dataframe(pd.read_sql_query("SELECT * FROM price_events ORDER BY id DESC LIMIT 50", conn))

st.subheader("CX Actions/Events")
st.dataframe(pd.read_sql_query("SELECT * FROM cx_events ORDER BY id DESC LIMIT 50", conn))
