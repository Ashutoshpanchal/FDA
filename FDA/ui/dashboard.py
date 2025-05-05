import streamlit as st
import requests

API_BASE = "http://localhost:4321"  # change to deployed URL if hosted

st.title("📊 Financial Insight Engine")

# --- Section: Add New Asset ---
st.header("➕ Track New Asset")
new_symbol = st.text_input("Enter new symbol (e.g., AAPL, BTC-USD)")

if st.button("Add Symbol"):
    response = requests.post(f"{API_BASE}/ingest", json={"symbol": new_symbol})
    if response.status_code == 200:
        st.success(f"Symbol '{new_symbol}' added and ingested.")
    else:
        st.error("Error adding symbol.")

# --- Section: Show All Assets ---
st.header("📋 Tracked Assets")
assets = requests.get(f"{API_BASE}/assets").json()
st.table(assets)

# --- Section: View Metrics ---
st.header("📈 View Metrics")
symbols = [a["symbol"] for a in assets]
selected = st.selectbox("Choose asset", symbols)

if selected:
    metrics = requests.get(f"{API_BASE}/metrics/{selected}").json()
    st.json(metrics)

# --- Section: Compare Assets ---
st.header("⚖️ Compare Assets")
asset1 = st.selectbox("Asset 1", symbols, key="a1")
asset2 = st.selectbox("Asset 2", symbols, key="a2")

if st.button("Compare"):
    compare = requests.get(f"{API_BASE}/compare", params={"asset1": asset1, "asset2": asset2}).json()
    st.json(compare)

# --- Section: AI Summary ---
st.header("🧠 GenAI Market Summary")

if st.button("Get Market Summary"):
    summary = requests.get(f"{API_BASE}/summary").json()
    st.markdown(summary["summary"])
