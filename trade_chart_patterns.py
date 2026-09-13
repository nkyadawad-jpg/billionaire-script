"""
📈 TRADE CHART — Institutional Price Action Chart Patterns Detection Engine
Part of The Ultimate Edge by Noeman

Refined Multi-Timeframe Structural Engine:
- 15-Min: Intraday Scalp Alert
- 1-Hour: Intraday / Swing
- Daily: Swing Trading
- Weekly: Positional Macro

ZERO LOOK-AHEAD BIAS: Signals generated IMMEDIATELY at pattern completion/breakout confirmation.
Entry, Entry Zone, SL, Risk per share, and Target projections (T1, T2, T3) calculated strictly from pattern geometry.
"""

import numpy as np
import pandas as pd
import logging
import datetime
from typing import Dict, List, Optional
import yfinance as yf
import concurrent.futures
import threading

from indicators import compute_all_indicators
from stock_universe import get_stock_info, get_nifty500_tickers, get_nifty50_tickers, get_nifty200_tickers
from scanner import fetch_stock_data_realtime
from unified_consensus import calculate_unified_consensus
from safe_data_pipeline import safe_download, safe_get_fast_info
from chart_patterns import build_actionable_trade_setup, calculate_option_strike

logger = logging.getLogger(__name__)

def get_pattern_svg(pattern_name: str) -> str:
    """Return inline SVG diagram illustrating the exact geometry of the detected pattern."""
    p_upper = pattern_name.upper()
    
    if 'DOUBLE BOTTOM' in p_upper or 'W-SHAPE' in p_upper:
        return """
        <svg width="240" height="130" viewBox="0 0 240 130" style="background:#0f172a; border-radius:10px; padding:5px;">
            <polyline points="20,20 60,95 100,50 140,95 180,25" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/>
            <line x1="15" y1="50" x2="220" y2="50" stroke="#ef4444" stroke-width="2" stroke-dasharray="4"/>
            <text x="150" y="42" fill="#ef4444" font-size="10" font-weight="bold">Neckline (Trigger)</text>
            <line x1="90" y1="95" x2="220" y2="95" stroke="#f43f5e" stroke-width="1.5" stroke-dasharray="2"/>
            <text x="160" y="110" fill="#f43f5e" font-size="10">Stop Loss</text>
            <line x1="140" y1="15" x2="220" y2="15" stroke="#22c55e" stroke-width="2" stroke-dasharray="3"/>
            <text x="165" y="12" fill="#22c55e" font-size="10" font-weight="bold">Target</text>
        </svg>
        """
    elif 'DOUBLE TOP' in p_upper or 'M-SHAPE' in p_upper:
        return """
        <svg width="240" height="130" viewBox="0 0 240 130" style="background:#0f172a; border-radius:10px; padding:5px;">
            <polyline points="20,105 60,25 100,75 140,25 180,115" fill="none" stroke="#f43f5e" stroke-width="3" stroke-linecap="round"/>
            <line x1="15" y1="75" x2="220" y2="75" stroke="#ef4444" stroke-width="2" stroke-dasharray="4"/>
            <text x="150" y="70" fill="#ef4444" font-size="10" font-weight="bold">Neckline (Trigger)</text>
            <line x1="60" y1="18" x2="220" y2="18" stroke="#f43f5e" stroke-width="1.5" stroke-dasharray="2"/>
            <text x="160" y="14" fill="#f43f5e" font-size="10">Stop Loss</text>
            <line x1="140" y1="120" x2="220" y2="120" stroke="#22c55e" stroke-width="2" stroke-dasharray="3"/>
            <text x="165" y="118" fill="#22c55e" font-size="10" font-weight="bold">Target</text>
        </svg>
        """
    elif 'INVERSE HEAD' in p_upper:
        return """
        <svg width="240" height="130" viewBox="0 0 240 130" style="background:#0f172a; border-radius:10px; padding:5px;">
            <polyline points="15,20 45,65 75,38 115,105 155,38 185,65 215,15" fill="none" stroke="#38bdf8" stroke-width="3"/>
            <line x1="10" y1="38" x2="225" y2="38" stroke="#ef4444" stroke-width="2" stroke-dasharray="4"/>
            <text x="160" y="32" fill="#ef4444" font-size="10" font-weight="bold">Neckline</text>
            <line x1="155" y1="65" x2="225" y2="65" stroke="#f43f5e" stroke-width="1.5" stroke-dasharray="2"/>
            <text x="160" y="78" fill="#f43f5e" font-size="10">Stop Loss</text>
            <line x1="185" y1="10" x2="235" y2="10" stroke="#22c55e" stroke-width="2" stroke-dasharray="3"/>
            <text x="175" y="8" fill="#22c55e" font-size="10" font-weight="bold">Target</text>
        </svg>
        """
    elif 'HEAD & SHOULDERS' in p_upper or 'HEAD AND SHOULDERS' in p_upper:
        return """
        <svg width="240" height="130" viewBox="0 0 240 130" style="background:#0f172a; border-radius:10px; padding:5px;">
            <polyline points="15,105 45,55 75,85 115,15 155,85 185,55 215,120" fill="none" stroke="#f43f5e" stroke-width="3"/>
            <line x1="10" y1="85" x2="225" y2="85" stroke="#ef4444" stroke-width="2" stroke-dasharray="4"/>
            <text x="160" y="80" fill="#ef4444" font-size="10" font-weight="bold">Neckline</text>
            <line x1="155" y1="55" x2="225" y2="55" stroke="#f43f5e" stroke-width="1.5" stroke-dasharray="2"/>
            <text x="160" y="50" fill="#f43f5e" font-size="10">Stop Loss</text>
            <line x1="185" y1="122" x2="235" y2="122" stroke="#22c55e" stroke-width="2" stroke-dasharray="3"/>
            <text x="175" y="118" fill="#22c55e" font-size="10" font-weight="bold">Target</text>
        </svg>
        """
    elif 'FALLING WEDGE' in p_upper:
        return """
        <svg width="240" height="130" viewBox="0 0 240 130" style="background:#0f172a; border-radius:10px; padding:5px;">
            <line x1="20" y1="20" x2="160" y2="80" stroke="#ef4444" stroke-width="2"/>
            <line x1="20" y1="55" x2="160" y2="100" stroke="#ef4444" stroke-width="2"/>
            <polyline points="20,38 50,26 80,64 110,48 140,84 175,25 210,10" fill="none" stroke="#22c55e" stroke-width="2.5"/>
            <text x="145" y="20" fill="#22c55e" font-size="10" font-weight="bold">Entry / Target</text>
        </svg>
        """
    elif 'RISING WEDGE' in p_upper:
        return """
        <svg width="240" height="130" viewBox="0 0 240 130" style="background:#0f172a; border-radius:10px; padding:5px;">
            <line x1="20" y1="105" x2="160" y2="35" stroke="#ef4444" stroke-width="2"/>
            <line x1="20" y1="75" x2="160" y2="22" stroke="#ef4444" stroke-width="2"/>
            <polyline points="20,90 50,70 80,44 110,34 140,24 175,85 210,115" fill="none" stroke="#f43f5e" stroke-width="2.5"/>
            <text x="140" y="110" fill="#f43f5e" font-size="10" font-weight="bold">Breakdown / Target</text>
        </svg>
        """
    elif 'ASCENDING TRIANGLE' in p_upper:
        return """
        <svg width="240" height="130" viewBox="0 0 240 130" style="background:#0f172a; border-radius:10px; padding:5px;">
            <line x1="20" y1="35" x2="170" y2="35" stroke="#ef4444" stroke-width="2"/>
            <line x1="20" y1="110" x2="170" y2="35" stroke="#22c55e" stroke-width="2"/>
            <polyline points="20,95 50,35 80,80 110,35 140,52 170,35 200,10" fill="none" stroke="#38bdf8" stroke-width="2.5"/>
            <text x="145" y="22" fill="#38bdf8" font-size="10" font-weight="bold">Flat Top Breakout</text>
        </svg>
        """
    elif 'DESCENDING TRIANGLE' in p_upper:
        return """
        <svg width="240" height="130" viewBox="0 0 240 130" style="background:#0f172a; border-radius:10px; padding:5px;">
            <line x1="20" y1="100" x2="170" y2="100" stroke="#ef4444" stroke-width="2"/>
            <line x1="20" y1="25" x2="170" y2="100" stroke="#ef4444" stroke-width="2"/>
            <polyline points="20,35 50,100 80,52 110,100 140,80 170,100 200,125" fill="none" stroke="#f43f5e" stroke-width="2.5"/>
            <text x="140" y="120" fill="#f43f5e" font-size="10" font-weight="bold">Flat Bottom Breakdown</text>
        </svg>
        """
    elif 'SYMMETRICAL' in p_upper or 'PENNANT' in p_upper:
        return """
        <svg width="240" height="130" viewBox="0 0 240 130" style="background:#0f172a; border-radius:10px; padding:5px;">
            <line x1="20" y1="20" x2="170" y2="65" stroke="#ef4444" stroke-width="2"/>
            <line x1="20" y1="115" x2="170" y2="65" stroke="#22c55e" stroke-width="2"/>
            <polyline points="20,105 50,28 80,90 110,42 140,75 170,65 205,25" fill="none" stroke="#38bdf8" stroke-width="2.5"/>
            <text x="145" y="22" fill="#38bdf8" font-size="10" font-weight="bold">Coil Breakout</text>
        </svg>
        """
    else:
        return """
        <svg width="240" height="130" viewBox="0 0 240 130" style="background:#0f172a; border-radius:10px; padding:5px;">
            <line x1="20" y1="30" x2="180" y2="30" stroke="#ef4444" stroke-width="2"/>
            <line x1="20" y1="95" x2="180" y2="95" stroke="#22c55e" stroke-width="2"/>
            <polyline points="20,75 50,30 80,95 110,30 140,95 180,30 215,10" fill="none" stroke="#38bdf8" stroke-width="2.5"/>
            <text x="145" y="18" fill="#38bdf8" font-size="10" font-weight="bold">Channel Breakout</text>
        </svg>
        """

