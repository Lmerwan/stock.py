# Import required libraries
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date, timedelta, datetime
import streamlit as st
import yfinance as yf
import requests
from PIL import Image
import plotly.graph_objects as go
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

# Create tabs
tabs = st.tabs(["🏠 Home", "📊 Stock Analysis", "📈 Stock Comparison", "📰 Stock News", "📞 Contacts"])

# Tab: Home
with tabs[0]:
    st.header("Welcome to the Stock Analysis App")
    st.write("""
        Explore stock trends, compare performances, and stay updated with the latest financial news. This app provides a comprehensive 
        suite of tools for analyzing S&P 500 stocks and making informed decisions.
    """)

    # Display a home image
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

                # Display basic stock information
                st.subheader(f"Current Price: {data['Close'].iloc[-1]:.2f} USD")
                st.write(f"**Ticker:** {ticker_symbol.upper()}")
                st.write(f"**Data Range:** {start_date} to {end_date}")
                st.write(f"**Volume (Last Trading Day):** {data['Volume'].iloc[-1]}")

                # Show Candlestick Chart
                st.subheader("Candlestick Chart")
                fig = go.Figure(data=[go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    increasing_line_color='green',
                    decreasing_line_color='red',
                    name="Candlesticks"
                )])
                fig.update_layout(
                    title=f"{ticker_symbol.upper()} Candlestick Chart",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    xaxis_rangeslider_visible=False
                )
                st.plotly_chart(fig)

                # Show Indicators Button
                if st.button("Show Technical Indicators"):
                    st.subheader("Technical Indicators")
                    buy_signals = 0
                    sell_signals = 0

                    # Initialize a Seaborn figure
                    plt.figure(figsize=(14, 8))
                    sns.set_style("whitegrid")

                    # Plot Close Price
                    sns.lineplot(data=data, x=data.index, y="Close", label="Close Price", color="blue")

                    # SMA (Short and Long)
                    sma_short_period = st.slider("SMA (Short) Period", 5, 50, 20)
                    data['SMA_Short'] = data['Close'].rolling(window=sma_short_period).mean()
                    sns.lineplot(data=data, x=data.index, y="SMA_Short", label=f"SMA (Short, {sma_short_period})")
                    if data['Close'].iloc[-1] > data['SMA_Short'].iloc[-1]:
                        buy_signals += 1
                    else:
                        sell_signals += 1

                    sma_long_period = st.slider("SMA (Long) Period", 50, 200, 100)
                    data['SMA_Long'] = data['Close'].rolling(window=sma_long_period).mean()
                    sns.lineplot(data=data, x=data.index, y="SMA_Long", label=f"SMA (Long, {sma_long_period})")
                    if data['Close'].iloc[-1] > data['SMA_Long'].iloc[-1]:
                        buy_signals += 1
                    else:
                        sell_signals += 1

                    # EMA
                    ema_period = st.slider("EMA Period", 5, 100, 20)
                    data['EMA'] = data['Close'].ewm(span=ema_period, adjust=False).mean()
                    sns.lineplot(data=data, x=data.index, y="EMA", label=f"EMA ({ema_period})")
                    if data['Close'].iloc[-1] > data['EMA'].iloc[-1]:
                        buy_signals += 1
                    else:
                        sell_signals += 1

                    # RSI
                    rsi_period = st.slider("RSI Period", 5, 50, 14)
                    delta = data['Close'].diff()
                    gain = delta.where(delta > 0, 0)
                    loss = -delta.where(delta < 0, 0)
                    avg_gain = gain.rolling(window=rsi_period).mean()
                    avg_loss = loss.rolling(window=rsi_period).mean()
                    rs = avg_gain / avg_loss
                    data['RSI'] = 100 - (100 / (1 + rs))
                    st.line_chart(data['RSI'], height=250)
                    if data['RSI'].iloc[-1] < 30:
                        buy_signals += 1
                    elif data['RSI'].iloc[-1] > 70:
                        sell_signals += 1

                    # MACD
                    short_ema = data['Close'].ewm(span=12, adjust=False).mean()
                    long_ema = data['Close'].ewm(span=26, adjust=False).mean()
                    data['MACD'] = short_ema - long_ema
                    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
                    sns.lineplot(data=data, x=data.index, y="MACD", label="MACD")
                    sns.lineplot(data=data, x=data.index, y="Signal", label="Signal Line")
                    if data['MACD'].iloc[-1] > data['Signal'].iloc[-1]:
                        buy_signals += 1
                    else:
                        sell_signals += 1

                    # Display Indicators Plot
                    plt.title(f"{ticker_symbol.upper()} Technical Indicators", fontsize=16)
                    plt.xlabel("Date", fontsize=12)
                    plt.ylabel("Price (USD)", fontsize=12)
                    plt.legend(loc="upper left")
                    st.pyplot(plt)

                    # Recommendation Summary
                    st.subheader("Recommendation Summary")
                    st.write(f"**Buy Signals:** {buy_signals}")
                    st.write(f"**Sell Signals:** {sell_signals}")
                    if buy_signals > sell_signals:
                        st.success("Overall Recommendation: BUY")
                    elif sell_signals > buy_signals:
                        st.error("Overall Recommendation: SELL")
                    else:
                        st.info("Overall Recommendation: HOLD")

            except Exception as e:
                st.error(f"Error fetching data for {ticker_symbol}: {e}")

# Tab: Stock Comparison
with tabs[2]:
    st.header("📈 Stock Comparison")
    st.write("Compare the performance of multiple stocks over a selected date range.")

    # Comparison logic
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
        feed = requests.get(url)
        if feed.status_code == 200:
            feed = feedparser.parse(feed.content)
            return [{"title": entry.title, "url": entry.link, "date": entry.published} for entry in feed.entries[:10]]
        return []

    if ticker_symbol:
        news = extract_news_from_google_rss(ticker_symbol)
        for article in news:
            st.write(f"**{article['title']}**")
            st.write(f"[Read more]({article['url']})")

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
st.markdown("---")
st.markdown("<div style='text-align:center'><small>© 2024 International University of Japan. All rights reserved.</small></div>", unsafe_allow_html=True)
