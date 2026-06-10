import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Advanced Market Analyzer", layout="wide")
st.sidebar.header("⚙️ Control Panel")
st.sidebar.info("Upload your market data, or use our Advanced Simulation to test the logic.")

analysis_window = st.sidebar.slider("Trend Analysis Window (Days)", min_value=3, max_value=14, value=7)
uploaded_file = st.sidebar.file_uploader("Upload Market Data (CSV)", type=["csv"])

st.title("📈 Advanced Market Demand & Restock Analyzer")
st.markdown("Dynamic inventory forecasting based on moving average momentum.")

@st.cache_data
def generate_realistic_data():
    dates = [datetime.today() - timedelta(days=x) for x in range(60, 0, -1)]
    
    coffee = []
    for x in range(60):
        base = 100 + (x * 0.8)
        if dates[x].weekday() >= 5: 
            base += np.random.randint(30, 50)
        coffee.append(int(base + np.random.randint(-10, 15)))
        
    jackets = []
    for x in range(60):
        base = 200 - (x * 2.5)
        jackets.append(int(max(10, base + np.random.randint(-20, 20))))
        
    return pd.DataFrame({"Date": dates, "Organic Coffee": coffee, "Winter Jackets": jackets})

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = generate_realistic_data()

st.subheader("📊 Executive Summary")
col1, col2 = st.columns(2)

def calculate_kpi(product):
    current = df[product].tail(analysis_window).mean()
    previous = df[product].iloc[-(analysis_window*2):-analysis_window].mean()
    percent_change = ((current - previous) / previous) * 100
    return current, percent_change

c_current, c_change = calculate_kpi("Organic Coffee")
j_current, j_change = calculate_kpi("Winter Jackets")

col1.metric("Organic Coffee (Avg Daily Sales)", f"{c_current:.0f} units", f"{c_change:.1f}%")
col2.metric("Winter Jackets (Avg Daily Sales)", f"{j_current:.0f} units", f"{j_change:.1f}%")

st.subheader("Market Demand Visualization")
fig = px.line(df, x="Date", y=["Organic Coffee", "Winter Jackets"], markers=True, template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

st.subheader("🛒 Restock Recommendations")

def dynamic_recommendation(product, change):
    st.markdown(f"### **{product}**")
    if change > 5:
        st.success(f"**Action: AGGRESSIVE RESTOCK.** \n\nDemand has grown by **{change:.1f}%** over the last {analysis_window} days. Capitalize on the momentum.")
    elif change > -5:
        st.warning(f"**Action: HOLD INVENTORY.** \n\nDemand is stable ({change:.1f}% change). Monitor for another {analysis_window} days before reordering.")
    else:
        st.error(f"**Action: HALT ORDERS / DISCOUNT.** \n\nDemand has dropped by **{abs(change):.1f}%**. Do not order more; consider a marketing push to clear stock.")

rc1, rc2 = st.columns(2)
with rc1:
    dynamic_recommendation("Organic Coffee", c_change)
with rc2:
    dynamic_recommendation("Winter Jackets", j_change)