def find_trade_extrema(df: pd.DataFrame, window: int = 3) -> List[Dict]:
    """Find local swing highs and swing lows for chart pattern geometry."""
    pivots = []
    highs = df['High'].values
    lows = df['Low'].values
    dates = df.index
    
    n = len(df)
    for i in range(window, n - window):
        is_high = all(highs[i] >= highs[i - j] for j in range(1, window + 1)) and \
                  all(highs[i] >= highs[i + j] for j in range(1, window + 1))
        is_low = all(lows[i] <= lows[i - j] for j in range(1, window + 1)) and \
                 all(lows[i] <= lows[i + j] for j in range(1, window + 1))
                 
        if is_high:
            pivots.append({'index': i, 'date': str(dates[i]), 'type': 'HIGH', 'price': float(highs[i])})
        elif is_low:
            pivots.append({'index': i, 'date': str(dates[i]), 'type': 'LOW', 'price': float(lows[i])})
            
    pivots.append({'index': n - 1, 'date': str(dates[-1]), 'type': 'CLOSE', 'price': float(df['Close'].iloc[-1])})
    return pivots

def detect_trade_chart_pattern(df: pd.DataFrame, ticker: str, name: str, rt_price: float, prev_close: float, chg_pct: float, timeframe: str = 'Daily') -> Optional[Dict]:
    """
    Refined Structural Pattern Engine with zero look-ahead bias.
    Calculates Entry, Entry Zone, Stop Loss, Target 1, Target 2, Target 3, and Trade Lifecycle Status strictly from pattern completion geometry.
    """
    if len(df) < 15:
        return None
        
    curr_close = float(rt_price) if rt_price and rt_price > 0 else float(df['Close'].iloc[-1])
    tf_lower = timeframe.lower()
    
    if '15' in tf_lower:
        window_size = 2
        min_h_pct = 1.2
        min_pole_pct = 2.5
        max_peak_diff_pct = 1.8
    elif '1h' in tf_lower or 'hour' in tf_lower:
        window_size = 3
        min_h_pct = 2.2
        min_pole_pct = 4.5
        max_peak_diff_pct = 2.5
    elif 'week' in tf_lower:
        window_size = 2
        min_h_pct = 6.5
        min_pole_pct = 12.0
        max_peak_diff_pct = 3.5
    else:
        window_size = 3
        min_h_pct = 3.5
        min_pole_pct = 6.5
        max_peak_diff_pct = 3.0
        
    pivots = find_trade_extrema(df, window=window_size)
    high_pivots = [p for p in pivots if p['type'] == 'HIGH']
    low_pivots = [p for p in pivots if p['type'] == 'LOW']
    
    # ─── 1. 🎯 DOUBLE BOTTOM (W-Shape Reversal) ──────────────────────────────
    if len(low_pivots) >= 2 and len(high_pivots) >= 1:
        bot1 = low_pivots[-2]['price']
        bot2 = low_pivots[-1]['price']
        neckline = high_pivots[-1]['price']
        diff_pct = abs(bot1 - bot2) / bot1 * 100
        
        if diff_pct <= max_peak_diff_pct and neckline > max(bot1, bot2):
            pattern_h = neckline - min(bot1, bot2)
            if (pattern_h / bot1 * 100) >= min_h_pct:
                trigger = round(neckline * 1.002, 2)
                sl = round(min(bot1, bot2) * 0.99, 2)
                return build_actionable_trade_setup(
                    ticker, name, timeframe, '🎯 Double Bottom (W-Shape)', 'Reversal Pattern',
                    'BUY / LONG (REVERSAL)', trigger, sl, pattern_h, curr_close, chg_pct, 95,
                    f"Twin bottoms tested at ₹{bot1:.2f} & ₹{bot2:.2f} (diff {diff_pct:.1f}%). Neckline trigger: ₹{neckline:.2f}.", df
                )

    # ─── 2. 🔴 DOUBLE TOP (M-Shape Reversal) ─────────────────────────────────
    if len(high_pivots) >= 2 and len(low_pivots) >= 1:
        top1 = high_pivots[-2]['price']
        top2 = high_pivots[-1]['price']
        neckline = low_pivots[-1]['price']
        diff_pct = abs(top1 - top2) / top1 * 100
        
        if diff_pct <= max_peak_diff_pct and neckline < min(top1, top2):
            pattern_h = max(top1, top2) - neckline
            if (pattern_h / top1 * 100) >= min_h_pct:
                trigger = round(neckline * 0.998, 2)
                sl = round(max(top1, top2) * 1.01, 2)
                return build_actionable_trade_setup(
                    ticker, name, timeframe, '🔴 Double Top (M-Shape)', 'Reversal Pattern',
                    'SELL / SHORT (REVERSAL)', trigger, sl, pattern_h, curr_close, chg_pct, 94,
                    f"Twin tops peaked at ₹{top1:.2f} & ₹{top2:.2f} (diff {diff_pct:.1f}%). Neckline breakdown trigger: ₹{neckline:.2f}.", df
                )

    # ─── 3. 👤 INVERSE HEAD & SHOULDERS (Bullish Reversal) ────────────────────
    if len(low_pivots) >= 3 and len(high_pivots) >= 2:
        left_s = low_pivots[-3]['price']
        head = low_pivots[-2]['price']
        right_s = low_pivots[-1]['price']
        neckline = max(high_pivots[-2]['price'], high_pivots[-1]['price'])
        
        if head < left_s and head < right_s and abs(left_s - right_s) / left_s * 100 <= (max_peak_diff_pct + 1.5):
            pattern_h = neckline - head
            if (pattern_h / head * 100) >= min_h_pct:
                trigger = round(neckline * 1.002, 2)
                sl = round(right_s * 0.985, 2)
                return build_actionable_trade_setup(
                    ticker, name, timeframe, '👤 Inverse Head & Shoulders', 'Reversal Pattern',
                    'BUY / LONG (REVERSAL)', trigger, sl, pattern_h, curr_close, chg_pct, 96,
                    f"Head capitulated at ₹{head:.2f}. Shoulders at ₹{left_s:.2f} & ₹{right_s:.2f}. Neckline trigger: ₹{neckline:.2f}.", df
                )

    # ─── 4. 👤 BEARISH HEAD & SHOULDERS TOP ───────────────────────────────────
    if len(high_pivots) >= 3 and len(low_pivots) >= 2:
        left_s = high_pivots[-3]['price']
        head = high_pivots[-2]['price']
        right_s = high_pivots[-1]['price']
        neckline = min(low_pivots[-2]['price'], low_pivots[-1]['price'])
        
        if head > left_s and head > right_s and abs(left_s - right_s) / left_s * 100 <= (max_peak_diff_pct + 1.5):
            pattern_h = head - neckline
            if (pattern_h / head * 100) >= min_h_pct:
                trigger = round(neckline * 0.998, 2)
                sl = round(right_s * 1.015, 2)
                return build_actionable_trade_setup(
                    ticker, name, timeframe, '👤 Head & Shoulders Top', 'Reversal Pattern',
                    'SELL / SHORT (REVERSAL)', trigger, sl, pattern_h, curr_close, chg_pct, 95,
                    f"Head peaked at ₹{head:.2f}. Right shoulder at ₹{right_s:.2f}. Neckline breakdown trigger: ₹{neckline:.2f}.", df
                )

    # ─── 5. 🟢 FALLING WEDGE (Bullish Reversal / Breakout) ────────────────────
    if len(high_pivots) >= 2 and len(low_pivots) >= 2:
        h1, h2 = high_pivots[-2]['price'], high_pivots[-1]['price']
        l1, l2 = low_pivots[-2]['price'], low_pivots[-1]['price']
        
        if h2 < h1 and l2 < l1:
            high_drop = h1 - h2
            low_drop = l1 - l2
            if high_drop > low_drop * 1.10 and (h1 - l2) / l2 * 100 >= min_h_pct:
                trigger = round(h2 * 1.002, 2)
                sl = round(l2 * 0.985, 2)
                pattern_h = h1 - l2
                return build_actionable_trade_setup(
                    ticker, name, timeframe, '🟢 Falling Wedge (Bullish Reversal)', 'Reversal Pattern',
                    'BUY / LONG (BREAKOUT)', trigger, sl, pattern_h, curr_close, chg_pct, 94,
                    f"Falling wedge converging between highs ₹{h1:.1f}->₹{h2:.1f} and lows ₹{l1:.1f}->₹{l2:.1f}. Trigger: ₹{h2:.2f}.", df
                )

    # ─── 6. 🔴 RISING WEDGE (Bearish Reversal / Breakdown) ───────────────────
    if len(high_pivots) >= 2 and len(low_pivots) >= 2:
        h1, h2 = high_pivots[-2]['price'], high_pivots[-1]['price']
        l1, l2 = low_pivots[-2]['price'], low_pivots[-1]['price']
        
        if h2 > h1 and l2 > l1:
            high_rise = h2 - h1
            low_rise = l2 - l1
            if low_rise > high_rise * 1.10 and (h2 - l1) / l1 * 100 >= min_h_pct:
                trigger = round(l2 * 0.998, 2)
                sl = round(h2 * 1.015, 2)
                pattern_h = h2 - l1
                return build_actionable_trade_setup(
                    ticker, name, timeframe, '🔴 Rising Wedge (Bearish Reversal)', 'Reversal Pattern',
                    'SELL / SHORT (BREAKDOWN)', trigger, sl, pattern_h, curr_close, chg_pct, 93,
                    f"Rising wedge converging between highs ₹{h1:.1f}->₹{h2:.1f} and lows ₹{l1:.1f}->₹{l2:.1f}. Breakdown trigger: ₹{l2:.2f}.", df
                )

    # ─── 7. 🚩 BULLISH PENNANT / RECTANGLE ────────────────────────────────────
    if len(df) >= 15:
        lookback = max(0, len(df) - 15)
        pole_low = df['Low'].iloc[lookback:lookback + 6].min()
        pole_high = df['High'].iloc[lookback + 3:len(df) - 3].max()
        pole_surge = (pole_high - pole_low) / pole_low * 100 if pole_low > 0 else 0.0
        
        if pole_surge >= min_pole_pct:
            box_low = df['Low'].iloc[-5:].min()
            box_high = df['High'].iloc[-5:].max()
            box_retrace = (pole_high - box_low) / (pole_high - pole_low) * 100
            
            if 8.0 <= box_retrace <= 45.0:
                trigger = round(box_high * 1.002, 2)
                sl = round(box_low * 0.985, 2)
                pole_h = pole_high - pole_low
                return build_actionable_trade_setup(
                    ticker, name, timeframe, '🚩 Bullish Pennant / Rectangle', 'Continuation Pattern',
                    'BUY / LONG (CONTINUATION)', trigger, sl, pole_h, curr_close, chg_pct, 95,
                    f"Impulse pole surged +{pole_surge:.1f}%. Pennant box retrace {box_retrace:.1f}%. Trigger: ₹{box_high:.2f}.", df
                )

    # ─── 8. 🚩 BEARISH PENNANT / RECTANGLE ────────────────────────────────────
    if len(df) >= 15:
        lookback = max(0, len(df) - 15)
        pole_high = df['High'].iloc[lookback:lookback + 6].max()
        pole_low = df['Low'].iloc[lookback + 3:len(df) - 3].min()
        pole_drop = (pole_high - pole_low) / pole_high * 100 if pole_high > 0 else 0.0
        
        if pole_drop >= min_pole_pct:
            box_high = df['High'].iloc[-5:].max()
            box_low = df['Low'].iloc[-5:].min()
            box_retrace = (box_high - pole_low) / (pole_high - pole_low) * 100
            
            if 8.0 <= box_retrace <= 45.0:
                trigger = round(box_low * 0.998, 2)
                sl = round(box_high * 1.015, 2)
                pole_h = pole_high - pole_low
                return build_actionable_trade_setup(
                    ticker, name, timeframe, '🚩 Bearish Pennant / Rectangle', 'Continuation Pattern',
                    'SELL / SHORT (CONTINUATION)', trigger, sl, pole_h, curr_close, chg_pct, 94,
                    f"Waterfall pole dropped -{pole_drop:.1f}%. Box retrace {box_retrace:.1f}%. Breakdown trigger: ₹{box_low:.2f}.", df
                )

    # ─── 9. 📐 ASCENDING TRIANGLE ──────────────────────────────────────────────
    if len(high_pivots) >= 2 and len(low_pivots) >= 2:
        h1, h2 = high_pivots[-2]['price'], high_pivots[-1]['price']
        l1, l2 = low_pivots[-2]['price'], low_pivots[-1]['price']
        
        flat_top_diff = abs(h1 - h2) / h1 * 100
        if flat_top_diff <= (max_peak_diff_pct + 0.5) and l2 > l1 * 1.008 and (h2 - l1) / l1 * 100 >= min_h_pct:
            trigger = round(h2 * 1.002, 2)
            sl = round(l2 * 0.985, 2)
            tri_h = h2 - l1
            return build_actionable_trade_setup(
                ticker, name, timeframe, '📐 Ascending Triangle', 'Bilateral Pattern',
                'BUY / LONG (BREAKOUT)', trigger, sl, tri_h, curr_close, chg_pct, 95,
                f"Flat resistance ceiling at ₹{h2:.2f} with rising support lows ₹{l1:.1f}->₹{l2:.1f}. Breakout trigger: ₹{h2:.2f}.", df
            )

    # ─── 10. 📐 DESCENDING TRIANGLE ───────────────────────────────────────────
    if len(high_pivots) >= 2 and len(low_pivots) >= 2:
        h1, h2 = high_pivots[-2]['price'], high_pivots[-1]['price']
        l1, l2 = low_pivots[-2]['price'], low_pivots[-1]['price']
        
        flat_bot_diff = abs(l1 - l2) / l1 * 100
        if flat_bot_diff <= (max_peak_diff_pct + 0.5) and h2 < h1 * 0.992 and (h1 - l2) / l2 * 100 >= min_h_pct:
            trigger = round(l2 * 0.998, 2)
            sl = round(h2 * 1.015, 2)
            tri_h = h1 - l2
            return build_actionable_trade_setup(
                ticker, name, timeframe, '📐 Descending Triangle', 'Bilateral Pattern',
                'SELL / SHORT (BREAKDOWN)', trigger, sl, tri_h, curr_close, chg_pct, 94,
                f"Flat support floor at ₹{l2:.2f} with falling resistance highs ₹{h1:.1f}->₹{h2:.1f}. Breakdown trigger: ₹{l2:.2f}.", df
            )

    # ─── 11. ⚡ SYMMETRICAL TRIANGLE ───────────────────────────────────────────
    if len(high_pivots) >= 2 and len(low_pivots) >= 2:
        h1, h2 = high_pivots[-2]['price'], high_pivots[-1]['price']
        l1, l2 = low_pivots[-2]['price'], low_pivots[-1]['price']
        
        if h2 < h1 and l2 > l1 and (h1 - l1) / l1 * 100 >= min_h_pct:
            is_bull = curr_close >= h2 * 0.998
            direction = 'BUY / LONG (BREAKOUT)' if is_bull else 'SELL / SHORT (BREAKDOWN)'
            trigger = round(h2 * 1.002, 2) if is_bull else round(l2 * 0.998, 2)
            sl = round(l2 * 0.985, 2) if is_bull else round(h2 * 1.015, 2)
            tri_h = h1 - l1
            return build_actionable_trade_setup(
                ticker, name, timeframe, '⚡ Symmetrical Triangle', 'Bilateral Pattern',
                direction, trigger, sl, tri_h, curr_close, chg_pct, 93,
                f"Symmetrical triangle coiling between highs ₹{h1:.1f}->₹{h2:.1f} and lows ₹{l1:.1f}->₹{l2:.1f}. Apex trigger: ₹{trigger:.2f}.", df
            )

    return None

