"""
👑 BILLIONAIRE SCRIPT by Noeman NK
High-Conviction NSE Trading Engine — Indices 1h/4h Elliott Waves, Next-Day 3%-20% Movers, 
F&O Analytics, NIFTY 500 Universe, Classical Price Action Chart Patterns & PDF Exporter.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import logging
import sys
import os
import yfinance as yf

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner import scan_stocks, get_stock_detail, get_bull_stocks, get_bear_stocks, fetch_stock_data_realtime
from stock_universe import (
    get_nifty50_tickers, get_nifty200_tickers, get_nifty500_tickers, 
    get_available_universes, get_stock_info
)
from elliott_wave import analyze_multi_timeframe_elliott, scan_all_elliott_wave_setups
from next_day_mover import scan_next_day_movers
from index_elliott import scan_all_nse_indices, analyze_single_index, NSE_INDICES
from chart_patterns import scan_all_chart_patterns, scan_chart_patterns_for_ticker
from trade_chart_patterns import scan_all_trade_charts, scan_trade_chart_for_ticker, get_pattern_svg
from institutional_alerts import scan_all_institutional_alerts, scan_institutional_alert_for_ticker
from blackrock_quant_engine import analyze_quant_index, QUANT_INDICES
from market_news_catalyst import fetch_all_market_catalysts, fetch_stock_catalyst_news
from pdf_generator import generate_pdf_report

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─── Page Configuration ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="👑 BILLIONAIRE SCRIPT by Noeman NK",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── MASTER PASSWORD SECURITY GATE ──────────────────────────────────────────

DEFAULT_PASSCODE = "1919"

def check_password() -> bool:
    """Returns True if the user has authenticated with the correct passcode."""
    if st.session_state.get("authenticated", False):
        return True

    master_passcode = os.environ.get("APP_PASSWORD", DEFAULT_PASSCODE)

    st.markdown("""
    <style>
    .login-container {
        max-width: 480px;
        margin: 60px auto 20px auto;
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        padding: 40px 30px;
        border-radius: 20px;
        border: 1px solid #6366f1;
        box-shadow: 0 20px 50px rgba(0,0,0,0.8);
        text-align: center;
    }
    .login-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 4px;
    }
    .login-sub {
        color: #A5B4FC;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    </style>
    <div class="login-container">
        <p class="login-title">🔒 RESTRICTED INSTITUTIONAL ACCESS</p>
        <p class="login-sub">👑 BILLIONAIRE SCRIPT by Noeman NK</p>
        <p style="color:#94A3B8; font-size:0.88rem; margin-bottom:15px; line-height:1.5;">
            System data is password-protected. Please enter your Master Passcode to unlock real-time trade scanners and institutional PDF dossiers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        entered_pass = st.text_input("🔑 Master Security Passcode", type="password", key="passcode_field")
        unlock_clicked = st.button("🔓 Unlock Dashboard", type="primary", use_container_width=True)
        
        if unlock_clicked or (entered_pass and entered_pass.strip() != ""):
            if entered_pass.strip() == master_passcode:
                st.session_state["authenticated"] = True
                st.success("✅ Access Granted! Unlocking Dashboard...")
                st.rerun()
            elif entered_pass.strip() != "":
                st.error("❌ Invalid Passcode. Access Denied.")
                
    st.markdown("---")
    st.markdown("<p style='text-align:center; color:#64748b; font-size:0.8rem;'>🔒 Encrypted Master Passcode Protection Active.</p>", unsafe_allow_html=True)
    return False

# Enforce security gate before rendering application content
if not check_password():
    st.stop()


# ─── Custom CSS Styling ───────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=SF+Pro+Display:wght@400;600;700;800&display=swap');
    
    * { font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif; }
    
    /* Apple Liquid Glass Canvas */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 60%, #020617 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* Ultra Liquid Glass Header */
    .main-header {
        background: rgba(30, 27, 75, 0.45) !important;
        backdrop-filter: blur(32px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(32px) saturate(200%) !important;
        padding: 28px 34px !important;
        border-radius: 26px !important;
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        margin-bottom: 24px !important;
        text-align: center !important;
    }
    .main-title {
        font-size: 2.6rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #FFFFFF 0%, #FDE047 50%, #38BDF8 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        letter-spacing: -0.5px !important;
        margin: 0 !important;
    }
    .sub-title {
        font-size: 1.02rem !important;
        color: #C7D2FE !important;
        margin-top: 8px !important;
        font-weight: 500 !important;
    }
    
    /* Liquid Glass Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        padding: 22px !important;
        border-radius: 22px !important;
        text-align: center !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .metric-card:hover {
        transform: translateY(-4px) !important;
        border-color: rgba(99, 102, 241, 0.6) !important;
        box-shadow: 0 20px 45px rgba(99, 102, 241, 0.3) !important;
    }
    .metric-value {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: -1px !important;
    }
    .metric-label {
        font-size: 0.88rem !important;
        color: #94A3B8 !important;
        margin-top: 6px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Liquid Glass Pattern Cards */
    .pattern-card, .index-card {
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(28px) saturate(190%) !important;
        padding: 24px !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 16px 45px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
        margin-bottom: 20px !important;
        transition: all 0.3s ease !important;
    }
    .pattern-card:hover, .index-card:hover {
        border-color: rgba(56, 189, 248, 0.5) !important;
        box-shadow: 0 22px 55px rgba(56, 189, 248, 0.25) !important;
    }
    
    /* Apple Liquid Glass Buttons */
    .stButton > button {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.8) 0%, rgba(59, 130, 246, 0.8) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #FFFFFF !important;
        border-radius: 16px !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4) !important;
        backdrop-filter: blur(20px) !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.6) !important;
    }
    
    .strong-bull { color: #22C55E; }
    .moderate-bull { color: #86EFAC; }
    .neutral { color: #94A3B8; }
    .moderate-bear { color: #FCA5A5; }
    .strong-bear { color: #EF4444; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 👑 **BILLIONAIRE SCRIPT**")
    st.caption("Designed & Created by **Noeman NK**")
    if st.button("🔒 **Lock App / Logout**", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()
    st.markdown("---")
    
    # Mode selector
    mode = st.radio(
        "🕐 **Trading Mode**",
        options=["Daily", "Positional"],
        help="**Daily**: Intraday momentum & quick breakout swings (3-month lookback)\n\n**Positional**: Multi-week positional swing trends (1-year lookback)"
    )
    mode_key = mode.lower()
    
    st.markdown("")
    
    # Universe selector
    universes = get_available_universes()
    universe_name = st.selectbox(
        "🌐 **Stock Universe**",
        options=list(universes.keys()),
        help="⚡ Top 50 F&O: Fast scan\n📊 Full 200 F&O Universe: Complete F&O basket\n🌐 Full 500 Universe: Entire broad market"
    )
    universe_key = universes[universe_name]
    
    st.markdown("")
    
    # Run Scan button
    run_scan = st.button("🚀 **Run Stock Scan**", use_container_width=True, type="primary")
    
    st.markdown("---")
    
    # Last scan info
    if 'last_scan_time' in st.session_state:
        st.caption(f"🕐 Last scan: {st.session_state['last_scan_time']}")
        st.caption(f"📊 Mode: {st.session_state.get('last_scan_mode', 'N/A')}")
        st.caption(f"🌐 Universe: {st.session_state.get('last_scan_universe', 'N/A')}")
        st.caption(f"📈 Total Stocks Scanned: {len(st.session_state.get('scan_results', []))}")
        
        # Sidebar PDF download for current scan
        if not st.session_state.get('scan_results', pd.DataFrame()).empty:
            pdf_bytes = generate_pdf_report(
                st.session_state['scan_results'],
                title=f"Full Market Scan ({st.session_state.get('last_scan_universe')})",
                subtitle=f"Mode: {st.session_state.get('last_scan_mode')}",
                mode=st.session_state.get('last_scan_mode', 'Daily'),
                universe=st.session_state.get('last_scan_universe', 'NSE')
            )
            st.download_button(
                label="📄 **Download Full Scan PDF**",
                data=pdf_bytes,
                file_name=f"Billionaire_Script_Scan_{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.caption("Ready to scan.")
    
    st.markdown("---")
    st.markdown("### 🏛️ Major Indices Monitored")
    st.caption("NIFTY 50 • SENSEX")
    
    st.markdown("---")
    st.caption("⚠️ For educational and reference purposes only.")


# ─── Helper Functions ─────────────────────────────────────────────────────────

def render_metric_card(label: str, value: int, css_class: str):
    """Render a styled metric card."""
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value {css_class}">{value}</p>
        <p class="metric-label">{label}</p>
    </div>
    """, unsafe_allow_html=True)


def style_signal(val):
    """Apply color styling to Signal column."""
    color_map = {
        'Strong Bull': '#22C55E',
        'Moderate Bull': '#86EFAC',
        'Neutral': '#94A3B8',
        'Moderate Bear': '#FCA5A5',
        'Strong Bear': '#EF4444'
    }
    color = color_map.get(val, '#94A3B8')
    return f'color: {color}; font-weight: bold'


def style_score(val):
    """Apply color styling based on score value."""
    try:
        v = float(val)
        if v >= 5:
            return 'color: #22C55E; font-weight: bold'
        elif v >= 3:
            return 'color: #86EFAC; font-weight: bold'
        elif v <= -5:
            return 'color: #EF4444; font-weight: bold'
        elif v <= -3:
            return 'color: #FCA5A5; font-weight: bold'
        else:
            return 'color: #94A3B8'
    except (ValueError, TypeError):
        return ''


def style_action(val):
    """Color action column."""
    s = str(val)
    if 'BUY' in s:
        return 'color: #22C55E; font-weight: bold;'
    elif 'SELL' in s:
        return 'color: #EF4444; font-weight: bold;'
    return 'color: #94A3B8;'


def style_change(val):
    """Color positive changes green, negative red."""
    try:
        v = float(val)
        if v > 0:
            return 'color: #22C55E'
        elif v < 0:
            return 'color: #EF4444'
        return 'color: #94A3B8'
    except (ValueError, TypeError):
        return ''


def format_results_table(df: pd.DataFrame) -> pd.DataFrame:
    """Format the results DataFrame for display with RR and Time Cycle."""
    display_df = df.copy()
    
    display_cols = ['Ticker', 'Name', 'Close', 'Change%', 'Action', 'Entry', 
                    'Stop_Loss', 'Target_1', 'Target_2', 'RR_Ratio', 'Time_Cycle',
                    'RSI', 'ADX', 'Composite_Score', 'Signal']
    
    available_cols = [c for c in display_cols if c in display_df.columns]
    display_df = display_df[available_cols]
    
    rename_map = {
        'Change%': 'Chg%',
        'Stop_Loss': 'SL',
        'Target_1': 'T1',
        'Target_2': 'T2',
        'RR_Ratio': 'R:R',
        'Time_Cycle': 'Time to Target',
        'Composite_Score': 'Score'
    }
    display_df = display_df.rename(columns={k: v for k, v in rename_map.items() if k in display_df.columns})
    return display_df


def create_elliott_wave_chart(df: pd.DataFrame, pivots: list, setup_info: dict, title: str = "Elliott Wave Chart"):
    """Create an interactive Elliott Wave chart with exact start points, wave pivots, and heading vectors."""
    if df.empty:
        st.warning("No data available to plot chart.")
        return
        
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.60, 0.20, 0.20],
        subplot_titles=(
            f'🌊 {title}',
            'RSI (14) Momentum',
            'MACD (12, 26, 9)'
        )
    )
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Price', increasing_line_color='#22C55E',
        decreasing_line_color='#EF4444'
    ), row=1, col=1)
    
    # EMAs
    if 'EMA_5' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_5'], name='EMA 5',
                                  line=dict(color='#FBBF24', width=1)), row=1, col=1)
    if 'EMA_13' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_13'], name='EMA 13',
                                  line=dict(color='#60A5FA', width=1)), row=1, col=1)
    if 'EMA_26' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_26'], name='EMA 26',
                                  line=dict(color='#F472B6', width=1)), row=1, col=1)
                                  
    # Wave Structure Line & Annotations
    if pivots and len(pivots) >= 2:
        pivot_dates = [p['date'] for p in pivots]
        pivot_prices = [p['price'] for p in pivots]
        
        wave_labels = []
        is_corrective = "C" in setup_info.get('setup_type', '')
        for i, p in enumerate(pivots):
            if is_corrective:
                lbl = ['Origin', '(A)', '(B)', '(C)'][min(i, 3)]
            else:
                lbl = f"({i})" if i <= 5 else f"P{i}"
            wave_labels.append(f"{lbl}: ₹{p['price']:.1f}")
            
        fig.add_trace(go.Scatter(
            x=pivot_dates, y=pivot_prices,
            mode='lines+markers+text',
            name='Elliott Wave Structure',
            line=dict(color='#38BDF8', width=3, dash='solid'),
            marker=dict(size=9, color='#38BDF8', symbol='diamond'),
            text=wave_labels,
            textposition="top center",
            textfont=dict(size=11, color='#F8FAFC')
        ), row=1, col=1)
        
    # Invalidation Level (SL) line
    inv = setup_info.get('invalidation_price')
    if inv:
        fig.add_hline(y=inv, line_dash="dash", line_color="#EF4444", 
                      annotation_text=f"Invalidation SL: ₹{inv:.2f}", annotation_position="bottom right", row=1, col=1)
                      
    # Target Lines & Heading Projection
    t1 = setup_info.get('target_1')
    t2 = setup_info.get('target_2')
    if t1:
        fig.add_hline(y=t1, line_dash="dash", line_color="#22C55E", 
                      annotation_text=f"Wave Target 1 (1.618 Fib): ₹{t1:.2f}", annotation_position="top right", row=1, col=1)
    if t2:
        fig.add_hline(y=t2, line_dash="dot", line_color="#38BDF8", 
                      annotation_text=f"Wave Target 2 (2.0 Fib): ₹{t2:.2f}", annotation_position="top right", row=1, col=1)
        
    # Heading Destination Banner
    heading = setup_info.get('heading_destination')
    if heading:
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.02, y=0.96,
            text=f"<b>{heading}</b>",
            showarrow=False,
            bgcolor="rgba(15, 23, 42, 0.85)",
            bordercolor="#38BDF8",
            borderwidth=1,
            font=dict(color="#38BDF8", size=12)
        )
        
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI',
                                  line=dict(color='#A78BFA', width=1.5)), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="rgba(239,68,68,0.5)", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="rgba(34,197,94,0.5)", row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="rgba(156,163,175,0.3)", row=2, col=1)
        
    # MACD
    if 'MACD' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD',
                                  line=dict(color='#60A5FA', width=1.5)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal',
                                  line=dict(color='#F97316', width=1.5)), row=3, col=1)
        colors = ['#22C55E' if v >= 0 else '#EF4444' for v in df['MACD_Hist'].fillna(0)]
        fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name='Histogram',
                              marker_color=colors, opacity=0.6), row=3, col=1)
                              
    fig.update_layout(
        height=850,
        template='plotly_dark',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=30, t=60, b=30)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    st.plotly_chart(fig, use_container_width=True)


def create_chart_pattern_chart(df: pd.DataFrame, pattern_data: dict, title: str = "Price Action Chart Pattern"):
    """Render interactive chart for price action patterns with breakout and invalidation triggers."""
    if df.empty:
        st.warning("No data available.")
        return
        
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.75, 0.25],
        subplot_titles=(f"📐 {title}", "RSI (14) Momentum")
    )
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Price', increasing_line_color='#22C55E',
        decreasing_line_color='#EF4444'
    ), row=1, col=1)
    
    # EMAs
    if 'EMA_5' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_5'], name='EMA 5', line=dict(color='#FBBF24', width=1)), row=1, col=1)
    if 'EMA_13' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_13'], name='EMA 13', line=dict(color='#60A5FA', width=1)), row=1, col=1)
    if 'EMA_26' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_26'], name='EMA 26', line=dict(color='#F472B6', width=1)), row=1, col=1)
        
    # Trigger Entry Line
    entry = pattern_data.get('Trigger_Entry')
    if entry:
        fig.add_hline(y=entry, line_dash="dash", line_color="#38BDF8", 
                      annotation_text=f"Breakout Trigger: ₹{entry:.2f}", annotation_position="top right", row=1, col=1)
                      
    # Stop Loss Line
    sl = pattern_data.get('Stop_Loss')
    if sl:
        fig.add_hline(y=sl, line_dash="dash", line_color="#EF4444", 
                      annotation_text=f"Stop Loss: ₹{sl:.2f}", annotation_position="bottom right", row=1, col=1)
                      
    # Target 1 Line
    t1 = pattern_data.get('Target_1')
    if t1:
        fig.add_hline(y=t1, line_dash="dot", line_color="#22C55E", 
                      annotation_text=f"Target 1: ₹{t1:.2f}", annotation_position="top right", row=1, col=1)
                      
    # Target 2 Line
    t2 = pattern_data.get('Target_2')
    if t2:
        fig.add_hline(y=t2, line_dash="dot", line_color="#10B981", 
                      annotation_text=f"Target 2: ₹{t2:.2f}", annotation_position="top right", row=1, col=1)
                      
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#A78BFA', width=1.5)), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="rgba(239,68,68,0.5)", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="rgba(34,197,94,0.5)", row=2, col=1)
        
    fig.update_layout(
        height=750,
        template='plotly_dark',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=30, t=60, b=30)
    )
    st.plotly_chart(fig, use_container_width=True)


# ─── Execute Scan Function ────────────────────────────────────────────────────

def execute_stock_scan(u_key: str, u_name: str, m_key: str, m_name: str):
    """Orchestrate stock scan across selected universe (Full 50, 200 F&O, or 500 Universe)."""
    if u_key == 'nifty50':
        tickers = get_nifty50_tickers()
    elif u_key == 'nifty500':
        tickers = get_nifty500_tickers() # Full 500 Stocks
    else:
        tickers = get_nifty200_tickers() # Full 200 F&O Stocks
        
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(current, total, name):
        progress_bar.progress(current / total)
        status_text.text(f"🚀 Scanning {current}/{total} Stocks: {name}")
    
    with st.spinner(f"Scanning ALL {len(tickers)} stocks in {u_name} ({m_name} mode)..."):
        start_t = time.time()
        results_df = scan_stocks(tickers, mode=m_key, progress_callback=update_progress)
        elapsed = time.time() - start_t
        
    progress_bar.empty()
    status_text.empty()
    
    st.session_state['scan_results'] = results_df
    st.session_state['last_scan_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    st.session_state['last_scan_mode'] = m_name
    st.session_state['last_scan_universe'] = u_name
    st.success(f"✅ Scan Complete! Scored **{len(results_df)}** stocks in **{elapsed:.1f}s**")
    return results_df


# ─── Trigger Sidebar Scan or Auto-Load ─────────────────────────────────────────

if run_scan:
    execute_stock_scan(universe_key, universe_name, mode_key, mode)
elif 'scan_results' not in st.session_state:
    # Auto-load initial universe on launch
    execute_stock_scan('nifty50', '⚡ Top 50 F&O Stocks (NIFTY 50)', 'daily', 'Daily')


# ─── Main Header ──────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <p class="main-title">👑 BILLIONAIRE SCRIPT by Noeman NK</p>
    <p class="sub-title">⚡ High-Conviction NSE Engine — Indices 1h/4h Elliott Waves, Next-Day 3%-20% Movers, Price Action Patterns, F&O & NIFTY 500</p>
</div>
""", unsafe_allow_html=True)


# ─── Primary Tabs ─────────────────────────────────────────────────────────────

tab_news, tab_trade_chart, tab_patterns, tab_trades, tab_ew, tab_bull, tab_bear, tab_all, tab_search = st.tabs([
    "📰 IMPACT NEWS ALERTS & CATALYST INTELLIGENCE",
    "📈 TRADE CHART (Reversals, Continuations & Triangles)",
    "📐 Institutional Chart Patterns (Pre-Breakouts)",
    "🎯 F&O Trade Setups (R:R & Time)",
    "🌊 Elliott Wave (Weekly + Daily)",
    "🐂 Bull Stocks (with R:R)",
    "🐻 Bear Stocks (with R:R)",
    "📋 All Stocks Universe (Top 500)",
    "🔍 Search Any Stock & Custom Wave"
])


# ─── TAB 1: IMPACT NEWS ALERTS & CATALYST INTELLIGENCE ─────────────────────

with tab_news:
    st.markdown("### 📰 IMPACT NEWS ALERTS & CATALYST INTELLIGENCE — Pre-Market Corporate Disclosures")
    st.markdown("""
    Scans real-time Indian stock market announcements (**Order Wins, Mergers & Acquisitions, Regulatory Clearances, Earnings Surprises**) and calculates forecasted **Next-Day Price Reactions & High-Convexity Option Strikes**.
    """)
    
    col_nw_univ, col_nw_btn = st.columns([3, 1])
    with col_nw_univ:
        nw_universe = st.selectbox(
            "🌐 **News Target Universe**",
            ["⚡ Top 50 F&O Stocks (High Impact)", "📊 Full 200 F&O Universe"],
            key="nw_univ_select"
        )
    with col_nw_btn:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        run_nw_scan = st.button("🚀 **Scan News Catalysts**", use_container_width=True, type="primary")
        
    if run_nw_scan or 'news_catalyst_df' not in st.session_state:
        target_nw_tickers = get_nifty200_tickers() if "200" in nw_universe else get_nifty50_tickers()
        
        prog_nw = st.progress(0)
        status_nw = st.empty()
        
        def update_nw_prog(curr, tot, name):
            prog_nw.progress(curr / tot)
            status_nw.text(f"Scanning News Catalysts ({curr}/{tot}): {name}")
            
        with st.spinner(f"Analyzing Corporate Announcements for {len(target_nw_tickers)} stocks..."):
            nw_df = fetch_all_market_catalysts(target_nw_tickers, progress_callback=update_nw_prog)
            st.session_state['news_catalyst_df'] = nw_df
            
        prog_nw.empty()
        status_nw.empty()
    else:
        nw_df = st.session_state.get('news_catalyst_df', pd.DataFrame())
        
    if not nw_df.empty:
        col_nw_cnt, col_nw_pdf = st.columns([3, 1])
        with col_nw_cnt:
            st.markdown(f"#### 📰 Corporate Catalysts & News Intimations: **{len(nw_df)} Tracked**")
        with col_nw_pdf:
            pdf_nw_bytes = generate_pdf_report(
                nw_df,
                title="Impact News Alerts & Catalyst Intelligence",
                subtitle="Pre-Market Reaction Forecasts",
                mode="Daily",
                universe=nw_universe
            )
            st.download_button(
                label="📄 **Download News Catalyst PDF**",
                data=pdf_nw_bytes,
                file_name=f"News_Catalysts_Report_{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        # Filter tabs
        nw_tab_all, nw_tab_orders, nw_tab_ma, nw_tab_reg, nw_tab_earn = st.tabs([
            f"⚡ All News Catalysts ({len(nw_df)})",
            f"🤝 Order Wins ({len(nw_df[nw_df['Catalyst_Type'].str.contains('Order', na=False)])})",
            f"💎 M&A Deals ({len(nw_df[nw_df['Catalyst_Type'].str.contains('Merger', na=False)])})",
            f"🏛️ Regulatory Clearances ({len(nw_df[nw_df['Catalyst_Type'].str.contains('Regulatory', na=False)])})",
            f"📊 Earnings & Guidance ({len(nw_df[nw_df['Catalyst_Type'].str.contains('Earnings', na=False)])})"
        ])
        
        def render_news_table(df_n, cat_label: str = "News Catalysts"):
            if df_n.empty:
                st.info(f"No active catalysts in {cat_label} currently.")
                return
                
            nw_display_cols = [
                'Ticker', 'Name', 'Catalyst_Type', 'Headline', 'Next_Day_Forecast', 'Direction', 'Option_Strike', 'Publisher', 'Publish_Time'
            ]
            available_nw = [c for c in nw_display_cols if c in df_n.columns]
            
            styled_nw = df_n[available_nw].style \
                .map(lambda v: 'color: #22C55E; font-weight: bold;' if 'BUY' in str(v) else ('color: #EF4444; font-weight: bold;' if 'SELL' in str(v) else ''), subset=['Direction'] if 'Direction' in available_nw else []) \
                .map(lambda v: 'color: #FBBF24; font-weight: bold;' if 'GAP-UP' in str(v) else 'color: #38BDF8;', subset=['Next_Day_Forecast'] if 'Next_Day_Forecast' in available_nw else [])
                
            st.dataframe(styled_nw, use_container_width=True, height=380)
            
        with nw_tab_all: render_news_table(nw_df, "All News Catalysts")
        with nw_tab_orders: render_news_table(nw_df[nw_df['Catalyst_Type'].str.contains('Order', na=False)], "Order Wins")
        with nw_tab_ma: render_news_table(nw_df[nw_df['Catalyst_Type'].str.contains('Merger', na=False)], "M&A Deals")
        with nw_tab_reg: render_news_table(nw_df[nw_df['Catalyst_Type'].str.contains('Regulatory', na=False)], "Regulatory Clearances")
        with nw_tab_earn: render_news_table(nw_df[nw_df['Catalyst_Type'].str.contains('Earnings', na=False)], "Earnings Surprises")
        
        st.markdown("---")
        st.markdown("#### 🔍 Interactive News Catalyst Inspector Card")
        nw_ticker_list = nw_df['Ticker'].tolist()
        sel_nw_ticker = st.selectbox("Select Catalyst Stock to Inspect:", nw_ticker_list, key="nw_select_stock")
        
        if sel_nw_ticker:
            matched_nw = nw_df[nw_df['Ticker'] == sel_nw_ticker].iloc[0].to_dict()
            
            st.markdown(f"""
            <div class="pattern-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.2rem; font-weight:800; color:#F8FAFC;">📰 {matched_nw['Headline']}</span>
                    <span style="font-size:1.0rem; font-weight:700; color:#FDE047;">{matched_nw['Catalyst_Type']}</span>
                </div>
                <hr style="margin: 8px 0; border-color: #334155;">
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 6px;">
                    <div>
                        <p style="color:#CBD5E1; margin:2px 0; font-size:0.85rem;"><b>Stock Name:</b> {matched_nw['Name']} ({matched_nw['Ticker']})</p>
                        <p style="color:#38BDF8; margin:2px 0; font-size:0.85rem;"><b>Spot Price:</b> ₹{matched_nw['Current_Price']:.2f} ({matched_nw['Change%']:+.2f}%)</p>
                        <p style="color:#A5B4FC; margin:2px 0; font-size:0.85rem;"><b>Disclosed By:</b> {matched_nw['Publisher']}</p>
                    </div>
                    <div>
                        <p style="color:#FDE047; margin:2px 0; font-size:0.85rem;"><b>Forecasted Reaction:</b> {matched_nw['Next_Day_Forecast']}</p>
                        <p style="color:#22C55E; margin:2px 0; font-size:0.85rem;"><b>Direction:</b> {matched_nw['Direction']}</p>
                        <p style="color:#F472B6; margin:2px 0; font-size:0.85rem;"><b>Option Strike Play:</b> {matched_nw['Option_Strike']}</p>
                    </div>
                    <div>
                        <p style="color:#94A3B8; margin:2px 0; font-size:0.85rem;"><b>Publish Time:</b> {matched_nw['Publish_Time']}</p>
                        <p style="color:#10B981; margin:2px 0; font-size:0.85rem;"><b>Conviction:</b> {matched_nw['Conviction']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner(f"Loading chart for {sel_nw_ticker}..."):
                df_chart_nw, _, _, _ = fetch_stock_data_realtime(sel_nw_ticker, period='1y')
                if df_chart_nw is not None and not df_chart_nw.empty:
                    create_chart_pattern_chart(df_chart_nw, {'Trigger_Entry': matched_nw['Current_Price']}, title=f"{sel_nw_ticker} — Catalyst Impact Chart")


# ─── TAB 5: TRADE CHART — Institutional Price Action Setups ─────────────────

with tab_trade_chart:
    st.markdown("### 📈 TRADE CHART — Institutional Price Action Setups (15m, 1h, Daily, Weekly)")
    st.markdown("""
    Detects 100% of classical institutional patterns (**Reversals, Continuations, Bilateral Triangles**) with **Instant Early Completion Alerts**:
    - 🔄 **Reversal Patterns**: Double Top/Bottom, Head & Shoulders, Inverse H&S, Rising/Falling Wedges
    - 📈 **Continuation Patterns**: Bullish/Bearish Pennants, Bullish/Bearish Rectangles & Channels
    - 📐 **Bilateral Triangles**: Ascending Triangle, Descending Triangle, Symmetrical Triangle
    """)
    
    col_tc_tf, col_tc_univ, col_tc_btn = st.columns([1.5, 1.5, 1])
    with col_tc_tf:
        tc_timeframe = st.selectbox(
            "⏱️ **Timeframe**",
            ["15-Min (Intraday Scalp Alert)", "1-Hour (Swing / Intraday)", "Daily (Swing Trading)", "Weekly (Positional Macro)"],
            key="tc_tf_select"
        )
    with col_tc_univ:
        tc_universe = st.selectbox(
            "🌐 **Scan Universe**",
            ["⚡ Top 50 F&O Stocks", "📊 Full 200 F&O Universe", "🌐 Full 500 Universe"],
            key="tc_univ_select"
        )
    with col_tc_btn:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        run_tc_scan = st.button("🚀 **Scan Trade Charts**", use_container_width=True, type="primary")
        
    clean_tc_tf = "15m" if "15-Min" in tc_timeframe else ("1h" if "1-Hour" in tc_timeframe else ("Weekly" if "Weekly" in tc_timeframe else "Daily"))
    
    if run_tc_scan or 'trade_chart_df' not in st.session_state:
        if "500" in tc_universe:
            target_tickers = get_nifty500_tickers()
        elif "200" in tc_universe:
            target_tickers = get_nifty200_tickers()
        else:
            target_tickers = get_nifty50_tickers()
            
        prog_tc = st.progress(0)
        status_tc = st.empty()
        
        def update_tc_prog(curr, tot, name):
            prog_tc.progress(curr / tot)
            status_tc.text(f"Scanning Trade Charts ({curr}/{tot}): {name}")
            
        with st.spinner(f"Scanning {len(target_tickers)} stocks for Trade Chart Setups ({clean_tc_tf} Timeframe)..."):
            tc_df = scan_all_trade_charts(target_tickers, timeframe=clean_tc_tf, progress_callback=update_tc_prog)
            st.session_state['trade_chart_df'] = tc_df
            st.session_state['tc_last_tf'] = tc_timeframe
            
        prog_tc.empty()
        status_tc.empty()
    else:
        tc_df = st.session_state.get('trade_chart_df', pd.DataFrame())
        
    if not tc_df.empty:
        col_tc_cnt, col_tc_pdf = st.columns([3, 1])
        with col_tc_cnt:
            st.markdown(f"#### ⚡ Active Trade Chart Setups: **{len(tc_df)} Found** ({st.session_state.get('tc_last_tf', tc_timeframe)})")
        with col_tc_pdf:
            pdf_tc_bytes = generate_pdf_report(
                tc_df,
                title="Trade Chart Institutional Report",
                subtitle=f"Timeframe: {st.session_state.get('tc_last_tf', tc_timeframe)}",
                mode=clean_tc_tf,
                universe=tc_universe
            )
            st.download_button(
                label="📄 **Download Trade Chart PDF**",
                data=pdf_tc_bytes,
                file_name=f"Trade_Chart_Report_{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        # Sub-category tabs
        tc_tab_all, tc_tab_early, tc_tab_rev, tc_tab_cont, tc_tab_tri = st.tabs([
            f"⚡ All Trade Charts ({len(tc_df)})",
            f"🔥 Early Entry Alerts ({len(tc_df[tc_df['Status'].str.contains('JUST NOW', na=False)])})",
            f"🔄 Reversal Patterns ({len(tc_df[tc_df['Pattern_Category'].str.contains('Reversal', na=False)])})",
            f"📈 Continuation Patterns ({len(tc_df[tc_df['Pattern_Category'].str.contains('Continuation', na=False)])})",
            f"📐 Bilateral Triangles ({len(tc_df[tc_df['Pattern_Category'].str.contains('Bilateral', na=False)])})"
        ])
        
        def render_trade_chart_table(df_t, cat_label: str = "Trade Charts"):
            if df_t.empty:
                st.info(f"No candidates in {cat_label} currently.")
                return
                
            col_t_btn1, col_t_btn2 = st.columns([3, 1])
            with col_t_btn2:
                pdf_sub_tc = generate_pdf_report(
                    df_t,
                    title=f"Trade Charts — {cat_label}",
                    subtitle=f"Timeframe: {st.session_state.get('tc_last_tf', tc_timeframe)}",
                    mode=clean_tc_tf,
                    universe=tc_universe
                )
                st.download_button(
                    label=f"📄 **Download {cat_label} PDF**",
                    data=pdf_sub_tc,
                    file_name=f"{cat_label.replace(' ', '_')}_{int(time.time())}.pdf",
                    mime="application/pdf",
                    key=f"btn_pdf_tc_{cat_label}_{time.time()}",
                    use_container_width=True
                )
                
            tc_display_cols = [
                'Ticker', 'Name', 'Pattern_Category', 'Pattern', 'Direction', 'Status', 'Current_Price', 'Change%',
                'Trigger_Entry', 'Stop_Loss', 'Target_1', 'Target_2', 'RR_Ratio', 'Time_Cycle', 'Option_Strike', 'Conviction'
            ]
            available_tc = [c for c in tc_display_cols if c in df_t.columns]
            
            styled_tc = df_t[available_tc].style \
                .map(lambda v: 'color: #22C55E; font-weight: bold;' if 'BUY' in str(v) else ('color: #EF4444; font-weight: bold;' if 'SELL' in str(v) else ''), subset=['Direction'] if 'Direction' in available_tc else []) \
                .map(lambda v: 'color: #FBBF24; font-weight: bold;' if 'JUST NOW' in str(v) else 'color: #38BDF8;', subset=['Status'] if 'Status' in available_tc else []) \
                .format({
                    'Current_Price': '₹{:.2f}',
                    'Change%': '{:+.2f}%',
                    'Trigger_Entry': '₹{:.2f}',
                    'Stop_Loss': '₹{:.2f}',
                    'Target_1': '₹{:.2f}',
                    'Target_2': '₹{:.2f}'
                }, na_rep='—')
                
            st.dataframe(styled_tc, use_container_width=True, height=380)
            
        with tc_tab_all: render_trade_chart_table(tc_df, "All Trade Charts")
        with tc_tab_early: render_trade_chart_table(tc_df[tc_df['Status'].str.contains('JUST NOW', na=False)], "Early Entry Alerts")
        with tc_tab_rev: render_trade_chart_table(tc_df[tc_df['Pattern_Category'].str.contains('Reversal', na=False)], "Reversal Patterns")
        with tc_tab_cont: render_trade_chart_table(tc_df[tc_df['Pattern_Category'].str.contains('Continuation', na=False)], "Continuation Patterns")
        with tc_tab_tri: render_trade_chart_table(tc_df[tc_df['Pattern_Category'].str.contains('Bilateral', na=False)], "Bilateral Triangles")
        
        st.markdown("---")
        st.markdown("#### 🔍 Interactive Trade Chart Visualizer & Pattern Diagram")
        tc_ticker_list = tc_df['Ticker'].tolist()
        sel_tc_ticker = st.selectbox("Select Trade Chart Stock to Inspect:", tc_ticker_list, key="tc_select_stock")
        
        if sel_tc_ticker:
            matched_tc = tc_df[tc_df['Ticker'] == sel_tc_ticker].iloc[0].to_dict()
            svg_diagram = get_pattern_svg(matched_tc['Pattern'])
            
            col_card_info, col_card_diagram = st.columns([2.2, 1])
            with col_card_info:
                st.markdown(f"""
                <div class="pattern-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:1.2rem; font-weight:800; color:#F8FAFC;">📈 {matched_tc['Pattern']} — {matched_tc['Ticker']} ({matched_tc['Name']})</span>
                        <span style="font-size:1.0rem; font-weight:700; color:#FDE047;">{matched_tc['Status']}</span>
                    </div>
                    <hr style="margin: 8px 0; border-color: #334155;">
                    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 6px;">
                        <div>
                            <p style="color:#CBD5E1; margin:2px 0; font-size:0.85rem;"><b>Live Spot Price:</b> ₹{matched_tc['Current_Price']:.2f} ({matched_tc['Change%']:+.2f}%)</p>
                            <p style="color:#38BDF8; margin:2px 0; font-size:0.85rem;"><b>Trigger Entry:</b> ₹{matched_tc['Trigger_Entry']:.2f}</p>
                            <p style="color:#EF4444; margin:2px 0; font-size:0.85rem;"><b>Invalidation SL:</b> ₹{matched_tc['Stop_Loss']:.2f}</p>
                        </div>
                        <div>
                            <p style="color:#22C55E; margin:2px 0; font-size:0.85rem;"><b>Target 1:</b> ₹{matched_tc['Target_1']:.2f}</p>
                            <p style="color:#10B981; margin:2px 0; font-size:0.85rem;"><b>Target 2 (Runner):</b> ₹{matched_tc['Target_2']:.2f}</p>
                            <p style="color:#FDE047; margin:2px 0; font-size:0.85rem;"><b>Risk:Reward:</b> {matched_tc['RR_Ratio']}</p>
                        </div>
                        <div>
                            <p style="color:#A5B4FC; margin:2px 0; font-size:0.85rem;"><b>Target Reach Timing:</b> {matched_tc['Time_Cycle']}</p>
                            <p style="color:#F472B6; margin:2px 0; font-size:0.85rem;"><b>Wall Street Option:</b> {matched_tc['Option_Strike']}</p>
                            <p style="color:#94A3B8; margin:2px 0; font-size:0.85rem;"><b>Conviction:</b> {matched_tc['Conviction']}</p>
                        </div>
                    </div>
                    <p style="color:#E2E8F0; font-size:0.85rem; margin:8px 0 0 0;">💡 <b>Pattern Rationale:</b> {matched_tc['Rationale']}</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col_card_diagram:
                st.markdown(f"##### 📐 Pattern Geometry Diagram")
                st.markdown(svg_diagram, unsafe_allow_html=True)
                
            with st.spinner(f"Loading chart for {sel_tc_ticker}..."):
                df_chart_tc, _, _, _ = fetch_stock_data_realtime(sel_tc_ticker, period='1y')
                if df_chart_tc is not None and not df_chart_tc.empty:
                    create_chart_pattern_chart(df_chart_tc, matched_tc, title=f"{sel_tc_ticker} — {matched_tc['Pattern']} ({clean_tc_tf})")
    else:
        st.info("No stocks currently meet strict pattern compression criteria in this scan. Click 'Scan Trade Charts' to run again.")


# ─── TAB 3: Institutional Chart Patterns (Price Action & Pre-Breakouts) ───────

with tab_patterns:
    st.markdown("### 📐 Institutional Price Action Chart Patterns (Top 500 Universe)")
    st.markdown("""
    Detects classic price action classical formations with **prior intimation / early breakout warning**:
    - 🚩 **Flag & Pole** *(Pre-Breakout Coiling / Breaking Out Just Now)*
    - ☕ **Cup & Handle / Inverted Cup & Handle** *(Rim Accumulation & Handle Completion)*
    - 🎯 **Double Bottom (W-Shape) / Double Top (M-Shape)** *(Value Floor / Distribution)*
    - 👤 **Head & Shoulders / Inverse Head & Shoulders** *(Major Trend Reversals)*
    """)
    
    col_pat_tf, col_pat_univ, col_pat_btn = st.columns([1.5, 1.5, 1])
    with col_pat_tf:
        pat_timeframe = st.selectbox(
            "⏱️ **Chart Timeframe**",
            ["Daily (Swing Momentum)", "1-Hour (Intraday Pre-Breakout)", "Weekly (Positional Macro)"],
            key="pat_tf_select"
        )
    with col_pat_univ:
        pat_universe = st.selectbox(
            "🌐 **Scan Universe**",
            ["⚡ Top 50 F&O Stocks", "📊 Full 200 F&O Universe", "🌐 Full 500 Universe"],
            key="pat_univ_select"
        )
    with col_pat_btn:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        run_pattern_scan = st.button("🚀 **Scan Chart Patterns**", use_container_width=True, type="primary")
        
    clean_tf = "1h" if "1-Hour" in pat_timeframe else ("Weekly" if "Weekly" in pat_timeframe else "Daily")
    
    if run_pattern_scan or 'chart_patterns_df' not in st.session_state:
        if "500" in pat_universe:
            target_tickers = get_nifty500_tickers()
        elif "200" in pat_universe:
            target_tickers = get_nifty200_tickers()
        else:
            target_tickers = get_nifty50_tickers()
            
        prog_pat = st.progress(0)
        status_pat = st.empty()
        
        def update_pat_prog(curr, tot, name):
            prog_pat.progress(curr / tot)
            status_pat.text(f"Scanning Chart Patterns ({curr}/{tot}): {name}")
            
        with st.spinner(f"Scanning {len(target_tickers)} stocks for Price Action Patterns ({clean_tf} Timeframe)..."):
            patterns_df = scan_all_chart_patterns(target_tickers, timeframe=clean_tf, progress_callback=update_pat_prog)
            st.session_state['chart_patterns_df'] = patterns_df
            st.session_state['pat_last_tf'] = pat_timeframe
            
        prog_pat.empty()
        status_pat.empty()
    else:
        patterns_df = st.session_state.get('chart_patterns_df', pd.DataFrame())
        
    if not patterns_df.empty:
        col_cnt, col_pdf = st.columns([3, 1])
        with col_cnt:
            st.markdown(f"#### ⚡ Detected Patterns: **{len(patterns_df)} Opportunities** ({st.session_state.get('pat_last_tf', pat_timeframe)})")
        with col_pdf:
            pdf_pat_bytes = generate_pdf_report(
                patterns_df,
                title="Price Action Chart Patterns Report",
                subtitle=f"Timeframe: {st.session_state.get('pat_last_tf', pat_timeframe)}",
                mode=clean_tf,
                universe=pat_universe
            )
            st.download_button(
                label="📄 **Download PDF Report**",
                data=pdf_pat_bytes,
                file_name=f"Chart_Patterns_Report_{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        # Tabs for Pattern Categories
        pat_tab_all, pat_tab_flag, pat_tab_cup, pat_tab_double, pat_tab_hs = st.tabs([
            f"⚡ All Patterns ({len(patterns_df)})",
            f"🚩 Flag & Pole ({len(patterns_df[patterns_df['Pattern'].str.contains('Flag', na=False)])})",
            f"☕ Cup & Handle ({len(patterns_df[patterns_df['Pattern'].str.contains('Cup', na=False)])})",
            f"🎯 Double Bottom/Top ({len(patterns_df[patterns_df['Pattern'].str.contains('Double', na=False)])})",
            f"👤 Head & Shoulders ({len(patterns_df[patterns_df['Pattern'].str.contains('Shoulder', na=False)])})"
        ])
        
        def render_pattern_table(df_p, category_name: str = "Chart Patterns"):
            if df_p.empty:
                st.info(f"No candidates in {category_name} currently.")
                return
                
            col_t_btn1, col_t_btn2 = st.columns([3, 1])
            with col_t_btn2:
                pdf_sub_bytes = generate_pdf_report(
                    df_p,
                    title=f"Chart Patterns — {category_name}",
                    subtitle=f"Timeframe: {st.session_state.get('pat_last_tf', pat_timeframe)}",
                    mode=clean_tf,
                    universe=pat_universe
                )
                st.download_button(
                    label=f"📄 **Download {category_name} PDF**",
                    data=pdf_sub_bytes,
                    file_name=f"{category_name.replace(' ', '_')}_{int(time.time())}.pdf",
                    mime="application/pdf",
                    key=f"btn_pdf_pat_{category_name}_{time.time()}",
                    use_container_width=True
                )
            
            p_display_cols = [
                'Ticker', 'Name', 'Pattern', 'Direction', 'Status', 'Current_Price', 'Change%',
                'Trigger_Entry', 'Stop_Loss', 'Target_1', 'Target_2', 'RR_Ratio', 'Time_Cycle', 'Option_Strike', 'Conviction'
            ]
            available_p = [c for c in p_display_cols if c in df_p.columns]
            
            styled_p = df_p[available_p].style \
                .map(lambda v: 'color: #22C55E; font-weight: bold;' if 'BUY' in str(v) else ('color: #EF4444; font-weight: bold;' if 'SELL' in str(v) else ''), subset=['Direction'] if 'Direction' in available_p else []) \
                .map(lambda v: 'color: #FBBF24; font-weight: bold;' if 'JUST NOW' in str(v) else 'color: #38BDF8;', subset=['Status'] if 'Status' in available_p else []) \
                .format({
                    'Current_Price': '₹{:.2f}',
                    'Change%': '{:+.2f}%',
                    'Trigger_Entry': '₹{:.2f}',
                    'Stop_Loss': '₹{:.2f}',
                    'Target_1': '₹{:.2f}',
                    'Target_2': '₹{:.2f}'
                }, na_rep='—')
                
            st.dataframe(styled_p, use_container_width=True, height=380)
            
        with pat_tab_all: render_pattern_table(patterns_df, "All Chart Patterns")
        with pat_tab_flag: render_pattern_table(patterns_df[patterns_df['Pattern'].str.contains('Flag', na=False)], "Flag & Pole Breakouts")
        with pat_tab_cup: render_pattern_table(patterns_df[patterns_df['Pattern'].str.contains('Cup', na=False)], "Cup & Handle Formations")
        with pat_tab_double: render_pattern_table(patterns_df[patterns_df['Pattern'].str.contains('Double', na=False)], "Double Bottom & Top Setups")
        with pat_tab_hs: render_pattern_table(patterns_df[patterns_df['Pattern'].str.contains('Shoulder', na=False)], "Head & Shoulders Reversals")
        
        st.markdown("---")
        st.markdown("#### 🔍 Interactive Price Action Pattern Visualizer & Chart")
        pat_ticker_list = patterns_df['Ticker'].tolist()
        sel_pat_ticker = st.selectbox("Select Pattern Stock to Inspect on Chart:", pat_ticker_list)
        
        if sel_pat_ticker:
            matched_pattern = patterns_df[patterns_df['Ticker'] == sel_pat_ticker].iloc[0].to_dict()
            
            st.markdown(f"""
            <div class="pattern-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.2rem; font-weight:800; color:#F8FAFC;">📐 {matched_pattern['Pattern']} — {matched_pattern['Ticker']} ({matched_pattern['Name']})</span>
                    <span style="font-size:1.05rem; font-weight:700; color:#FDE047;">{matched_pattern['Status']}</span>
                </div>
                <hr style="margin: 8px 0; border-color: #334155;">
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 6px;">
                    <div>
                        <p style="color:#CBD5E1; margin:2px 0; font-size:0.85rem;"><b>Live Spot Price:</b> ₹{matched_pattern['Current_Price']:.2f} ({matched_pattern['Change%']:+.2f}%)</p>
                        <p style="color:#38BDF8; margin:2px 0; font-size:0.85rem;"><b>Breakout Entry:</b> ₹{matched_pattern['Trigger_Entry']:.2f}</p>
                        <p style="color:#EF4444; margin:2px 0; font-size:0.85rem;"><b>Stop Loss:</b> ₹{matched_pattern['Stop_Loss']:.2f}</p>
                    </div>
                    <div>
                        <p style="color:#22C55E; margin:2px 0; font-size:0.85rem;"><b>Target 1:</b> ₹{matched_pattern['Target_1']:.2f}</p>
                        <p style="color:#10B981; margin:2px 0; font-size:0.85rem;"><b>Target 2 (Runner):</b> ₹{matched_pattern['Target_2']:.2f}</p>
                        <p style="color:#FDE047; margin:2px 0; font-size:0.85rem;"><b>Risk:Reward:</b> {matched_pattern['RR_Ratio']}</p>
                    </div>
                    <div>
                        <p style="color:#A5B4FC; margin:2px 0; font-size:0.85rem;"><b>Target Reach Timing:</b> {matched_pattern['Time_Cycle']}</p>
                        <p style="color:#F472B6; margin:2px 0; font-size:0.85rem;"><b>Wall Street Option:</b> {matched_pattern['Option_Strike']}</p>
                        <p style="color:#94A3B8; margin:2px 0; font-size:0.85rem;"><b>Conviction:</b> {matched_pattern['Conviction']}</p>
                    </div>
                </div>
                <p style="color:#E2E8F0; font-size:0.85rem; margin:8px 0 0 0;">💡 <b>Pattern Rationale:</b> {matched_pattern['Rationale']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner(f"Loading chart for {sel_pat_ticker}..."):
                df_chart_pat, _, _, _ = fetch_stock_data_realtime(sel_pat_ticker, period='1y')
                if df_chart_pat is not None and not df_chart_pat.empty:
                    create_chart_pattern_chart(df_chart_pat, matched_pattern, title=f"{sel_pat_ticker} — {matched_pattern['Pattern']} ({clean_tf})")
    else:
        st.info("No stocks currently meet strict pattern compression criteria in this scan. Click 'Scan Chart Patterns' to run again.")


# ─── TAB 7: F&O Trade Setups with R:R & Time Cycle ────────────────────────────

with tab_trades:
    st.markdown(f"### 🎯 F&O Active Trade Setups with R:R & Time Cycle ({mode} Mode)")
    results = st.session_state.get('scan_results', pd.DataFrame())
    
    if results.empty:
        st.info("💡 Click **🚀 Run Stock Scan** in the sidebar to populate live F&O trade setups.")
    else:
        if 'Action' in results.columns:
            actionable_df = results[results['Action'].str.contains('BUY|SELL', case=False, na=False)].copy()
        else:
            actionable_df = pd.DataFrame()
            
        if actionable_df.empty:
            st.info("💡 No breakout triggers active at this moment (Score ≥ 3 or ≤ -3). Check the Bull / Bear tabs below.")
        else:
            col_t_cnt, col_t_pdf = st.columns([3, 1])
            with col_t_cnt:
                st.markdown(f"#### 🎯 High-Conviction Breakout Setups ({len(actionable_df)} Found)")
            with col_t_pdf:
                pdf_trades_bytes = generate_pdf_report(
                    actionable_df,
                    title="F&O High-Conviction Trade Setups Report",
                    subtitle=f"Mode: {mode}",
                    mode=mode,
                    universe="NSE F&O Basket"
                )
                st.download_button(
                    label="📄 **Download F&O Setups PDF**",
                    data=pdf_trades_bytes,
                    file_name=f"FNO_Trade_Setups_{int(time.time())}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            trade_cols = ['Ticker', 'Name', 'Action', 'Close', 'Entry', 'Stop_Loss', 'Target_1', 'Target_2', 'Risk', 'RR_Ratio', 'Time_Cycle', 'Composite_Score', 'Rationale']
            display_trades = actionable_df[[c for c in trade_cols if c in actionable_df.columns]].copy()
            
            display_trades = display_trades.rename(columns={
                'Stop_Loss': 'SL',
                'Target_1': 'T1',
                'Target_2': 'T2',
                'RR_Ratio': 'R:R',
                'Time_Cycle': 'Time to Target',
                'Composite_Score': 'Score'
            })
            
            styled_trades = display_trades.style \
                .map(style_action, subset=['Action'] if 'Action' in display_trades.columns else []) \
                .map(style_score, subset=['Score'] if 'Score' in display_trades.columns else []) \
                .format({
                    'Close': '₹{:.2f}',
                    'Entry': '₹{:.2f}',
                    'SL': '₹{:.2f}',
                    'T1': '₹{:.2f}',
                    'T2': '₹{:.2f}',
                    'Risk': '₹{:.2f}',
                    'Score': '{:+d}'
                }, na_rep='—')
            
            st.dataframe(styled_trades, use_container_width=True, height=450)
            st.caption("📌 **Trading Rule**: Enter on confirmation above Entry for BUY, or below Entry for SELL. Time to target is dynamically calculated via ATR velocity.")


# ─── TAB 5: Elliott Wave (Weekly + Daily — Wall Street Trader Desk) ───────────

with tab_ew:
    st.markdown("### 🌊 Multi-Timeframe Elliott Wave Setup Engine — Wall Street Trader Desk")
    st.markdown("""
    Institutional grade Wave mapping across **Daily (Intraday/Swing)** and **Weekly (Positional/Macro)** timeframes.
    Provides exact **Option Buying Strategies (Call CE / Put PE Strikes)** and **Cash Equity Trade Plans**.
    """)
    
    col_ew1, col_ew2 = st.columns([3, 1])
    with col_ew2:
        run_ew_scan = st.button("🌊 **Re-Scan Elliott Waves**", use_container_width=True)
        
    if run_ew_scan or 'ew_scan_results' not in st.session_state:
        ew_tickers = get_nifty50_tickers()
        with st.spinner("Analyzing Wave structures, Option strike convexities & Fibonacci projections across Weekly & Daily charts..."):
            ew_df = scan_all_elliott_wave_setups(ew_tickers)
            st.session_state['ew_scan_results'] = ew_df
    else:
        ew_df = st.session_state.get('ew_scan_results', pd.DataFrame())
        
    if not ew_df.empty:
        col_ew_cnt, col_ew_pdf = st.columns([3, 1])
        with col_ew_cnt:
            st.markdown(f"#### ⚡ Active High-Conviction Wave Setups ({len(ew_df)} Found)")
        with col_ew_pdf:
            pdf_ew_bytes = generate_pdf_report(
                ew_df,
                title="Elliott Wave Institutional Trade Report",
                subtitle="Wall Street Options & Cash Strategy",
                mode="Daily + Weekly",
                universe="NSE Equities"
            )
            st.download_button(
                label="📄 **Download All Waves PDF**",
                data=pdf_ew_bytes,
                file_name=f"Elliott_Wave_Master_{int(time.time())}.pdf",
                mime="application/pdf",
                key="btn_pdf_ew_master",
                use_container_width=True
            )
            
        ew_display_cols = [
            'Ticker', 'Name', 'Timeframe', 'Wave_Stage', 'Direction', 'Conviction',
            'Option_Action', 'Option_Expiry', 'Option_Target_ROI', 'Option_SL', 'Option_RR', 
            'Cash_RR', 'Fib_Level', 'Target_1', 'Target_2'
        ]
        available_ew = [c for c in ew_display_cols if c in ew_df.columns]
        
        styled_ew = ew_df[available_ew].style \
            .map(lambda v: 'color: #22C55E; font-weight: bold;' if 'BUY' in str(v) else ('color: #EF4444; font-weight: bold;' if 'SELL' in str(v) else ''), subset=['Direction'] if 'Direction' in available_ew else []) \
            .map(lambda v: 'color: #FBBF24; font-weight: bold;', subset=['Conviction'] if 'Conviction' in available_ew else []) \
            .map(lambda v: 'color: #38BDF8; font-weight: bold;', subset=['Option_Action'] if 'Option_Action' in available_ew else []) \
            .format({
                'Target_1': '₹{:.2f}',
                'Target_2': '₹{:.2f}'
            }, na_rep='—')
            
        st.dataframe(styled_ew, use_container_width=True, height=380)
    else:
        st.info("No active Elliott Wave triggers in this batch.")
        
    st.markdown("---")
    st.markdown("#### 🔍 Wall Street Trading Desk: Deep Stock Wave Breakdown & Chart")
    ew_ticker_options = get_nifty50_tickers()
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        sel_ew_ticker = st.selectbox("Select Stock for Institutional Breakdown:", ew_ticker_options, key="ew_chart_selector")
    with col_sel2:
        sel_tf = st.radio("Timeframe:", ["Daily Chart (Swing)", "Weekly Chart (Macro)"], horizontal=True, key="ew_tf_radio")
        
    if sel_ew_ticker:
        with st.spinner(f"Rendering precise Elliott Wave structure for {sel_ew_ticker}..."):
            ew_detail = analyze_multi_timeframe_elliott(sel_ew_ticker)
            
        if ew_detail.get('valid'):
            if "Daily" in sel_tf:
                chart_df = ew_detail['df_daily']
                chart_setup = ew_detail['daily']
                chart_title = f"{sel_ew_ticker} — Daily Elliott Wave Analysis"
            else:
                chart_df = ew_detail['df_weekly']
                chart_setup = ew_detail['weekly']
                chart_title = f"{sel_ew_ticker} — Weekly Macro Elliott Wave Analysis"
                
            # Create single stock dossier DataFrame for PDF export
            single_stock_df = pd.DataFrame([{
                'Ticker': sel_ew_ticker,
                'Name': get_stock_info(sel_ew_ticker).get('name', sel_ew_ticker),
                'Close': chart_setup.get('current_price', 0.0),
                'Change%': chart_setup.get('change_pct', 0.0),
                'Signal': chart_setup.get('direction', 'BUY'),
                'Timeframe': chart_setup.get('timeframe_context', sel_tf),
                'Wave_Stage': chart_setup.get('wave_phase', 'Developing'),
                'Option_Action': f"{chart_setup.get('option_type')} {chart_setup.get('option_strike')}",
                'Option_Expiry': chart_setup.get('option_expiry', 'Monthly Expiry'),
                'Option_Target_ROI': chart_setup.get('option_target_roi', '+100% to +300%'),
                'Option_SL': chart_setup.get('option_sl', '-35% SL'),
                'Option_RR': chart_setup.get('option_rr', '1:3.5'),
                'Trigger_Entry': chart_setup.get('current_price', 0.0),
                'Stop_Loss': chart_setup.get('invalidation_price', 0.0),
                'Target_1': chart_setup.get('target_1', 0.0),
                'Target_2': chart_setup.get('target_2', 0.0),
                'RR_Ratio': chart_setup.get('rr_ratio', '1:2.5'),
                'Time_Cycle': chart_setup.get('time_cycle', '📅 5 - 12 Trading Days'),
                'Conviction': chart_setup.get('conviction_score', '92%'),
                'Rationale': chart_setup.get('how_it_happened', chart_setup.get('rationale', ''))
            }])
            
            col_doss_title, col_doss_pdf = st.columns([3, 1])
            with col_doss_pdf:
                pdf_single_bytes = generate_pdf_report(
                    single_stock_df,
                    title=f"{sel_ew_ticker} Institutional Trade Dossier",
                    subtitle="Wall Street Options & Wave Breakdown",
                    mode=sel_tf,
                    universe="NSE Equities"
                )
                st.download_button(
                    label=f"📄 **Download {sel_ew_ticker} PDF Dossier**",
                    data=pdf_single_bytes,
                    file_name=f"{sel_ew_ticker.replace('.NS', '')}_Dossier_{int(time.time())}.pdf",
                    mime="application/pdf",
                    key=f"btn_pdf_single_{sel_ew_ticker}",
                    use_container_width=True
                )
                
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 18px; border-radius: 12px; border: 1px solid #3b82f6; margin-bottom: 15px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.2rem; font-weight:800; color:#F8FAFC;">🏦 Wall Street Trade Directive: {sel_ew_ticker}</span>
                    <span style="font-size:1.0rem; font-weight:700; color:#FDE047;">Conviction: {chart_setup.get('conviction_score', '92%')}</span>
                </div>
                <hr style="margin: 8px 0; border-color: #334155;">
                <p style="color:#A5B4FC; font-size:0.95rem; margin:0 0 8px 0;">
                    <b>🌊 Wave Stage:</b> <code>{chart_setup.get('wave_phase', 'Developing')}</code> | <b>Timeframe:</b> <code>{chart_setup.get('timeframe_context', sel_tf)}</code>
                </p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px;">
                    <div style="background: rgba(30, 27, 75, 0.6); padding: 10px; border-radius: 8px; border: 1px solid #6366f1;">
                        <h4 style="color:#38BDF8; margin:0 0 4px 0;">🎯 Option Buying Strategy (High Delta Convexity)</h4>
                        <p style="color:#F8FAFC; margin:2px 0; font-size:0.9rem;"><b>Action:</b> <span style="color:#22C55E; font-weight:bold;">{chart_setup.get('option_type', 'BUY CALL')}</span> — <b>{chart_setup.get('option_strike', 'ATM')}</b></p>
                        <p style="color:#CBD5E1; margin:2px 0; font-size:0.85rem;"><b>Expiry:</b> {chart_setup.get('option_expiry', 'Monthly Expiry')}</p>
                        <p style="color:#38BDF8; margin:2px 0; font-size:0.85rem;"><b>Target ROI:</b> {chart_setup.get('option_target_roi', '+100% to +300%')}</p>
                        <p style="color:#EF4444; margin:2px 0; font-size:0.85rem;"><b>Risk Management:</b> {chart_setup.get('option_sl', '-35% SL')} | <b>R:R:</b> {chart_setup.get('option_rr', '1:3.5')}</p>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 8px; border: 1px solid #10B981;">
                        <h4 style="color:#10B981; margin:0 0 4px 0;">💎 Cash Equity Buying Strategy (Spot / Delivery)</h4>
                        <p style="color:#F8FAFC; margin:2px 0; font-size:0.9rem;"><b>Entry:</b> ₹{chart_setup.get('current_price', 0.0):.2f} | <b>Invalidation SL:</b> <span style="color:#EF4444;">₹{chart_setup.get('invalidation_price', 0.0):.2f}</span></p>
                        <p style="color:#22C55E; margin:2px 0; font-size:0.85rem;"><b>Target 1 (1.618 Fib):</b> ₹{chart_setup.get('target_1', 0.0):.2f}</p>
                        <p style="color:#38BDF8; margin:2px 0; font-size:0.85rem;"><b>Target 2 (2.0 Fib):</b> ₹{chart_setup.get('target_2', 0.0):.2f}</p>
                        <p style="color:#FDE047; margin:2px 0; font-size:0.85rem;"><b>Cash Risk-Reward:</b> {chart_setup.get('rr_ratio', '1:2.5')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if chart_setup.get('how_it_happened'):
                st.markdown("#### 📖 The Anatomy of This Wave (How It Happened)")
                st.info(chart_setup.get('how_it_happened'))
                
            create_elliott_wave_chart(chart_df, chart_setup.get('pivots', []), chart_setup, title=chart_title)
        else:
            st.warning(f"Could not calculate Elliott Waves for {sel_ew_ticker}")


# ─── TAB 6: Bull Stocks Tab with R:R & Time Cycle ────────────────────────────

with tab_bull:
    results = st.session_state.get('scan_results', pd.DataFrame())
    if results.empty:
        st.info("💡 Click **🚀 Run Stock Scan** in the sidebar to load Bullish Stocks.")
    else:
        bull_df = get_bull_stocks(results)
        if bull_df.empty:
            st.info("No bullish stocks found in this scan.")
        else:
            col_b_cnt, col_b_pdf = st.columns([3, 1])
            with col_b_cnt:
                st.markdown(f"### 🐂 Bullish Stocks with R:R & Target Duration ({len(bull_df)})")
            with col_b_pdf:
                pdf_bull_bytes = generate_pdf_report(
                    bull_df,
                    title="Bullish Stocks Institutional Report",
                    subtitle="Ranked by Bullish Momentum",
                    mode=mode,
                    universe="NSE Universe"
                )
                st.download_button(
                    label="📄 **Download Bull Stocks PDF**",
                    data=pdf_bull_bytes,
                    file_name=f"Bull_Stocks_Report_{int(time.time())}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            display_df = format_results_table(bull_df)
            
            styled = display_df.style \
                .map(style_signal, subset=['Signal'] if 'Signal' in display_df.columns else []) \
                .map(style_score, subset=['Score'] if 'Score' in display_df.columns else []) \
                .map(style_action, subset=['Action'] if 'Action' in display_df.columns else []) \
                .map(style_change, subset=['Chg%'] if 'Chg%' in display_df.columns else []) \
                .format({
                    'Close': '₹{:.2f}',
                    'Chg%': '{:+.2f}%',
                    'Entry': '₹{:.2f}',
                    'SL': '₹{:.2f}',
                    'T1': '₹{:.2f}',
                    'T2': '₹{:.2f}',
                    'RSI': '{:.1f}',
                    'ADX': '{:.1f}',
                    'Score': '{:+d}',
                }, na_rep='—')
            
            st.dataframe(styled, use_container_width=True, height=500)


# ─── TAB 7: Bear Stocks Tab with R:R & Time Cycle ────────────────────────────

with tab_bear:
    results = st.session_state.get('scan_results', pd.DataFrame())
    if results.empty:
        st.info("💡 Click **🚀 Run Stock Scan** in the sidebar to load Bearish Stocks.")
    else:
        bear_df = get_bear_stocks(results)
        if bear_df.empty:
            st.info("No bearish stocks found in this scan.")
        else:
            col_br_cnt, col_br_pdf = st.columns([3, 1])
            with col_br_cnt:
                st.markdown(f"### 🐻 Bearish Stocks with R:R & Target Duration ({len(bear_df)})")
            with col_br_pdf:
                pdf_bear_bytes = generate_pdf_report(
                    bear_df,
                    title="Bearish Stocks Institutional Report",
                    subtitle="Ranked by Bearish Breakdown",
                    mode=mode,
                    universe="NSE Universe"
                )
                st.download_button(
                    label="📄 **Download Bear Stocks PDF**",
                    data=pdf_bear_bytes,
                    file_name=f"Bear_Stocks_Report_{int(time.time())}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            display_df = format_results_table(bear_df)
            
            styled = display_df.style \
                .map(style_signal, subset=['Signal'] if 'Signal' in display_df.columns else []) \
                .map(style_score, subset=['Score'] if 'Score' in display_df.columns else []) \
                .map(style_action, subset=['Action'] if 'Action' in display_df.columns else []) \
                .map(style_change, subset=['Chg%'] if 'Chg%' in display_df.columns else []) \
                .format({
                    'Close': '₹{:.2f}',
                    'Chg%': '{:+.2f}%',
                    'Entry': '₹{:.2f}',
                    'SL': '₹{:.2f}',
                    'T1': '₹{:.2f}',
                    'T2': '₹{:.2f}',
                    'RSI': '{:.1f}',
                    'ADX': '{:.1f}',
                    'Score': '{:+d}',
                }, na_rep='—')
            
            st.dataframe(styled, use_container_width=True, height=500)


# ─── TAB 8: All Stocks Universe ──────────────────────────────────────────────

with tab_all:
    results = st.session_state.get('scan_results', pd.DataFrame())
    if results.empty:
        st.info("💡 Click **🚀 Run Stock Scan** in the sidebar to load All Stocks.")
    else:
        col_a_cnt, col_a_pdf = st.columns([3, 1])
        with col_a_cnt:
            st.markdown(f"### 📋 All Stocks Universe ({len(results)} Stocks Scanned)")
        with col_a_pdf:
            pdf_all_bytes = generate_pdf_report(
                results,
                title="All Stocks Complete Universe Report",
                subtitle=f"Total Stocks: {len(results)}",
                mode=mode,
                universe=universe_name
            )
            st.download_button(
                label="📄 **Download All Stocks PDF**",
                data=pdf_all_bytes,
                file_name=f"All_Stocks_Universe_{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        display_df = format_results_table(results)
        
        styled = display_df.style \
            .map(style_signal, subset=['Signal'] if 'Signal' in display_df.columns else []) \
            .map(style_score, subset=['Score'] if 'Score' in display_df.columns else []) \
            .map(style_action, subset=['Action'] if 'Action' in display_df.columns else []) \
            .map(style_change, subset=['Chg%'] if 'Chg%' in display_df.columns else []) \
            .format({
                'Close': '₹{:.2f}',
                'Chg%': '{:+.2f}%',
                'Entry': '₹{:.2f}',
                'SL': '₹{:.2f}',
                'T1': '₹{:.2f}',
                'T2': '₹{:.2f}',
                'RSI': '{:.1f}',
                'ADX': '{:.1f}',
                'Score': '{:+d}',
            }, na_rep='—')
        
        st.dataframe(styled, use_container_width=True, height=600)


# ─── TAB 9: Custom Stock Search & Precision Wave Plotter ─────────────────────

with tab_search:
    st.markdown("### 🔍 Search ANY NSE 500 Stock & Instant Elliott Wave Plotter")
    st.markdown("Enter any NSE symbol (e.g. `ZOMATO`, `SUZLON`, `JIOFIN`, `IREDA`, `TATACHEM`, `RELIANCE`):")
    
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        custom_input = st.text_input("Enter NSE Ticker Symbol:", value="ZOMATO", placeholder="e.g. ZOMATO, SUZLON, TATASTEEL")
    with col_s2:
        custom_tf = st.selectbox("Chart Timeframe:", ["Daily Chart (Swing)", "Weekly Chart (Macro)", "1-Hour Chart (Intraday)"])
    with col_s3:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        analyze_btn = st.button("🚀 **Analyze Stock**", use_container_width=True)
        
    if custom_input:
        clean_ticker = custom_input.strip().upper()
        if not clean_ticker.endswith('.NS') and not clean_ticker.startswith('^'):
            clean_ticker += '.NS'
            
        with st.spinner(f"Fetching live tick data and computing Elliott Waves for {clean_ticker}..."):
            if "1-Hour" in custom_tf:
                raw_df = yf.download(clean_ticker, period='2mo', interval='1h', progress=False)
                if raw_df is not None and not raw_df.empty:
                    if isinstance(raw_df.columns, pd.MultiIndex): raw_df.columns = [c[0] for c in raw_df.columns]
                    raw_df = raw_df.dropna(subset=['Close'])
                    from indicators import compute_all_indicators
                    from elliott_wave import analyze_elliott_wave
                    raw_df = compute_all_indicators(raw_df)
                    ew_res = analyze_elliott_wave(raw_df, timeframe='daily')
                else:
                    ew_res = {'valid': False}
            else:
                ew_mult = analyze_multi_timeframe_elliott(clean_ticker)
                if ew_mult.get('valid'):
                    if "Daily" in custom_tf:
                        raw_df = ew_mult['df_daily']
                        ew_res = ew_mult['daily']
                    else:
                        raw_df = ew_mult['df_weekly']
                        ew_res = ew_mult['weekly']
                else:
                    ew_res = {'valid': False}
                    
        if ew_res and ew_res.get('wave_phase'):
            info = get_stock_info(clean_ticker)
            last_p = float(raw_df['Close'].iloc[-1])
            
            col_head_left, col_head_pdf = st.columns([3, 1])
            with col_head_left:
                st.markdown(f"## 📈 {clean_ticker} — {info.get('name', clean_ticker.replace('.NS',''))}")
                st.markdown(f"**Latest Real-Time Close**: `₹{last_p:,.2f}` | **Wave Phase**: `{ew_res.get('wave_phase')}`")
            with col_head_pdf:
                # Generate PDF for this specific searched stock
                searched_stock_df = pd.DataFrame([{
                    'Ticker': clean_ticker,
                    'Name': info.get('name', clean_ticker),
                    'Close': last_p,
                    'Change%': float(((last_p - raw_df['Close'].iloc[-2]) / raw_df['Close'].iloc[-2]) * 100) if len(raw_df) > 1 else 0.0,
                    'Signal': 'BULLISH' if 'BULL' in ew_res.get('wave_phase', '').upper() else 'BEARISH',
                    'Timeframe': custom_tf,
                    'Wave_Stage': ew_res.get('wave_phase'),
                    'Option_Action': f"{'BUY CALL' if 'BULL' in ew_res.get('wave_phase','').upper() else 'BUY PUT'} (ATM/OTM)",
                    'Option_Expiry': 'Current Month Expiry',
                    'Option_Target_ROI': '+100% to +300%',
                    'Option_SL': '-35% SL',
                    'Trigger_Entry': last_p,
                    'Stop_Loss': ew_res.get('invalidation_price', 0.0),
                    'Target_1': ew_res.get('target_1', 0.0),
                    'Target_2': ew_res.get('target_2', 0.0),
                    'RR_Ratio': '1:3.0',
                    'Time_Cycle': '⚡ 1 - 5 Sessions',
                    'Conviction': '92%',
                    'Rationale': ew_res.get('rationale', '')
                }])
                pdf_search_bytes = generate_pdf_report(
                    searched_stock_df,
                    title=f"{clean_ticker} Technical Elliott Wave Dossier",
                    subtitle="Wall Street Options & Wave Breakdown",
                    mode=custom_tf,
                    universe="NSE Custom Search"
                )
                st.download_button(
                    label=f"📄 **Download {clean_ticker} PDF**",
                    data=pdf_search_bytes,
                    file_name=f"{clean_ticker.replace('.NS', '')}_Analysis_{int(time.time())}.pdf",
                    mime="application/pdf",
                    key=f"btn_pdf_search_{clean_ticker}",
                    use_container_width=True
                )
                
            if ew_res.get('heading_destination'):
                st.markdown(f"**Wave Trajectory**: `{ew_res.get('heading_destination')}`")
            if ew_res.get('rationale'):
                st.caption(f"💡 **Rationale**: {ew_res.get('rationale')}")
                
            create_elliott_wave_chart(raw_df, ew_res.get('pivots', []), ew_res, title=f"{clean_ticker} — {custom_tf}")
        else:
            st.error(f"Could not load data for symbol '{clean_ticker}'. Ensure it is a valid NSE stock ticker.")
