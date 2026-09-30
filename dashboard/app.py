import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Pipeline Dashboard", layout="wide")
st.title("Web Scraping Pipeline Dashboard")

tab1, tab2 = st.tabs(["Books", "Jobs"])

with tab1:
    st.header("Current Books")
    books = requests.get(f"{API_URL}/books", params={"limit": 100}).json()
    df_books = pd.DataFrame(books)
    st.dataframe(df_books[["title", "price", "availability", "rating"]])

    st.subheader("Price History Lookup")
    book_url = st.selectbox("Select a book", df_books["book_url"].unique())
    if book_url:
        history = requests.get(f"{API_URL}/books/{book_url}/history").json()
        df_history = pd.DataFrame(history)
        df_history["valid_from"] = pd.to_datetime(df_history["valid_from"])
        st.line_chart(df_history.set_index("valid_from")["price"])

with tab2:
    st.header("Current Jobs")
    jobs = requests.get(f"{API_URL}/jobs", params={} if False else None).json()
    df_jobs = pd.DataFrame(jobs)
    st.dataframe(df_jobs[["title", "company", "location", "posted_date"]])

    st.subheader("Jobs per Company")
    company_counts = df_jobs["company"].value_counts().head(10)
    st.bar_chart(company_counts)