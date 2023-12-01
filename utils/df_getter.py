import streamlit as st
import pandas as pd

def get_df():
    # Initialize connection.
    conn = st.experimental_connection("postgresql", type="sql")

    # Perform query.
    df = pd.DataFrame(conn.query("SELECT * FROM power_cons ;", ttl="10m"))
    return df