def scan_trade_chart_for_ticker(ticker: str, timeframe: str = '1-Hour') -> Optional[Dict]:
    """Scan a single ticker for Trade Chart patterns across 15m, 1h, Daily, and Weekly timeframes."""
    try:
        info = get_stock_info(ticker)
        name = info.get('name', ticker)
        
        rt_price, prev_close = safe_get_fast_info(ticker)
        
        tf_lower = timeframe.lower()
        if '15' in tf_lower:
            df = safe_download(ticker, period='1mo', interval='15m')
        elif '1h' in tf_lower or 'hour' in tf_lower:
            df = safe_download(ticker, period='2mo', interval='1h')
        elif 'week' in tf_lower:
            df = safe_download(ticker, period='3y', interval='1wk')
        else:
            df, rt_price, prev_close, _ = fetch_stock_data_realtime(ticker, period='1y')
            
        if df is None or df.empty or len(df) < 15:
            return None
            
        if rt_price and float(rt_price) > 0:
            rt_price = float(rt_price)
            last_idx = df.index[-1]
            df.loc[last_idx, 'Close'] = rt_price
            if rt_price > df.loc[last_idx, 'High']:
                df.loc[last_idx, 'High'] = rt_price
            if rt_price < df.loc[last_idx, 'Low']:
                df.loc[last_idx, 'Low'] = rt_price
        else:
            rt_price = float(df['Close'].iloc[-1])
            
        if not prev_close or float(prev_close) <= 0:
            prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else rt_price
        else:
            prev_close = float(prev_close)
            
        chg_pct = ((rt_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
        df = compute_all_indicators(df)
        
        res = detect_trade_chart_pattern(df, ticker, name, rt_price=rt_price, prev_close=prev_close, chg_pct=chg_pct, timeframe=timeframe)
        if res:
            consensus = calculate_unified_consensus(df, ticker, pattern_setup=res, timeframe=timeframe)
            res['Conviction'] = f"{consensus['conviction_score']}% ({consensus['master_direction']} Harmonized)"
            res['Consensus_Action'] = consensus['action']
        return res
    except Exception as e:
        logger.debug(f"Error scanning Trade Chart pattern for {ticker}: {e}")
        return None

def scan_all_trade_charts(tickers: List[str], timeframe: str = '1-Hour', progress_callback=None) -> pd.DataFrame:
    """
    Concurrent multi-threaded scanner for Trade Chart patterns.
    Prioritizes VERY FRESH & FRESH actionable breakout/breakdown signals at the top.
    """
    results = []
    total = len(tickers)
    completed_count = 0
    lock = threading.Lock()
    
    max_workers = 16 if total > 100 else 10
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(scan_trade_chart_for_ticker, ticker, timeframe): ticker
            for ticker in tickers
        }
        
        for future in concurrent.futures.as_completed(future_map):
            ticker = future_map[future]
            try:
                res = future.result()
                if res:
                    results.append(res)
            except Exception:
                pass
                
            with lock:
                completed_count += 1
                if progress_callback:
                    info = get_stock_info(ticker)
                    progress_callback(completed_count, total, info.get('name', ticker))
                    
    df_res = pd.DataFrame(results)
    if not df_res.empty:
        freshness_order = {
            'VERY FRESH': 1,
            'FRESH': 2,
            'PRE-BREAKOUT': 3,
            'PRE-BREAKDOWN': 3,
            'EXTENDED': 4,
            'TARGET 1 HIT': 5,
            'TARGET 2 HIT': 6,
            'TARGET 3 HIT': 7,
            'EXPIRED': 8
        }
        df_res['Priority'] = df_res['Freshness'].map(lambda f: freshness_order.get(str(f), 9))
        df_res = df_res.sort_values(by=['Priority', 'Change%'], ascending=[True, False]).drop(columns=['Priority']).reset_index(drop=True)
    return df_res
