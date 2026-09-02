"""
Stock Scanner Engine.

Orchestrates data fetching, indicator computation, and scoring across stock universes
using high-performance multi-threading with REAL-TIME live tick quote synchronization.
"""

import time
import logging
import pandas as pd
import yfinance as yf
from typing import Callable, Optional, List, Dict
import concurrent.futures
import threading

from indicators import compute_all_indicators
from scoring import score_stock
from stock_universe import (
    get_nifty50_tickers,
    get_nifty200_tickers,
    get_nifty500_tickers,
    get_stock_info
)
from safe_data_pipeline import safe_download, safe_get_fast_info

logger = logging.getLogger(__name__)

def fetch_stock_data_realtime(ticker: str, period: str = '3mo') -> tuple:
    """
    Fetch OHLCV data safely without YFRateLimitError exceptions.
    Returns (df, rt_price, prev_close, change_pct).
    """
    try:
        rt_price, prev_close = safe_get_fast_info(ticker)
        df = safe_download(ticker, period=period, interval='1d')
        
        if df is None or df.empty or len(df) < 5:
            return None, None, None, None
            
        rt_price = rt_price or float(df['Close'].iloc[-1])
        prev_close = prev_close or (float(df['Close'].iloc[-2]) if len(df) > 1 else rt_price)
        chg_pct = ((rt_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
        
        df = compute_all_indicators(df)
        return df, rt_price, prev_close, chg_pct
    except Exception as e:
        logger.debug(f"Error fetching realtime data for {ticker}: {e}")
        return None, None, None, None

def fetch_single_stock_scan(ticker: str, period: str, mode: str) -> Optional[Dict]:
    """Fetch and score a single stock with real-time price."""
    try:
        df, rt_price, prev_close, chg_pct = fetch_stock_data_realtime(ticker, period=period)
        if df is None or df.empty:
            return None
            
        scores = score_stock(df, mode)
        info = get_stock_info(ticker)
        name = info.get('name', ticker)
        sector = info.get('sector', 'NSE Equities / F&O')
        
        # Override with exact real-time prices
        close_val = rt_price if rt_price is not None else (scores.get('close') or 0.0)
        change_val = chg_pct if chg_pct is not None else (scores.get('change_pct') or 0.0)
        
        return {
            'Ticker': ticker,
            'Name': name,
            'Sector': sector,
            'Close': round(float(close_val), 2),
            'Change%': round(float(change_val), 2),
            'Action': scores.get('action', 'NO TRADE'),
            'Entry': scores.get('entry', 0.0),
            'Stop_Loss': scores.get('stop_loss', 0.0),
            'Target_1': scores.get('target_1', 0.0),
            'Target_2': scores.get('target_2', 0.0),
            'Risk': scores.get('risk_per_share', 0.0),
            'RR_Ratio': scores.get('rr_ratio', 'N/A'),
            'Time_Cycle': scores.get('time_cycle', 'N/A'),
            'Rationale': scores.get('rationale', ''),
            'RSI': scores.get('rsi_value', None),
            'Stoch_K': scores.get('stoch_k_value', None),
            'BB_PctB': scores.get('bb_pctb_value', None),
            'ADX': scores.get('adx_value', None),
            'RSI_Score': scores.get('rsi_score', 0),
            'MACD_Score': scores.get('macd_score', 0),
            'EMA_Score': scores.get('ema_score', 0),
            'Stoch_Score': scores.get('stoch_score', 0),
            'BB_Score': scores.get('bb_score', 0),
            'ADX_Score': scores.get('adx_score', 0),
            'Composite_Score': scores.get('composite_score', 0),
            'Signal': scores.get('signal', 'Neutral'),
            'Signal_Color': scores.get('signal_color', '#9CA3AF')
        }
    except Exception as e:
        logger.debug(f"Error scanning {ticker}: {e}")
        return None

def scan_stocks(
    tickers: list[str],
    mode: str = 'daily',
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> pd.DataFrame:
    """Scan a list of stocks concurrently and return scored results with real-time prices."""
    results = []
    period = '3mo' if mode == 'daily' else '1y'
    total_tickers = len(tickers)
    completed_count = 0
    lock = threading.Lock()
    
    max_workers = 16 if total_tickers > 100 else 10
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(fetch_single_stock_scan, ticker, period, mode): ticker
            for ticker in tickers
        }
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                res = future.result()
                if res:
                    results.append(res)
            except Exception as e:
                logger.debug(f"Scan future error for {ticker}: {e}")
                
            with lock:
                completed_count += 1
                if progress_callback:
                    info = get_stock_info(ticker)
                    progress_callback(completed_count, total_tickers, info.get('name', ticker))
                    
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results.sort_values(by='Composite_Score', ascending=False).reset_index(drop=True)
        
    return df_results

def get_trade_setups(results_df: pd.DataFrame) -> pd.DataFrame:
    """Filter stocks that have active actionable trade signals (BUY or SELL)."""
    if results_df.empty or 'Action' not in results_df.columns:
        return results_df
    return results_df[results_df['Action'].str.contains('BUY|SELL', case=False, na=False)].reset_index(drop=True)

def get_stock_detail(ticker: str, period: str = '1y') -> dict:
    """Get detailed data for a single stock for the detail view with real-time price."""
    df, rt_price, prev_close, chg_pct = fetch_stock_data_realtime(ticker, period=period)
    if df is None or df.empty:
        return {
            'ticker': ticker,
            'df': pd.DataFrame(),
            'scores': {},
            'info': get_stock_info(ticker)
        }
        
    scores = score_stock(df, mode='positional')
    if rt_price:
        scores['close'] = rt_price
    if chg_pct:
        scores['change_pct'] = chg_pct
    info = get_stock_info(ticker)
    
    return {
        'ticker': ticker,
        'df': df,
        'scores': scores,
        'info': info
    }

def get_bull_stocks(results_df: pd.DataFrame) -> pd.DataFrame:
    """Filter and return stocks with Signal containing 'Bull', sorted by Composite_Score desc."""
    if results_df.empty or 'Signal' not in results_df.columns:
        return results_df
    bull_df = results_df[results_df['Signal'].str.contains('Bull', case=False, na=False)]
    return bull_df.sort_values(by='Composite_Score', ascending=False).reset_index(drop=True)

def get_bear_stocks(results_df: pd.DataFrame) -> pd.DataFrame:
    """Filter and return stocks with Signal containing 'Bear', sorted by Composite_Score asc."""
    if results_df.empty or 'Signal' not in results_df.columns:
        return results_df
    bear_df = results_df[results_df['Signal'].str.contains('Bear', case=False, na=False)]
    return bear_df.sort_values(by='Composite_Score', ascending=True).reset_index(drop=True)
