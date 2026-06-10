import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Market Analyzer", layout="wide")
st.sidebar.header("⚙️ Data Settings")
analysis_window = st.sidebar.slider("Trend Analysis Window (Weeks)", min_value=1, max_value=8, value=4)
uploaded_file = st.sidebar.file_uploader("Upload 10-Item CSV", type=["csv"])

st.title("📈 10-Product Market Inventory Analyzer")

@st.cache_data
def generate_data():
    dates = [datetime(2026, 1, 1) + timedelta(weeks=x) for x in range(22)]
    # 10 diverse products with varied trends
    data = {"Date": dates,
            "Organic Coffee": [1500 + (x*150) for x in range(22)],
            "Winter Jackets": [6200 - (x*250) for x in range(22)],
            "Button Mushrooms": [500 + (x*200) for x in range(22)],
            "Milky Mushrooms": [800 + (x*50) for x in range(22)],
            "Badminton Rackets": [300 + np.random.randint(0, 100) for x in range(22)],
            "Umbrellas": [100 if x < 10 else 1800 + (x*50) for x in range(22)],
            "Energy Drinks": [5000 + np.random.randint(-200, 200) for x in range(22)],
            "Sunscreen": [200 + (x*180) for x in range(22)],
            "Smart Sensors": [1000 + (x*80) for x in range(22)],
            "Engine Oil": [400 + np.random.randint(-20, 20) for x in range(22)]}
    return pd.DataFrame(data)

df = uploaded_file if uploaded_file else generate_data()
if uploaded_file: df = pd.read_csv(uploaded_file)
products = [col for col in df.columns if col != "Date"]

st.plotly_chart(px.line(df, x="Date", y=products, markers=True, template="plotly_white"), use_container_width=True)

st.subheader("🛒 Item-by-Item Analysis & Restock Status")
for i in range(0, len(products), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j < len(products):
            prod = products[i + j]
            with cols[j]:
                current = df[prod].tail(analysis_window).mean()
                prev = df[prod].iloc[-(analysis_window*2):-analysis_window].mean()
                change = ((current - prev) / prev) * 100 if prev != 0 else 0
                st.metric(label=f"{prod}", value=f"{current:,.0f} units", delta=f"{change:.1f}%")
                if change > 5: st.success("Status: AGGRESSIVE RESTOCK")
                elif change >= -5: st.warning("Status: HOLD INVENTORY")
                else: st.error("Status: HALT ORDERS")