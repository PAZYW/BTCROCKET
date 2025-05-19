import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from pytrends.request import TrendReq
from textblob import TextBlob

# Ustawienia wyglądu
st.set_page_config(page_title="BTC Dashboard", layout="wide", page_icon="₿")
st.markdown("<style>body { background-color: #111; color: #eee; }</style>", unsafe_allow_html=True)

# CSS do stylu Binance
st.markdown("""
<style>
    .big-font {
        font-size:36px !important;
        font-weight: bold;
        color: #0ecb81;
    }
    .red {
        color: #f6465d;
    }
    .green {
        color: #0ecb81;
    }
</style>
""", unsafe_allow_html=True)

# --- SEKCJA: Cena i wolumen z CoinGecko ---
def get_market_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin"
    response = requests.get(url)
    data = response.json()
    market = data['market_data']
    return {
        "price": market['current_price']['usd'],
        "volume": market['total_volume']['usd'],
        "change": market['price_change_percentage_24h']
    }

market = get_market_data()
st.title("₿ BTC Dashboard – lokalna analiza AI")
st.markdown("---")

col1, col2, col3 = st.columns(3)
col1.markdown(f"<div class='big-font'>💰 Cena BTC: ${market['price']:,}</div>", unsafe_allow_html=True)
change_class = "green" if market["change"] >= 0 else "red"
col2.markdown(f"<div class='big-font {change_class}'>📉 Zmiana 24h: {market['change']:.2f}%</div>", unsafe_allow_html=True)
col3.markdown(f"<div class='big-font'>📊 Wolumen: ${market['volume'] / 1_000_000_000:.2f}B</div>", unsafe_allow_html=True)

st.markdown("---")

# --- SEKCJA: Wykres ceny z MA ---
@st.cache_data
def get_chart_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"
    data = requests.get(url).json()
    df = pd.DataFrame(data["prices"], columns=["time", "price"])
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df["MA7"] = df["price"].rolling(window=7).mean()
    df["MA25"] = df["price"].rolling(window=25).mean()
    return df

chart = get_chart_data()
fig = go.Figure()
fig.add_trace(go.Scatter(x=chart["time"], y=chart["price"], name="Cena", line=dict(color="white")))
fig.add_trace(go.Scatter(x=chart["time"], y=chart["MA7"], name="MA7", line=dict(color="purple")))
fig.add_trace(go.Scatter(x=chart["time"], y=chart["MA25"], name="MA25", line=dict(color="orange")))
fig.update_layout(template="plotly_dark", title="📈 Wykres ceny BTC z MA", height=400)
st.plotly_chart(fig, use_container_width=True)

# --- SEKCJA: Google Trends ---
pytrends = TrendReq(hl='en-US', tz=360)
pytrends.build_payload(["bitcoin"], cat=0, timeframe='now 7-d', geo='', gprop='')
trends = pytrends.interest_over_time()

if not trends.empty:
    trends = trends.reset_index()
    st.subheader("📊 Zainteresowanie Bitcoinem (Google Trends)")
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=trends["date"], y=trends["bitcoin"], fill="tozeroy", name="Zainteresowanie", line=dict(color="cyan")))
    fig_trend.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig_trend, use_container_width=True)

# --- SEKCJA: Sentyment z Reddita ---
def get_reddit_sentiment():
    url = "https://api.pushshift.io/reddit/search/submission/?q=bitcoin&size=100"
    r = requests.get(url)
    if r.status_code != 200:
        return "neutral"
    posts = r.json().get("data", [])
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    for post in posts:
        title = post.get("title", "")
        polarity = TextBlob(title).sentiment.polarity
        if polarity > 0.1:
            sentiments["positive"] += 1
        elif polarity < -0.1:
            sentiments["negative"] += 1
        else:
            sentiments["neutral"] += 1
    return max(sentiments, key=sentiments.get)

senti = get_reddit_sentiment()
senti_emoji = {"positive": "🟢", "neutral": "🟡", "negative": "🔴"}
st.markdown(f"### 💬 Nastroje z Reddita: {senti_emoji.get(senti, '🟡')} {senti.upper()}")

# --- SEKCJA: Analiza trendu i rekomendacja ---
st.markdown("---")
st.header("🧠 Analiza AI: TREND + DECYZJA")

trend = "wzrostowy" if chart["MA7"].iloc[-1] > chart["MA25"].iloc[-1] else "spadkowy" if chart["MA7"].iloc[-1] < chart["MA25"].iloc[-1] else "neutralny"

risk = 0.5 if senti == "negative" else 0.3 if senti == "neutral" else 0.15
reward = 0.03 if trend == "spadkowy" else 0.08 if trend == "wzrostowy" else 0.05

recommendation = "KUPUJ" if trend == "wzrostowy" and senti == "positive" else "SPRZEDAJ" if trend == "spadkowy" and senti == "negative" else "OBSERWUJ"

st.subheader(f"📌 Trend: {trend.upper()}")
st.subheader(f"✅ Rekomendacja: **{recommendation}**")
st.metric("📉 Ryzyko", f"{int(risk * 100)}%")
st.metric("📈 Potencjalny zysk", f"{int(reward * 100)}%")
