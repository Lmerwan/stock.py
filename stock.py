# Import required libraries
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import math
from pathlib import Path
from datetime import date, timedelta, datetime
import streamlit as st
import yfinance as yf
import requests
from PIL import Image

# Set Streamlit page configuration
st.set_page_config(
    page_title="Stock Price App",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for improved styling
def apply_custom_css():
    st.markdown("""
        <style>
        .header {
            background-color: #1f4e79;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            color: white;
            font-size: 36px;
            margin: 0;
        }
        .image-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 20px 0;
        }
        .image-container img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_custom_css()

# Render header
def render_header(title):
    st.markdown(f"""
        <div class="header">
            <h1>{title}</h1>
        </div>
    """, unsafe_allow_html=True)

render_header("📈 S&P 500 Stock Analysis")

# Add responsive banner image
def display_image(image_path, caption, height=200):
    try:
        img = Image.open(image_path)
        img_resized = img.resize((1200, height))  # Resize for consistent dimensions
        st.image(img_resized, caption=caption, use_column_width=True)
    except Exception as e:
        st.error(f"Error loading image: {e}")

# Display banner image below the header
display_image(
    "stock-photo-american-financial-market-index-s-and-p-ticker-spx-on-blue-finance-background-from-numbers-2331803611.jpg",
    "Financial Insights at Your Fingertips"
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

    # Display a large home image
    display_image(
        "tyler-prahm-lmV3gJSAgbo-unsplash.jpg",
        "Dynamic Market Trends",
        height=300
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
    st.write("Compare the performance of multiple stocks over a selected date range.")
    comparison_image_url = "https://cdn.pixabay.com/photo/2018/01/31/07/15/chart-3120463_1280.jpg"

    # Fetch and resize image dynamically
    try:
        response = requests.get(comparison_image_url, stream=True)
        img = Image.open(response.raw)
        display_image("comparison_image.jpg", "Compare Performance Across Stocks")
    except Exception as e:
        st.error(f"Error loading comparison image: {e}")

# Footer
render_footer()
