import streamlit as st
import sqlite3
import pandas as pd

st.title("📊 Resume Relevance Checker Dashboard")

conn = sqlite3.connect("../backend/results.db")
df = pd.read_sql_query("SELECT * FROM evaluations", conn)
conn.close()

st.dataframe(df)
