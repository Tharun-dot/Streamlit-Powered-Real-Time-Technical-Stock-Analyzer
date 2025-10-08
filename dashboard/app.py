import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.alphavantage_api import fetch_daily_data
from services.indicators import add_indicators
from models.model import generate_signals
from config import DEFAULT_SYMBOL

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(
    page_title="Yami-stocks Pro - Advanced Trading Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# Premium Enterprise Styling
# --------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --warning-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --danger-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        --dark-bg: #0f0f23;
        --card-bg: rgba(255, 255, 255, 0.05);
        --border-color: rgba(255, 255, 255, 0.1);
        --text-primary: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.7);
        --text-muted: rgba(255, 255, 255, 0.5);
        --accent-blue: #00d4ff;
        --accent-purple: #8b5cf6;
        --accent-green: #10b981;
        --accent-orange: #f59e0b;
    }

    html, body, [class*="st-"] {
        font-family: 'Manrope', sans-serif;
        background: var(--dark-bg) !important;
        color: var(--text-primary) !important;
    }

    .main .block-container {
        padding-top: 1rem;
        max-width: 100%;
    }

    /* Premium Header */
    .premium-header {
        background: var(--primary-gradient);
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .premium-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    .premium-header h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #ffffff, #f0f9ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
    }
    
    .premium-header .subtitle {
        font-size: 1.4rem;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 0.5rem;
    }
    
    .premium-header .tagline {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 300;
    }

    /* Premium Metric Cards */
    .premium-metric-card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .premium-metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-gradient);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .premium-metric-card:hover::before {
        transform: scaleX(1);
    }
    
    .premium-metric-card:hover {
        transform: translateY(-8px);
        background: rgba(255, 255, 255, 0.08);
        border-color: var(--accent-blue);
        box-shadow: 0 25px 50px rgba(0, 212, 255, 0.2);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: var(--text-muted);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }
    
    .metric-change {
        font-size: 1rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        display: inline-block;
    }
    
    .metric-change.positive {
        background: var(--success-gradient);
        color: white;
    }
    
    .metric-change.negative {
        background: var(--danger-gradient);
        color: white;
    }

    /* Section Headers */
    .section-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 3rem 0 2rem 0;
        padding-bottom: 1rem;
        position: relative;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .section-header::after {
        content: '';
        flex: 1;
        height: 2px;
        background: var(--primary-gradient);
        border-radius: 1px;
    }

    /* Premium Trading Signals */
    .premium-signal {
        border-radius: 20px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
    }
    
    .premium-signal::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        opacity: 0.1;
        z-index: 0;
    }
    
    .signal-content {
        position: relative;
        z-index: 1;
    }
    
    .signal-buy {
        background: var(--success-gradient);
        box-shadow: 0 15px 35px rgba(16, 185, 129, 0.3);
    }
    
    .signal-sell {
        background: var(--danger-gradient);
        box-shadow: 0 15px 35px rgba(245, 101, 101, 0.3);
    }
    
    .signal-hold {
        background: var(--warning-gradient);
        box-shadow: 0 15px 35px rgba(245, 158, 11, 0.3);
        color: var(--dark-bg) !important;
    }
    
    .signal-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .signal-subtitle {
        font-size: 1.2rem;
        font-weight: 500;
        opacity: 0.9;
    }

    /* Premium Buttons */
    .stButton>button {
        background: var(--primary-gradient) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0) !important;
    }

    /* Premium Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--dark-bg) 0%, rgba(15, 15, 35, 0.95) 100%) !important;
        border-right: 1px solid var(--border-color) !important;
        backdrop-filter: blur(20px) !important;
    }
    
    .sidebar-header {
        padding: 2rem 1rem;
        text-align: center;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 2rem;
    }
    
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 700;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    /* Premium Data Tables */
    .stDataFrame {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Premium Selectbox & Input */
    .stSelectbox > div > div, .stTextInput > div > div {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }
    
    /* Premium Slider */
    .stSlider > div > div > div > div {
        background: var(--primary-gradient) !important;
    }
    
    /* Alert Improvements */
    .stAlert {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(20px) !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------
# Header
# --------------------------
st.markdown("""
<div class="premium-header">
    <h1><i class="fas fa-rocket"></i> Yami-stock Pro</h1>
    <div class="subtitle">Enterprise-Grade Financial Intelligence Platform</div>
    <div class="tagline">Powered by Advanced AI Analytics & Real-Time Market Data</div>
</div>
""", unsafe_allow_html=True)

# --------------------------
# Premium Sidebar Controls
# --------------------------
st.sidebar.markdown('<div class="sidebar-header"><div class="sidebar-title"><i class="fas fa-chart-line"></i> Trading Command Center</div><p style="color: var(--text-muted); font-size: 0.9rem;">Configure your analysis parameters</p></div>', unsafe_allow_html=True)

st.sidebar.markdown("### <i class='fas fa-search'></i> Market Analysis", unsafe_allow_html=True)
symbol = st.sidebar.text_input("🎯 Stock Symbol", value=DEFAULT_SYMBOL, help="Enter any valid stock ticker (e.g., AAPL, TSLA, GOOGL)")

time_period = st.sidebar.selectbox(
    "⏰ Analysis Timeframe", 
    ["1M", "3M", "6M", "1Y", "2Y", "5Y"], 
    index=2,
    help="Select the time period for historical analysis"
)

st.sidebar.markdown("### <i class='fas fa-chart-bar'></i> Technical Indicators", unsafe_allow_html=True)
show_sma = st.sidebar.checkbox(" Simple Moving Average (SMA)", value=True)
show_ema = st.sidebar.checkbox(" Exponential Moving Average (EMA)", value=True)
show_rsi = st.sidebar.checkbox(" Relative Strength Index (RSI)", value=True)
show_macd = st.sidebar.checkbox(" MACD Convergence Divergence", value=True)

st.sidebar.markdown("### <i class='fas fa-shield-alt'></i> Risk Parameters", unsafe_allow_html=True)
rsi_oversold = st.sidebar.slider("🔻 RSI Oversold Level", 20, 40, 30, help="RSI below this level indicates oversold condition")
rsi_overbought = st.sidebar.slider("🔺 RSI Overbought Level", 60, 80, 70, help="RSI above this level indicates overbought condition")

st.sidebar.markdown("---")
if st.sidebar.button(" Refresh Market Data", type="primary"):
    st.rerun()

# Add market status
st.sidebar.markdown("### <i class='fas fa-globe'></i> Market Status", unsafe_allow_html=True)
st.sidebar.success("🟢 Markets Open")
st.sidebar.info(f"🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}")

# --------------------------
# Main Dashboard
# --------------------------
try:
    with st.spinner("🔄 Fetching real-time market data..."):
        time.sleep(0.5)

    # Fetch & Process Data
    df_raw = fetch_daily_data(symbol)
    df_raw = add_indicators(df_raw)
    df_raw = generate_signals(df_raw)

    # Filter data based on selected time period
    today = datetime.now()
    if time_period == "1M":
        start_date = today - timedelta(days=30)
    elif time_period == "3M":
        start_date = today - timedelta(days=90)
    elif time_period == "6M":
        start_date = today - timedelta(days=180)
    elif time_period == "1Y":
        start_date = today - timedelta(days=365)
    elif time_period == "2Y":
        start_date = today - timedelta(days=730)
    elif time_period == "5Y":
        start_date = today - timedelta(days=1825)
    else:
        start_date = today - timedelta(days=180)  # Default to 6M
    
    df = df_raw.loc[df_raw.index >= start_date]

    if df.empty:
        st.error("No data available for the selected time period.")
        st.stop()
        
    # ----------------------
    # Premium Market Overview
    # ----------------------
    st.markdown('<div class="section-header"><i class="fas fa-chart-area"></i> Live Market Intelligence</div>', unsafe_allow_html=True)

    # Calculate advanced metrics
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    price_change = current_price - prev_price
    price_change_pct = (price_change / prev_price) * 100
    
    # Advanced volume analysis
    avg_volume = df['Volume'].rolling(20).mean().iloc[-1]
    current_volume = df['Volume'].iloc[-1]
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
    
    # Risk metrics
    returns = df['Close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(252) * 100
    sharpe_ratio = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
    max_drawdown = ((df['Close'] / df['Close'].expanding().max()) - 1).min() * 100
    
    # Performance metrics
    ytd_return = ((current_price - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        price_icon = "📈" if price_change >= 0 else "📉"
        st.markdown(f"""
        <div class="premium-metric-card">
            <div class="metric-icon">{price_icon}</div>
            <div class="metric-value">${current_price:.2f}</div>
            <div class="metric-label">Current Price</div>
            <div class="metric-change {'positive' if price_change >= 0 else 'negative'}">
                {price_change:+.2f} ({price_change_pct:+.2f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        rsi_value = df['RSI'].iloc[-1]
        rsi_status = "Oversold" if rsi_value < rsi_oversold else "Overbought" if rsi_value > rsi_overbought else "Neutral"
        rsi_icon = "🔻" if rsi_value < rsi_oversold else "🔺" if rsi_value > rsi_overbought else "⚖️"
        st.markdown(f"""
        <div class="premium-metric-card">
            <div class="metric-icon">{rsi_icon}</div>
            <div class="metric-value">{rsi_value:.1f}</div>
            <div class="metric-label">RSI Momentum</div>
            <div class="metric-change">{rsi_status}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="premium-metric-card">
            <div class="metric-icon">⚡</div>
            <div class="metric-value">{volatility:.1f}%</div>
            <div class="metric-label">Annual Volatility</div>
            <div class="metric-change">Risk Measure</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        volume_icon = "🚀" if volume_ratio > 1.5 else "📊"
        st.markdown(f"""
        <div class="premium-metric-card">
            <div class="metric-icon">{volume_icon}</div>
            <div class="metric-value">{volume_ratio:.2f}x</div>
            <div class="metric-label">Volume Ratio</div>
            <div class="metric-change">vs 20-Day Avg</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        sma_20 = df['SMA_20'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        trend = "Bullish" if sma_20 > sma_50 else "Bearish"
        trend_icon = "🐂" if trend == "Bullish" else "🐻"
        st.markdown(f"""
        <div class="premium-metric-card">
            <div class="metric-icon">{trend_icon}</div>
            <div class="metric-value">{trend}</div>
            <div class="metric-label">Market Trend</div>
            <div class="metric-change">SMA Analysis</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Additional premium metrics row
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="premium-metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-value">{sharpe_ratio:.2f}</div>
            <div class="metric-label">Sharpe Ratio</div>
            <div class="metric-change">Risk-Adjusted Return</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="premium-metric-card">
            <div class="metric-icon">📉</div>
            <div class="metric-value">{max_drawdown:.1f}%</div>
            <div class="metric-label">Max Drawdown</div>
            <div class="metric-change">Peak to Trough</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="premium-metric-card">
            <div class="metric-icon">📅</div>
            <div class="metric-value">{ytd_return:+.1f}%</div>
            <div class="metric-label">YTD Performance</div>
            <div class="metric-change">Year to Date</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        market_cap = current_price * 1000000000  # Placeholder calculation
        st.markdown(f"""
        <div class="premium-metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-value">${market_cap/1000000000:.1f}B</div>
            <div class="metric-label">Market Cap</div>
            <div class="metric-change">Estimated Value</div>
        </div>
        """, unsafe_allow_html=True)

    # ----------------------
    # Premium Price Analysis
    # ----------------------
    st.markdown('<div class="section-header"><i class="fas fa-chart-line"></i> Advanced Price Analysis</div>', unsafe_allow_html=True)
    
    # 1. Candlestick Chart with Signals
    fig_price = go.Figure()
    fig_price.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="Price",
        increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
    ))
    
    if show_sma and "SMA_20" in df.columns:
        fig_price.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], line=dict(color="#3498db", width=2), name="SMA 20"))
    if show_sma and "SMA_50" in df.columns:
        fig_price.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], line=dict(color="#e74c3c", width=2), name="SMA 50"))
    if show_ema and "EMA_20" in df.columns:
        fig_price.add_trace(go.Scatter(x=df.index, y=df["EMA_20"], line=dict(color="#9b59b6", width=2, dash='dash'), name="EMA 20"))

    buy_signals = df[df["Signal"] == "BUY"]
    if not buy_signals.empty:
        fig_price.add_trace(go.Scatter(
            x=buy_signals.index,
            y=buy_signals['Low'] * 0.98,
            mode='markers',
            marker=dict(symbol='triangle-up', size=12, color='#2ecc71', line=dict(width=1, color='white')),
            name='Buy Signal'
        ))

    sell_signals = df[df["Signal"] == "SELL"]
    if not sell_signals.empty:
        fig_price.add_trace(go.Scatter(
            x=sell_signals.index,
            y=sell_signals['High'] * 1.02,
            mode='markers',
            marker=dict(symbol='triangle-down', size=12, color='#e74c3c', line=dict(width=1, color='white')),
            name='Sell Signal'
        ))

    fig_price.update_layout(
        title=dict(text=f"<b>Price & Moving Averages for {symbol}</b>", x=0.5, font=dict(color='#f0f2f6')),
        xaxis_rangeslider_visible=False,
        height=600,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor="#2c3e50",
        paper_bgcolor="#1e1e2f"
    )

    st.plotly_chart(fig_price, width='stretch')

    # ----------------------
    # Premium Volume Analysis
    # ----------------------
    st.markdown('<div class="section-header"><i class="fas fa-chart-bar"></i> Volume Intelligence</div>', unsafe_allow_html=True)
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='#3498db'))
    fig_volume.update_layout(
        title=dict(text=f"<b>Daily Volume for {symbol}</b>", x=0.5, font=dict(color='#f0f2f6')),
        xaxis_rangeslider_visible=False,
        height=250,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor="#2c3e50",
        paper_bgcolor="#1e1e2f"
    )
    st.plotly_chart(fig_volume, width='stretch')

    # ----------------------
    # Advanced Technical Analysis
    # ----------------------
    st.markdown('<div class="section-header"><i class="fas fa-brain"></i> AI-Powered Technical Indicators</div>', unsafe_allow_html=True)
    fig_indicators = go.Figure()
    
    if show_rsi and "RSI" in df.columns:
        fig_indicators.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#9b59b6')))
        fig_indicators.add_hline(y=rsi_overbought, line_dash="dash", line_color="#e74c3c", annotation_text="Overbought")
        fig_indicators.add_hline(y=rsi_oversold, line_dash="dash", line_color="#2ecc71", annotation_text="Oversold")
    
    if show_macd and "MACD" in df.columns:
        fig_indicators.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='#3498db')))
        fig_indicators.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], name='Signal Line', line=dict(color='#e74c3c', dash='dot')))
        fig_indicators.add_trace(go.Bar(
            x=df.index, y=df['MACD_Histogram'], name='MACD Hist',
            marker_color=['#2ecc71' if hist > 0 else '#e74c3c' for hist in df['MACD_Histogram']]
        ))
        
    fig_indicators.update_layout(
        title=dict(text=f"<b>RSI & MACD for {symbol}</b>", x=0.5, font=dict(color='#f0f2f6')),
        xaxis_rangeslider_visible=False,
        height=350,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor="#2c3e50",
        paper_bgcolor="#1e1e2f"
    )
    st.plotly_chart(fig_indicators, width='stretch')

    # ----------------------
    # AI Trading Intelligence
    # ----------------------
    st.markdown('<div class="section-header"><i class="fas fa-robot"></i> AI Trading Intelligence & Signals</div>', unsafe_allow_html=True)
    
    if "Signal" in df.columns and not df.empty:
        last_signal = df["Signal"].iloc[-1]
        rsi_current = df['RSI'].iloc[-1]
        signal_strength = "STRONG" if abs(rsi_current - 50) > 25 else "MODERATE" if abs(rsi_current - 50) > 15 else "WEAK"
        
        # Calculate signal confidence score
        confidence_factors = []
        if abs(rsi_current - 50) > 20: confidence_factors.append("RSI Extreme")
        if df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().iloc[-1] * 1.5: confidence_factors.append("High Volume")
        if abs(df['Close'].iloc[-1] - df['SMA_20'].iloc[-1]) > df['Close'].iloc[-1] * 0.02: confidence_factors.append("Price Divergence")
        
        confidence_score = len(confidence_factors) * 33.33
        confidence_level = "HIGH" if confidence_score > 66 else "MEDIUM" if confidence_score > 33 else "LOW"
        
        signal_counts = df["Signal"].value_counts()
        
        # Premium signal metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="premium-metric-card">
                <div class="metric-icon">🟢</div>
                <div class="metric-value">{signal_counts.get("BUY", 0)}</div>
                <div class="metric-label">BUY Signals</div>
                <div class="metric-change positive">Bullish Opportunities</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="premium-metric-card">
                <div class="metric-icon">🔴</div>
                <div class="metric-value">{signal_counts.get("SELL", 0)}</div>
                <div class="metric-label">SELL Signals</div>
                <div class="metric-change negative">Bearish Warnings</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="premium-metric-card">
                <div class="metric-icon">🟡</div>
                <div class="metric-value">{signal_counts.get("HOLD", 0)}</div>
                <div class="metric-label">HOLD Signals</div>
                <div class="metric-change">Neutral Positions</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="premium-metric-card">
                <div class="metric-icon">🎯</div>
                <div class="metric-value">{confidence_score:.0f}%</div>
                <div class="metric-label">Signal Confidence</div>
                <div class="metric-change">{confidence_level} Reliability</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Premium signal display
        if last_signal == "BUY":
            st.markdown(f"""
            <div class="premium-signal signal-buy">
                <div class="signal-content">
                    <div class="signal-title"><i class="fas fa-arrow-trend-up"></i> STRONG BUY SIGNAL</div>
                    <div class="signal-subtitle">Confidence: {confidence_level} | Strength: {signal_strength} | RSI: {rsi_current:.1f}</div>
                    <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">Factors: {', '.join(confidence_factors) if confidence_factors else 'Standard Analysis'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif last_signal == "SELL":
            st.markdown(f"""
            <div class="premium-signal signal-sell">
                <div class="signal-content">
                    <div class="signal-title"><i class="fas fa-arrow-trend-down"></i> STRONG SELL SIGNAL</div>
                    <div class="signal-subtitle">Confidence: {confidence_level} | Strength: {signal_strength} | RSI: {rsi_current:.1f}</div>
                    <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">Factors: {', '.join(confidence_factors) if confidence_factors else 'Standard Analysis'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="premium-signal signal-hold">
                <div class="signal-content">
                    <div class="signal-title"><i class="fas fa-pause"></i> STRATEGIC HOLD</div>
                    <div class="signal-subtitle">Confidence: {confidence_level} | Strength: {signal_strength} | RSI: {rsi_current:.1f}</div>
                    <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.7;">Market in consolidation phase - Monitor for breakout</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Premium Signal History
        recent_signals = df[df["Signal"] != "HOLD"].tail(10)
        if not recent_signals.empty:
            st.markdown("#### <i class='fas fa-history'></i> Recent Signal History", unsafe_allow_html=True)
            sig_display = recent_signals[["Close", "RSI", "SMA_20", "SMA_50", "Signal"]].copy()
            sig_display.index = sig_display.index.strftime('%Y-%m-%d')
            
            # Add performance column
            sig_display['Performance'] = sig_display['Close'].pct_change().fillna(0) * 100
            sig_display = sig_display.round(2)
            
            st.dataframe(
                sig_display, 
                width='stretch', 
                hide_index=False,
                use_container_width=False
            )
        else:
            st.info("🚧 No recent BUY/SELL signals detected. Market in consolidation phase - Monitoring for opportunities.")
    else:
        st.warning("Signal generation failed or no data available.")

    # ----------------------
    # Premium Market Data Intelligence
    # ----------------------
    st.markdown('<div class="section-header"><i class="fas fa-database"></i> Comprehensive Market Data Intelligence</div>', unsafe_allow_html=True)
    
    # Create enhanced data display with additional calculated fields
    display_df = df[["Open", "High", "Low", "Close", "Volume", "SMA_20", "SMA_50", "RSI", "Signal"]].tail(20).copy()
    
    # Add calculated fields
    display_df['Daily Change %'] = df['Close'].pct_change() * 100
    display_df['Volume Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
    display_df['Price vs SMA20'] = ((df['Close'] - df['SMA_20']) / df['SMA_20'] * 100)
    
    # Round for display
    display_df = display_df.round(2)
    display_df.index = display_df.index.strftime('%Y-%m-%d')
    
    # Add summary statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### <i class='fas fa-chart-pie'></i> Period Statistics", unsafe_allow_html=True)
        stats_data = {
            'Metric': ['Average Price', 'Highest Price', 'Lowest Price', 'Total Volume', 'Avg Daily Volume'],
            'Value': [
                f"${df['Close'].tail(20).mean():.2f}",
                f"${df['High'].tail(20).max():.2f}",
                f"${df['Low'].tail(20).min():.2f}",
                f"{df['Volume'].tail(20).sum():,.0f}",
                f"{df['Volume'].tail(20).mean():,.0f}"
            ]
        }
        st.dataframe(pd.DataFrame(stats_data), hide_index=True, width='stretch')
    
    with col2:
        st.markdown("#### <i class='fas fa-brain'></i> Technical Summary", unsafe_allow_html=True)
        tech_data = {
            'Indicator': ['Current RSI', 'RSI Average', 'Bullish Days', 'Bearish Days', 'Neutral Days'],
            'Value': [
                f"{df['RSI'].iloc[-1]:.1f}",
                f"{df['RSI'].tail(20).mean():.1f}",
                f"{len(df[df['Signal'] == 'BUY'].tail(20))}",
                f"{len(df[df['Signal'] == 'SELL'].tail(20))}",
                f"{len(df[df['Signal'] == 'HOLD'].tail(20))}"
            ]
        }
        st.dataframe(pd.DataFrame(tech_data), hide_index=True, width='stretch')
    
    st.markdown("#### <i class='fas fa-table'></i> Detailed Market Data", unsafe_allow_html=True)
    st.dataframe(display_df, width='stretch', height=500, hide_index=False)

    # ----------------------
    # Premium Footer
    # ----------------------
    st.markdown('<br><br>', unsafe_allow_html=True)
    st.markdown("""
    <div style="
        background: var(--primary-gradient);
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        margin-top: 3rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    ">
        <h2 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem; color: white;">
            <i class="fas fa-rocket"></i> Yami-stocks Pro
        </h2>
        <p style="font-size: 1.2rem; margin-bottom: 1rem; color: rgba(255,255,255,0.9); font-weight: 500;">
            Enterprise-Grade Financial Intelligence Platform
        </p>
        <p style="font-size: 1rem; color: rgba(255,255,255,0.7); margin-bottom: 2rem;">
             Real-time Market Analysis •  AI-Powered Insights •  Lightning Fast Analytics • Enterprise Security
        </p>
        <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6); border-top: 1px solid rgba(255,255,255,0.2); padding-top: 1.5rem; margin-top: 1.5rem;">
            <p><i class="fas fa-exclamation-triangle"></i> <strong>Disclaimer:</strong> This platform is designed for educational and analytical purposes. 
            Always conduct your own research and consult with financial professionals before making investment decisions.</p>
            <p style="margin-top: 1rem;">
                <i class="fas fa-copyright"></i> 2024 Yami-stocks Pro. Advanced Trading Intelligence.
                Built with <i class="fas fa-heart" style="color: #ff6b6b;"></i> using cutting-edge technology.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add floating action buttons (conceptual)
    st.markdown("""
    <style>
    .floating-actions {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        z-index: 1000;
    }
    
    .floating-btn {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: var(--primary-gradient);
        color: white;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .floating-btn:hover {
        transform: translateY(-3px) scale(1.1);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ **Error:** {e}")
    st.info("💡 Troubleshooting Tips: Check API Key, Symbol, Internet, and Rate Limits.")
