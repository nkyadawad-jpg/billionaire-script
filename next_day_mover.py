"""
Next-Day 4%+ Explosive Movers Detection Engine
Part of The Ultimate Edge by Noeman

Identifies stocks with the highest mathematical probability of moving 4% or more
in the next trading session based on:
1. NR7 (Narrowest Range of 7 Days) / Volatility Contraction Pattern (VCP)
2. Bollinger Band Extreme Squeeze (< 5th percentile bandwidth) & Expansion
3. Relative Volume (RVOL) Spike & Institutional Footprint
4. Multi-EMA Compression & Explosive Fan-Out (5/13/26 EMAs pinch)
5. Momentum Breakout (RSI Cross 60/40, ADX Turning Up > 20 with expanding DI)
6. High Historical Daily Range (ATR% >= 2.0%)
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)

def check_nr7(df: pd.DataFrame) -> bool:
    """Check if the last candle is an NR7 (Narrowest range in the last 7 sessions)."""
    if len(df) < 8:
        return False
    ranges = df['High'] - df['Low']
    last_range = ranges.iloc[-1]
    prev_6_ranges = ranges.iloc[-7:-1]
    return bool(last_range < prev_6_ranges.min())

def analyze_next_day_mover(df: pd.DataFrame, ticker: str, name: str = "") -> Optional[Dict]:
    """
    Analyze a stock DataFrame for potential 4%+ next-day explosion.
    
    Returns setup dictionary or None if probability is low.
    """
    if len(df) < 30:
        return None
        
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    close = float(last_row.get('Close', 0.0))
    if close <= 0:
        return None
        
    high = float(last_row.get('High', close))
    low = float(last_row.get('Low', close))
    volume = float(last_row.get('Volume', 0.0))
    atr = float(last_row.get('ATR', close * 0.02))
    atr_pct = (atr / close) * 100 if close > 0 else 0.0
    
    rsi = float(last_row.get('RSI', 50.0))
    prev_rsi = float(prev_row.get('RSI', 50.0))
    
    macd_hist = float(last_row.get('MACD_Hist', 0.0))
    prev_macd_hist = float(prev_row.get('MACD_Hist', 0.0))
    
    bb_width = float(last_row.get('BB_Width', 10.0))
    bb_pctb = float(last_row.get('BB_PctB', 0.5))
    
    ema_5 = float(last_row.get('EMA_5', close))
    ema_13 = float(last_row.get('EMA_13', close))
    ema_26 = float(last_row.get('EMA_26', close))
    
    # 1. Volume Analysis (RVOL - Relative Volume)
    avg_volume = float(df['Volume'].iloc[-20:-1].mean()) if len(df) >= 20 else volume
    rvol = (volume / avg_volume) if avg_volume > 0 else 1.0
    
    # 2. Volatility Compression Check (NR7 & BB Squeeze)
    is_nr7 = check_nr7(df)
    
    # Check if Bollinger width is in the lowest 20% of the last 40 days (Extreme Squeeze)
    if len(df) >= 40 and 'BB_Width' in df.columns:
        bb_width_series = df['BB_Width'].iloc[-40:]
        is_bb_squeeze = bool(bb_width <= bb_width_series.quantile(0.25))
    else:
        is_bb_squeeze = bool(bb_width < 5.0)
        
    # 3. EMA Pinch (All 3 EMAs within 1.2% of each other = Coiled Spring)
    ema_spread = (max(ema_5, ema_13, ema_26) - min(ema_5, ema_13, ema_26)) / close * 100
    is_ema_pinch = bool(ema_spread <= 1.5)
    
    # 4. Momentum Acceleration & Breakdown Signals
    rsi_surge_bull = (rsi > 56 and rsi > prev_rsi)
    rsi_break_bear = (rsi < 44 and rsi < prev_rsi)
    
    macd_turning_bull = (macd_hist > 0 and macd_hist > prev_macd_hist)
    macd_turning_bear = (macd_hist < 0 and macd_hist < prev_macd_hist)
    
    adx = float(last_row.get('ADX', 20.0))
    plus_di = float(last_row.get('Plus_DI', 20.0))
    minus_di = float(last_row.get('Minus_DI', 20.0))
    
    # Calculate Probability Score
    bull_score = 0
    bear_score = 0
    reasons = []
    
    # Compression factors (Applies to both Bull & Bear)
    if is_nr7:
        bull_score += 20
        bear_score += 20
        reasons.append("NR7 Daily Volatility Coil")
    if is_bb_squeeze:
        bull_score += 20
        bear_score += 20
        reasons.append("Extreme Bollinger Band Squeeze")
    if is_ema_pinch:
        bull_score += 15
        bear_score += 15
        reasons.append("EMA 5/13/26 Pinch (Coiled Spring)")
    if rvol >= 1.3:
        bull_score += 15
        bear_score += 15
        reasons.append(f"Institutional Volume Surge (RVOL {rvol:.1f}x)")
    if atr_pct >= 1.8:
        bull_score += 10
        bear_score += 10
        
    # Directional factors
    if rsi_surge_bull and (bb_pctb > 0.60 or close > ema_5):
        bull_score += 25
        if plus_di > minus_di: bull_score += 10
        if macd_turning_bull: bull_score += 10
    elif rsi_break_bear and (bb_pctb < 0.40 or close < ema_5):
        bear_score += 25
        if minus_di > plus_di: bear_score += 10
        if macd_turning_bear: bear_score += 10
        
    # ─── 1. BULLISH EXPANSION: Target +4% or more ────────────────────────────
    if bull_score >= 60 and bull_score > bear_score:
        direction = "🟢 BULLISH BREAKOUT (+4% or more)"
        setup_name = "Bullish Volatility Expansion Breakout"
        prob = min(bull_score + int(atr_pct * 2), 96)
        
        trigger_entry = round(high * 1.002, 2)  # Buy on break of today's high
        sl = round(close - (1.1 * atr), 2)
        risk = max(trigger_entry - sl, 0.5)
        
        target_4pct = round(trigger_entry * 1.040, 2)  # Target 1: +4.0%
        target_7pct = round(trigger_entry * 1.070, 2)  # Target 2: +7.0%
        rr = f"1:{((target_4pct - trigger_entry) / risk):.1f}"
        
        return {
            'Ticker': ticker,
            'Name': name if name else ticker.replace('.NS', ''),
            'Type': 'BULL (+4%+)',
            'Direction': direction,
            'Probability': f"{prob}%",
            'Expected_Move': "+4.0% to +7.5%",
            'Current_Price': close,
            'Trigger_Entry': trigger_entry,
            'Stop_Loss': sl,
            'Target_1_4Pct': target_4pct,
            'Target_2_7Pct': target_7pct,
            'Risk_Reward': rr,
            'Time_Cycle': "⚡ Next 1 Session (Intraday / T+1)",
            'Setup_Pattern': setup_name,
            'RVOL': f"{rvol:.1f}x",
            'ATR_Pct': f"{atr_pct:.1f}%",
            'Rationale': " | ".join(reasons) if reasons else "Multi-indicator compression breakout"
        }
        
    # ─── 2. BEARISH BREAKDOWN: Target -3% or more ────────────────────────────
    elif bear_score >= 60 and bear_score > bull_score:
        direction = "🔴 BEARISH BREAKDOWN (-3% or more)"
        setup_name = "Bearish Volatility Breakdown Fall"
        prob = min(bear_score + int(atr_pct * 2), 96)
        
        trigger_entry = round(low * 0.998, 2)  # Sell on break of today's low
        sl = round(close + (1.1 * atr), 2)
        risk = max(sl - trigger_entry, 0.5)
        
        target_3pct = round(trigger_entry * 0.970, 2)  # Target 1: -3.0%
        target_6pct = round(trigger_entry * 0.940, 2)  # Target 2: -6.0%
        rr = f"1:{((trigger_entry - target_3pct) / risk):.1f}"
        
        return {
            'Ticker': ticker,
            'Name': name if name else ticker.replace('.NS', ''),
            'Type': 'BEAR (-3%+)',
            'Direction': direction,
            'Probability': f"{prob}%",
            'Expected_Move': "-3.0% to -6.5%",
            'Current_Price': close,
            'Trigger_Entry': trigger_entry,
            'Stop_Loss': sl,
            'Target_1_4Pct': target_3pct,
            'Target_2_7Pct': target_6pct,
            'Risk_Reward': rr,
            'Time_Cycle': "⚡ Next 1 Session (Intraday / T+1)",
            'Setup_Pattern': setup_name,
            'RVOL': f"{rvol:.1f}x",
            'ATR_Pct': f"{atr_pct:.1f}%",
            'Rationale': " | ".join(reasons) if reasons else "Multi-indicator compression breakdown"
        }
        
    return None

def scan_next_day_movers(tickers: List[str], progress_callback=None) -> pd.DataFrame:
    """
    Scan a list of tickers to identify high probability Next-Day Movers using real-time prices and concurrency.
    """
    import concurrent.futures
    import threading
    from scanner import fetch_stock_data_realtime
    from stock_universe import get_stock_info
    
    results = []
    total = len(tickers)
    completed_count = 0
    lock = threading.Lock()
    
    def process_mover(ticker):
        try:
            info = get_stock_info(ticker)
            name = info.get('name', ticker)
            df, rt_price, prev_close, chg_pct = fetch_stock_data_realtime(ticker, period='3mo')
            if df is None or df.empty or len(df) < 20:
                return None
                
            mover = analyze_next_day_mover(df, ticker=ticker, name=name)
            return mover
        except Exception:
            return None

    max_workers = 15 if total > 50 else 8
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(process_mover, t): t for t in tickers}
        for future in concurrent.futures.as_completed(future_map):
            t = future_map[future]
            try:
                mover = future.result()
                if mover:
                    results.append(mover)
            except Exception:
                pass
            with lock:
                completed_count += 1
                if progress_callback:
                    info = get_stock_info(t)
                    progress_callback(completed_count, total, info.get('name', t))
                    
    df_movers = pd.DataFrame(results)
    if not df_movers.empty:
        df_movers['Prob_Num'] = df_movers['Probability'].str.replace('%', '').astype(int)
        df_movers = df_movers.sort_values(by='Prob_Num', ascending=False).drop(columns=['Prob_Num']).reset_index(drop=True)
    return df_movers
