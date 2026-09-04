"""
NSE Major Indices Elliott Wave Analysis Engine (NIFTY 50 & SENSEX Only)
Wall Street Institutional Grade — 1-Hourly & 4-Hourly Timeframes
Part of The Ultimate Edge by Noeman
"""

import numpy as np
import pandas as pd
import yfinance as yf
import logging
from typing import Dict, List, Optional
from indicators import compute_all_indicators
from elliott_wave import analyze_elliott_wave

logger = logging.getLogger(__name__)

# Only NIFTY 50 and SENSEX as requested
NSE_INDICES = {
    'NIFTY 50': {
        'symbol': '^NSEI',
        'desc': 'Benchmark National Stock Exchange 50 Bluechips',
        'strike_step': 50,
        'etf': 'NIFTYBEES.NS'
    },
    'SENSEX': {
        'symbol': '^BSESN',
        'desc': 'Premier Bombay Stock Exchange 30 Bluechips',
        'strike_step': 100,
        'etf': 'SENSEXBEES.NS'
    }
}

def resample_to_4h(df_1h: pd.DataFrame) -> pd.DataFrame:
    """Resample 1-hour OHLCV data into 4-hour bars."""
    if df_1h.empty:
        return df_1h
        
    df_4h = df_1h.resample('4h').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna(subset=['Close'])
    
    return df_4h

def calculate_index_option_strike(price: float, direction: str, strike_step: int = 50) -> Dict:
    """
    Calculate optimal Wall Street Option Buying Strike (Delta 0.50 - 0.60)
    for index trading to maximize convexity and minimize time decay.
    """
    rounded_atm = round(price / strike_step) * strike_step
    
    if 'BUY' in direction or 'BULL' in direction:
        # For Bullish impulse: Choose slightly ITM or ATM Strike for high delta
        recommended_strike = rounded_atm
        strike_label = f"{int(recommended_strike)} CE (CALL)"
        option_strategy = f"BUY {strike_label} — Monthly/Weekly Expiry"
        expected_premium_move = "Target: +100% to +250% Gain on Premium (Wave 3 Explosion)"
        option_sl = "Hard SL: -35% of Premium Paid"
        cash_equiv = "Or Buy Cash ETF (NIFTYBEES / SENSEX ETF)"
    else:
        # For Bearish breakdown: Choose ATM or slightly ITM PE
        recommended_strike = rounded_atm
        strike_label = f"{int(recommended_strike)} PE (PUT)"
        option_strategy = f"BUY {strike_label} — Monthly/Weekly Expiry"
        expected_premium_move = "Target: +120% to +300% Gain on Premium (Waterfall Leg)"
        option_sl = "Hard SL: -35% of Premium Paid"
        cash_equiv = "Hedge Cash Portfolio or Short Futures"
        
    return {
        'strike_label': strike_label,
        'option_strategy': option_strategy,
        'expected_premium_move': expected_premium_move,
        'option_sl': option_sl,
        'cash_equiv': cash_equiv
    }

def analyze_single_index(name: str, symbol: str, strike_step: int = 50) -> Dict:
    """
    Fetch and analyze real-time 1-Hour and 4-Hour Elliott Wave setups for NIFTY 50 and SENSEX.
    """
    try:
        # 1. Fetch 1-hour data (last 2 months)
        df_1h = yf.download(symbol, period='2mo', interval='1h', progress=False)
        if df_1h is None or df_1h.empty:
            df_1h = yf.download(symbol, period='6mo', interval='1d', progress=False)
            
        if df_1h is None or df_1h.empty:
            return {'name': name, 'symbol': symbol, 'valid': False, 'error': 'No data'}
            
        if isinstance(df_1h.columns, pd.MultiIndex):
            df_1h.columns = [c[0] for c in df_1h.columns]
            
        df_1h = df_1h.dropna(subset=['Close'])
        df_1h = compute_all_indicators(df_1h)
        
        # 2. Build 4-Hour data
        df_4h = resample_to_4h(df_1h)
        if len(df_4h) >= 15:
            df_4h = compute_all_indicators(df_4h)
            ew_4h = analyze_elliott_wave(df_4h, timeframe='daily')
        else:
            ew_4h = {'setup_type': 'NEUTRAL', 'wave_phase': 'Developing 4-Hour Wave Structure'}
            
        ew_1h = analyze_elliott_wave(df_1h, timeframe='daily')
        
        # 3. Get Real-Time Price
        last_close = float(df_1h['Close'].iloc[-1])
        prev_close = float(df_1h['Close'].iloc[-2]) if len(df_1h) > 1 else last_close
        
        try:
            t = yf.Ticker(symbol)
            fi = getattr(t, 'fast_info', None)
            if fi:
                rt_price = getattr(fi, 'last_price', None) or getattr(fi, 'regular_market_price', None)
                if rt_price and float(rt_price) > 0:
                    last_close = float(rt_price)
                rt_prev = getattr(fi, 'previous_close', None)
                if rt_prev and float(rt_prev) > 0:
                    prev_close = float(rt_prev)
        except Exception:
            pass
            
        chg_pct = ((last_close - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
        
        # 4. Determine Option Trade Advice
        opt_advice_1h = calculate_index_option_strike(last_close, ew_1h.get('direction', 'BUY'), strike_step)
        opt_advice_4h = calculate_index_option_strike(last_close, ew_4h.get('direction', 'BUY'), strike_step)
        
        # 5. Determine Where the Wave is Heading
        heading_1h = "Consolidating / Rangebound"
        if ew_1h.get('target_1'):
            if 'BULL' in ew_1h.get('setup_type', ''):
                heading_1h = f"🚀 Heading UP to Target 1: {ew_1h['target_1']:,.1f} (+{((ew_1h['target_1']-last_close)/last_close*100):.1f}%)"
            elif 'BEAR' in ew_1h.get('setup_type', ''):
                heading_1h = f"🔻 Heading DOWN to Target 1: {ew_1h['target_1']:,.1f} ({((ew_1h['target_1']-last_close)/last_close*100):.1f}%)"
                
        heading_4h = "Consolidating / Rangebound"
        if ew_4h.get('target_1'):
            if 'BULL' in ew_4h.get('setup_type', ''):
                heading_4h = f"🚀 Heading UP to Target 1: {ew_4h['target_1']:,.1f} (+{((ew_4h['target_1']-last_close)/last_close*100):.1f}%)"
            elif 'BEAR' in ew_4h.get('setup_type', ''):
                heading_4h = f"🔻 Heading DOWN to Target 1: {ew_4h['target_1']:,.1f} ({((ew_4h['target_1']-last_close)/last_close*100):.1f}%)"

        return {
            'name': name,
            'symbol': symbol,
            'valid': True,
            'current_price': last_close,
            'change_pct': chg_pct,
            'ew_1h': ew_1h,
            'ew_4h': ew_4h,
            'df_1h': df_1h,
            'df_4h': df_4h,
            'heading_1h': heading_1h,
            'heading_4h': heading_4h,
            'option_advice_1h': opt_advice_1h,
            'option_advice_4h': opt_advice_4h
        }
        
    except Exception as e:
        logger.error(f"Error analyzing index {name}: {e}")
        return {'name': name, 'symbol': symbol, 'valid': False, 'error': str(e)}

def scan_all_nse_indices() -> List[Dict]:
    """Scan and analyze NIFTY 50 and SENSEX indices."""
    results = []
    for name, data in NSE_INDICES.items():
        res = analyze_single_index(name, data['symbol'], data['strike_step'])
        if res.get('valid'):
            results.append(res)
    return results
