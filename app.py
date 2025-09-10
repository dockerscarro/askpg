import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Sample Streamlit App", layout="centered")

# Title
st.title("📊 Sample Streamlit App")

# Sidebar
st.sidebar.header("Controls")
rows = st.sidebar.slider("Number of rows", min_value=5, max_value=50, value=10)

# Generate random data
df = pd.DataFrame({
    "A": np.random.randn(rows),
    "B": np.random.rand(rows),
    "C": np.random.randint(1, 100, rows)
})

# Show dataframe
st.subheader("Random Data")
st.dataframe(df)

# Summary stats
st.subheader("Summary Statistics")
st.write(df.describe())

# Simple chart
st.subheader("Line Chart of Column A")
st.line_chart(df["A"])

# User input example
name = st.text_input("Enter your name", "")
if name:
    st.success(f"Hello, {name}! 👋 Welcome to the sample app.")
