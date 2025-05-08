import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd





API_BASE = "http://44.226.122.3:4321/api/v1"  # change to deployed URL if hosted

# Set page config
st.set_page_config(
    page_title="Financial Insight Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for navbar
st.markdown("""
    <style>
    .navbar {
        height: 60px;
        background-color: #f0f2f6;
        padding: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .navbar-title {
        font-size: 24px;
        font-weight: bold;
        color: #262730;
    }
    .navbar-buttons {
        display: flex;
        gap: 10px;
    }
    .nav-button {
        background-color: #ffffff;
        border: 1px solid #d3d3d3;
        border-radius: 4px;
        padding: 8px 16px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .nav-button:hover {
        background-color: #e6e6e6;
    }
    </style>
""", unsafe_allow_html=True)

# Create navbar
st.markdown("""
    <div class="navbar">
        <div class="navbar-title">📊 Financial Insight Engine</div>
    </div>
""", unsafe_allow_html=True)

# Navigation
page = st.sidebar.radio("Navigation", ["Dashboard", "Track Assets", "AI Assistant"])

if page == "Dashboard":
    st.header("📊 Dashboard")
    
    # Get assets for dropdowns
    assets = requests.get(f"{API_BASE}/assets").json()
    symbols = set([a["symbol"] for a in assets])
    
    st.subheader("⚖️ Compare Assets")
    
    col1, col2 = st.columns(2)
    with col1:
        # Chart type selection
        chart_type = st.selectbox(
            "Select Chart Type",
            ["Line Chart", "Candlestick Chart", "Area Chart", "Bar Chart"],
            key="chart_type"
        )
        
        # Asset selection
        col1, col2 = st.columns(2)
        with col1:
            asset1 = st.selectbox("Asset 1", symbols, key="a1")
        with col2:
            asset2 = st.selectbox("Asset 2", symbols, key="a2")
        
        # Metric selection
        metric = st.selectbox(
            "Select Metric",
            ["Price", "Volume", "Market Cap", "Price Change %"],
            key="metric"
        )

    if st.button("Compare"):
        compare = requests.get(f"{API_BASE}/compare?asset1={asset1}&asset2={asset2}").json()
        
        # Create chart
        fig = go.Figure()
        
        # Get data from response
        asset1_data = compare['comparison'][asset1]
        asset2_data = compare['comparison'][asset2]
        
        # Extract data based on selected metric
        dates1 = [pd.to_datetime(item["timestamp"]) for item in asset1_data]
        dates2 = [pd.to_datetime(item["timestamp"]) for item in asset2_data]
        
        if metric == "Price":
            values1 = [item["latest_price"] for item in asset1_data]
            values2 = [item["latest_price"] for item in asset2_data]
            y_title = "Price"
        elif metric == "Volume":
            values1 = [item["volume"] for item in asset1_data]
            values2 = [item["volume"] for item in asset2_data]
            y_title = "Volume"
        elif metric == "Market Cap":
            values1 = [item["market_cap"] for item in asset1_data]
            values2 = [item["market_cap"] for item in asset2_data]
            y_title = "Market Cap"
        else:  # Price Change %
            values1 = [item["price_change_percent"] for item in asset1_data]
            values2 = [item["price_change_percent"] for item in asset2_data]
            y_title = "Price Change %"
        
        # Add traces based on chart type
        if chart_type == "Line Chart":
            fig.add_trace(go.Scatter(
                x=dates1,
                y=values1,
                name=asset1,
                line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                x=dates2,
                y=values2,
                name=asset2,
                line=dict(color='red')
            ))
        elif chart_type == "Candlestick Chart":
            # Note: This is a simplified candlestick - would need OHLC data for proper candlesticks
            fig.add_trace(go.Candlestick(
                x=dates1,
                open=[v * 0.99 for v in values1],  # Simulated open
                high=[v * 1.01 for v in values1],  # Simulated high
                low=[v * 0.98 for v in values1],   # Simulated low
                close=values1,
                name=asset1
            ))
            fig.add_trace(go.Candlestick(
                x=dates2,
                open=[v * 0.99 for v in values2],  # Simulated open
                high=[v * 1.01 for v in values2],  # Simulated high
                low=[v * 0.98 for v in values2],   # Simulated low
                close=values2,
                name=asset2
            ))
        elif chart_type == "Area Chart":
            fig.add_trace(go.Scatter(
                x=dates1,
                y=values1,
                name=asset1,
                fill='tozeroy',
                line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                x=dates2,
                y=values2,
                name=asset2,
                fill='tozeroy',
                line=dict(color='red')
            ))
        else:  # Bar Chart
            fig.add_trace(go.Bar(
                x=dates1,
                y=values1,
                name=asset1,
                marker_color='blue'
            ))
            fig.add_trace(go.Bar(
                x=dates2,
                y=values2,
                name=asset2,
                marker_color='red'
            ))
        
        # Update layout
        fig.update_layout(
            title=f"{asset1} vs {asset2} {metric} Comparison",
            xaxis_title="Date",
            yaxis_title=y_title,
            height=500,
            template="plotly_white",
            xaxis=dict(
                tickformat='%Y-%m-%d %H:%M',
                tickangle=45
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif page == "Track Assets":
    st.header("📋 Track Assets")
    
    # Add new asset form
    with st.form("add_symbol_form"):
        st.subheader("➕ Add New Asset")
        col1, col2 = st.columns(2)
        with col1:
            new_symbol = st.text_input("Enter new symbol (e.g., AAPL, BTC-USD)")
        with col2:
            st.write("")  # For alignment
            st.write("")  # For alignment
            submitted = st.form_submit_button("Add Asset")
        
        if submitted and new_symbol:
            response = requests.post(f"{API_BASE}/add_symbol?symbol={new_symbol}")
            if response.status_code == 200:
                st.success(f"Symbol '{new_symbol}' added and ingested.")
            else:
                st.error("Error adding symbol.")
    
    # Sync button
    if st.button("🔄 Sync All Assets"):
        response = requests.post(f"{API_BASE}/ingest")
        if response.status_code == 200:
            st.success("Data synced successfully!")
        else:
            st.error("Error syncing data")
    
    # Show all tracked assets
    st.subheader("📊 Tracked Assets")
    assets = requests.get(f"{API_BASE}/assets").json()
    if assets:
        st.table(assets)
    else:
        st.info("No assets are being tracked yet. Add some assets to get started!")

else:  # AI Assistant page
    st.header("🤖 AI Assistant")
    
    # Get list of available symbols
    assets = requests.get(f"{API_BASE}/assets").json()
    symbols = set([a["symbol"] for a in assets])
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Market Summary Section
        st.subheader("📈 Market Summary")
        if st.button("Generate Market Summary"):
            try:
                # Call the /summary API endpoint
                summary_response = requests.get(f"{API_BASE}/summary").json()
                st.markdown("### Current Market Overview")
                st.markdown(summary_response["summary"])
            except Exception as e:
                st.error(f"Error generating market summary: {str(e)}")
        
        # Chat Interface
        st.subheader("💬 Ask Questions")
        user_question = st.text_area(
            "Ask a question about the market or specific assets:",
            placeholder="e.g., What are the current market trends? How are BTC and ETH correlated?",
            height=100
        )
        
        if st.button("Get Analysis"):
            if user_question:
                try:
                    # Get all assets data
                    all_assets_data = {}
                    for symbol in symbols:
                        asset_data = requests.get(f"{API_BASE}/metrics/{symbol}").json()
                        all_assets_data[symbol] = asset_data
                    
                    # Generate response using Groq service
                    response = requests.post(
                        f"{API_BASE}/analyze",
                        json={"question": user_question, "assets": all_assets_data}
                    ).json()
                    st.markdown("### Analysis")
                    st.markdown(response["analysis"])
                except Exception as e:
                    st.error(f"Error generating analysis: {str(e)}")
            else:
                st.warning("Please enter a question to get market analysis.")
    
    with col2:
        # Quick Analysis Options
        st.subheader("⚡ Quick Analysis")
        
        # Predefined questions
        quick_questions = [
            "What are the current market trends?",
            "Which assets are performing best?",
            "What are the potential risks in the market?",
            "How are crypto and traditional assets correlated?"
        ]
        
        for question in quick_questions:
            if st.button(question, key=f"quick_{question}"):
                try:
                    # Get all assets data
                    all_assets_data = {}
                    for symbol in symbols:
                        asset_data = requests.get(f"{API_BASE}/metrics/{symbol}").json()
                        all_assets_data[symbol] = asset_data
                    
                    # Generate response using API endpoint
                    response = requests.post(
                        f"{API_BASE}/analyze",
                        json={"question": question, "assets": all_assets_data}
                    ).json()
                    st.markdown("### Analysis")
                    st.markdown(response["analysis"])
                except Exception as e:
                    st.error(f"Error generating analysis: {str(e)}")
        
        # Asset Information
        st.subheader("📊 Tracked Assets")
        asset_data = requests.get(f"{API_BASE}/get_latest_priceconne").json()
        assets = asset_data["latest_price"]
        for asset in assets:
            st.markdown(f"""
                **{asset['symbol']}**
                - Latest Price: ${asset['latest_price']:.2f}
                - 24h Change: {asset['change_percent_24h']:.2f}%
                - 7d Average: ${asset['average_price_7d']:.2f}
            """)
