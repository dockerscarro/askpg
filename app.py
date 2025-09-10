import streamlit as st
import pandas as pd
import numpy as np


# ---------------------------
# Utility functions
# ---------------------------
def generate_data(rows: int = 100) -> pd.DataFrame:
    """Generate random dataset with 3 columns."""
    np.random.seed(42)
    return pd.DataFrame({
        "Column A": np.random.randn(rows),
        "Column B": np.random.rand(rows),
        "Column C": np.random.randint(1, 100, rows)
    })


def filter_data(df: pd.DataFrame, min_value: int, max_value: int) -> pd.DataFrame:
    """Filter Column C by a range of values."""
    return df[(df["Column C"] >= min_value) & (df["Column C"] <= max_value)]


# ---------------------------
# Page functions
# ---------------------------
def show_dashboard(df: pd.DataFrame):
    st.header("Dashboard")

    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Mean of A", f"{df['Column A'].mean():.2f}")
    col2.metric("Mean of B", f"{df['Column B'].mean():.2f}")
    col3.metric("Median of C", f"{df['Column C'].median():.2f}")

    st.subheader("Line Chart of Column A")
    st.line_chart(df["Column A"])

    st.subheader("Bar Chart of Column C")
    st.bar_chart(df["Column C"])


def show_data_explorer(df: pd.DataFrame):
    st.header("Data Explorer")

    st.write("Adjust the filters to explore the dataset.")

    min_val = int(df["Column C"].min())
    max_val = int(df["Column C"].max())
    user_min, user_max = st.slider("Filter by Column C", min_val, max_val, (min_val, max_val))

    filtered_df = filter_data(df, user_min, user_max)
    st.write(f"Showing {len(filtered_df)} rows after filtering.")
    st.dataframe(filtered_df)


def show_statistics(df: pd.DataFrame):
    st.header("Statistics")

    st.subheader("Summary Table")
    st.write(df.describe())

    st.subheader("Histogram of Column A")
    st.bar_chart(np.histogram(df["Column A"], bins=20)[0])


def show_user_input():
    st.header("User Input")

    name = st.text_input("Enter your name")
    age = st.number_input("Enter your age", min_value=1, max_value=120, value=25)

    if st.button("Submit"):
        st.success(f"Hello {name}, you are {age} years old!")


# ---------------------------
# Main App
# ---------------------------
def main():
    st.set_page_config(page_title="Big Sample Streamlit App", layout="wide")
    st.title("Big Sample Streamlit App")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Data Explorer", "Statistics", "User Input"]
    )

    rows = st.sidebar.slider("Number of rows in dataset", 50, 500, 200, step=50)
    df = generate_data(rows)

    if page == "Dashboard":
        show_dashboard(df)
    elif page == "Data Explorer":
        show_data_explorer(df)
    elif page == "Statistics":
        show_statistics(df)
    elif page == "User Input":
        show_user_input()


if __name__ == "__main__":
    main()
