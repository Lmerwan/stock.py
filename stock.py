# Import required packages
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import pandas as pd
import math
import sqlite3
from pathlib import Path
from datetime import date, timedelta, datetime
import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import feedparser

# Set the cache directory
import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"

# Page configuration
st.set_page_config(
    page_title="Stock Price App",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global Header
def render_header(title):
    st.markdown(f"""
    <div style="background-color:#1f4e79;padding:10px;border-radius:5px">
        <h1 style="color:white;text-align:center;">{title}</h1>
    </div>
    """, unsafe_allow_html=True)

# Global Footer
def render_footer():
    st.markdown("""
    ---
    <div style="text-align:center;">
        <small>© 2024 International University of Japan. All rights reserved.</small>
    </div>
    """, unsafe_allow_html=True)

# Page Title
render_header("S&P 500 Stock Analysis")

# Create tabs
tabs = st.tabs(["Home", "Stock Analysis", "Stock Comparison", "Stock News", "Contacts"])

# Tab: Home
with tabs[0]:
    st.header("Home")
    st.write("Welcome to the Stock Analysis web app. Stay informed and make data-driven decisions!")
    st.image("https://st3.depositphotos.com/3108485/32120/i/600/depositphotos_321205098-stock-photo-businessman-plan-graph-growth-and.jpg", caption="Today's Stock Insights")

# Tab: Stock Analysis
with tabs[1]:
    st.header("Stock Analysis")
    ticker_symbol = st.text_input("Enter stock ticker (e.g., AAPL, MSFT):", "AAPL", key="ticker")
    start_date = st.date_input("Start Date", value=date(2022, 1, 1))
    end_date = st.date_input("End Date", value=date.today())

    # Ensure valid date range
    if start_date > end_date:
        st.error("End date must be after the start date.")
    else:
        try:
            stock = yf.Ticker(ticker_symbol)
            data = stock.history(start=start_date, end=end_date)

            # Display current stock data
            current_price = data['Close'].iloc[-1]
            st.subheader(f"Current Price: {current_price:.2f} USD")

            # Simple Moving Average (SMA)
            sma_period = st.slider("SMA Period", 5, 100, 20)
            data['SMA'] = data['Close'].rolling(window=sma_period).mean()
            st.line_chart(data[['Close', 'SMA']])

        except Exception as e:
            st.error(f"Error fetching stock data: {e}")

# Tab: Stock Comparison
with tabs[2]:
    st.header("Stock Comparison")
    st.write("Compare the performance of different stocks over a selected date range.")
    symbols = st.multiselect("Select Stocks", ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"], default=["AAPL"])
    date_range = st.slider("Date Range", min_value=date.today() - timedelta(days=1825), max_value=date.today(), value=(date.today() - timedelta(days=365), date.today()))

    if symbols:
        try:
            data = yf.download(symbols, start=date_range[0], end=date_range[1], group_by="ticker")['Close']
            st.line_chart(data)
        except Exception as e:
            st.error(f"Error fetching stock comparison data: {e}")
    else:
        st.warning("Please select at least one stock.")

# Tab: Stock News
with tabs[3]:
    st.header("Stock News")
    ticker_symbol = st.text_input("Enter stock ticker for news (e.g., AAPL):", key="news_ticker")

    def extract_news_from_google_rss(ticker):
        url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        news_articles = []
        for entry in feed.entries[:10]:
            news_articles.append({"title": entry.title, "url": entry.link, "date": datetime(*entry.published_parsed[:6])})
        return news_articles

    if ticker_symbol:
        news = extract_news_from_google_rss(ticker_symbol)
        for article in news:
            st.write(f"**{article['title']}**")
            st.write(f"[Read more]({article['url']}) - {article['date'].strftime('%Y-%m-%d')}")

# Tab: Contacts
with tabs[4]:
    st.header("Contact Us")
    st.write("Share your feedback with us.")
    name = st.text_input("Name")
    email = st.text_input("Email")
    message = st.text_area("Message")
    if st.button("Submit"):
        if name and email and message:
            st.success("Thank you for your feedback!")
        else:
            st.error("All fields are required.")

# Footer
render_footer()
