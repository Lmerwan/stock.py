# Import required libraries
import seaborn as sns
import matplotlib.pyplot as plt
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
    page_icon="📈",
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
render_header("📈 S&P 500 Stock Analysis")

# Add a banner image for the app
st.image(
    "https://cdn.pixabay.com/photo/2015/07/17/22/43/student-849828_1280.jpg",
    caption="Financial Insights at Your Fingertips",
    use_column_width=True
)

# Create tabs
tabs = st.tabs(["🏠 Home", "📊 Stock Analysis", "📈 Stock Comparison", "📰 Stock News", "📞 Contacts"])

# Tab: Home
with tabs[0]:
    st.header("Welcome to the Stock Analysis App")
    st.write("""
    Explore stock trends, compare performances, and stay updated with the latest financial news. This app provides a comprehensive 
    suite of tools for analyzing S&P 500 stocks and making informed decisions.
    """)

    # Use the image URL directly
    st.image(
        "tyler-prahm-lmV3gJSAgbo-unsplash.jpg",
        caption="Dynamic Market Trends",
        use_column_width=True
    )

# Tab: Stock Analysis
with tabs[1]:
    st.header("📊 Stock Analysis")
    ticker_symbol = st.text_input("Enter stock ticker (e.g., AAPL, MSFT):", "AAPL", key="ticker")
    start_date = st.date_input("Start Date", value=date(2022, 1, 1))
    end_date = st.date_input("End Date", value=date.today())

    if start_date > end_date:
        st.error("End date must be after the start date.")
    else:
        if ticker_symbol:
            try:
                # Fetch stock data
                stock = yf.Ticker(ticker_symbol)
                data = stock.history(start=start_date, end=end_date)

                # Display current price
                st.subheader(f"Current Price: {data['Close'].iloc[-1]:.2f} USD")

                # Indicator Selection
                st.subheader("Select Indicators")
                show_sma_short = st.checkbox("Show SMA (Short)")
                show_sma_long = st.checkbox("Show SMA (Long)")
                show_ema = st.checkbox("Show EMA")
                show_rsi = st.checkbox("Show RSI")
                show_macd = st.checkbox("Show MACD")

                # Analysis Button
                if st.button("Analyze"):
                    # Initialize a Seaborn plot
                    plt.figure(figsize=(12, 6))
                    sns.set_style("whitegrid")

                    # Plot the close prices
                    sns.lineplot(data=data, x=data.index, y="Close", label="Close Price", color="blue")

                    # Add indicators to the plot
                    if show_sma_short:
                        sma_short_period = st.slider("SMA (Short) Period", 5, 50, 20)
                        data['SMA_Short'] = data['Close'].rolling(window=sma_short_period).mean()
                        sns.lineplot(data=data, x=data.index, y="SMA_Short", label=f"SMA (Short, {sma_short_period})")

                    if show_sma_long:
                        sma_long_period = st.slider("SMA (Long) Period", 50, 200, 100)
                        data['SMA_Long'] = data['Close'].rolling(window=sma_long_period).mean()
                        sns.lineplot(data=data, x=data.index, y="SMA_Long", label=f"SMA (Long, {sma_long_period})")

                    if show_ema:
                        ema_period = st.slider("EMA Period", 5, 100, 20)
                        data['EMA'] = data['Close'].ewm(span=ema_period, adjust=False).mean()
                        sns.lineplot(data=data, x=data.index, y="EMA", label=f"EMA ({ema_period})")

                    if show_rsi:
                        rsi_period = st.slider("RSI Period", 5, 50, 14)
                        delta = data['Close'].diff()
                        gain = delta.where(delta > 0, 0)
                        loss = -delta.where(delta < 0, 0)
                        avg_gain = gain.rolling(window=rsi_period).mean()
                        avg_loss = loss.rolling(window=rsi_period).mean()
                        rs = avg_gain / avg_loss
                        data['RSI'] = 100 - (100 / (1 + rs))
                        st.line_chart(data['RSI'], height=250)

                    if show_macd:
                        short_ema = data['Close'].ewm(span=12, adjust=False).mean()
                        long_ema = data['Close'].ewm(span=26, adjust=False).mean()
                        data['MACD'] = short_ema - long_ema
                        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
                        sns.lineplot(data=data, x=data.index, y="MACD", label="MACD")
                        sns.lineplot(data=data, x=data.index, y="Signal", label="Signal Line")

                    # Customize the plot
                    plt.title(f"{ticker_symbol} Price Chart with Indicators", fontsize=16)
                    plt.xlabel("Date", fontsize=12)
                    plt.ylabel("Price (USD)", fontsize=12)
                    plt.legend(loc="upper left")
                    st.pyplot(plt)

            except Exception as e:
                st.error(f"Error fetching data for {ticker_symbol}: {e}")

# Tab: Stock Comparison
with tabs[2]:
    st.header("📈 Stock Comparison")
    st.write("""
    Compare the performance of multiple stocks over a selected date range.
    """)
    st.image("https://cdn.pixabay.com/photo/2018/01/31/07/15/chart-3120463_1280.jpg", caption="Compare Performance Across Stocks")

    symbols = st.multiselect("Select Stocks (e.g., AAPL, MSFT, GOOG)", ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"], default=["AAPL", "MSFT"])
    date_range = st.slider("Select Date Range", min_value=date.today() - timedelta(days=1825), max_value=date.today(), value=(date.today() - timedelta(days=365), date.today()))

    if symbols:
        try:
            data = yf.download(symbols, start=date_range[0], end=date_range[1], auto_adjust=True)
            plt.figure(figsize=(14, 7))
            for symbol in symbols:
                sns.lineplot(data=data['Close'][symbol], label=symbol)
            plt.title("Stock Comparison", fontsize=16)
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Price (USD)", fontsize=12)
            plt.legend(loc="upper left")
            st.pyplot(plt)
        except Exception as e:
            st.error(f"Error fetching comparison data: {e}")

# Tab: Stock News
with tabs[3]:
    st.header("📰 Stock News")
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
    st.header("📞 Contact Us")
    st.write("We'd love to hear from you! Please share your feedback.")
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
