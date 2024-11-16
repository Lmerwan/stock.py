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
# Tab: Stock Analysis
# Tab: Stock Analysis
with tabs[1]:
    st.header("Stock Analysis")
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
                show_vwap = st.checkbox("Show VWAP")
                show_stochastic = st.checkbox("Show Stochastic Oscillator")

                # Plot indicators
                st.subheader(f"{ticker_symbol} Price Chart with Indicators")
                fig = go.Figure()

                # Add Close Price
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name="Close Price"))

                # SMA (Short and Long)
                if show_sma_short:
                    sma_short_period = st.slider("SMA (Short) Period", 5, 50, 20)
                    data['SMA_Short'] = data['Close'].rolling(window=sma_short_period).mean()
                    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_Short'], mode='lines', name="SMA (Short)"))

                if show_sma_long:
                    sma_long_period = st.slider("SMA (Long) Period", 50, 200, 100)
                    data['SMA_Long'] = data['Close'].rolling(window=sma_long_period).mean()
                    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_Long'], mode='lines', name="SMA (Long)"))

                # EMA
                if show_ema:
                    ema_period = st.slider("EMA Period", 5, 100, 20)
                    data['EMA'] = data['Close'].ewm(span=ema_period, adjust=False).mean()
                    fig.add_trace(go.Scatter(x=data.index, y=data['EMA'], mode='lines', name="EMA"))

                # RSI
                if show_rsi:
                    rsi_period = st.slider("RSI Period", 5, 50, 14)
                    delta = data['Close'].diff()
                    gain = delta.where(delta > 0, 0)
                    loss = -delta.where(delta < 0, 0)
                    avg_gain = gain.rolling(window=rsi_period).mean()
                    avg_loss = loss.rolling(window=rsi_period).mean()
                    rs = avg_gain / avg_loss
                    data['RSI'] = 100 - (100 / (1 + rs))
                    st.line_chart(data['RSI'])

                # MACD
                if show_macd:
                    short_ema = data['Close'].ewm(span=12, adjust=False).mean()
                    long_ema = data['Close'].ewm(span=26, adjust=False).mean()
                    data['MACD'] = short_ema - long_ema
                    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
                    fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name="MACD"))
                    fig.add_trace(go.Scatter(x=data.index, y=data['Signal'], mode='lines', name="MACD Signal"))

                # VWAP
                if show_vwap:
                    data['VWAP'] = (data['Volume'] * (data['High'] + data['Low'] + data['Close']) / 3).cumsum() / data['Volume'].cumsum()
                    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], mode='lines', name="VWAP"))

                # Stochastic Oscillator
                if show_stochastic:
                    low_min = data['Low'].rolling(window=14).min()
                    high_max = data['High'].rolling(window=14).max()
                    data['%K'] = (data['Close'] - low_min) * 100 / (high_max - low_min)
                    data['%D'] = data['%K'].rolling(window=3).mean()
                    fig.add_trace(go.Scatter(x=data.index, y=data['%K'], mode='lines', name="Stochastic %K"))
                    fig.add_trace(go.Scatter(x=data.index, y=data['%D'], mode='lines', name="Stochastic %D"))

                # Update figure layout
                fig.update_layout(
                    title=f"{ticker_symbol} Price Chart",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    xaxis_rangeslider_visible=True
                )
                st.plotly_chart(fig)

            except Exception as e:
                st.error(f"Error fetching data for {ticker_symbol}: {e}")

# Tab: Stock Comparison
with tabs[2]:
    st.header("Stock Comparison")
    st.write("This is the Visualization page. Show your plots here.")
    import matplotlib.pyplot as plt
    import numpy as np
    from datetime import date, timedelta
    import yfinance as yf
    import pandas as pd
    # Title for date and stock selection
    st.title('Select Date and Stocks')
    # Date range selection
    today = date.today()
    min_date = today - timedelta(days=365 * 5)
    max_date = today
    date_range = st.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(today - timedelta(days=365), today)
    )
    sdate, edate = date_range
    # Stock selection
    symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]
    selected_stocks = st.multiselect(
        "Select Stocks", symbols, default=["AAPL"]
    )
    # Stock comparison
    st.title("Stock Comparison")
    if selected_stocks:
        # Fetch stock data
        data = yf.download(
            selected_stocks,
            start=sdate,
            end=edate,
            interval="1d",
            auto_adjust=True,
            prepost=True
        )
        if data.empty:
            st.error("Failed to fetch historical data or no data available for the selected period.")
        else:
            # Filter data for the selected date range
            filtered_data = data['Close'][selected_stocks]
            sdate_utc = pd.to_datetime(sdate).tz_localize('UTC')
            edate_utc = pd.to_datetime(edate).tz_localize('UTC')
            filtered_data = filtered_data[(filtered_data.index >= sdate_utc) & (filtered_data.index <= edate_utc)]
            if not filtered_data.empty:
                # Reset index to create a 'Date' column
                filtered_data = filtered_data.reset_index()
                filtered_data = filtered_data.rename(columns={'index': 'Date'})
                # Plot the data
                st.line_chart(
                    filtered_data,
                    x="Date",
                    y=selected_stocks[0] if len(selected_stocks) == 1 else selected_stocks
                )
            else:
                st.warning("No data available for the selected stock(s) and date range.")
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

