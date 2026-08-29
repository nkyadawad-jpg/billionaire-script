import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import yfinance as yf
import pandas as pd
from indicators import compute_all_indicators

def get_realtime_stock_df(ticker: str, period: str = '3mo'):
    try:
        t = yf.Ticker(ticker)
        fi = getattr(t, 'fast_info', None)
        rt_price = None
        prev_close = None
        if fi:
            rt_price = getattr(fi, 'last_price', None) or getattr(fi, 'regular_market_price', None)
            prev_close = getattr(fi, 'previous_close', None) or getattr(fi, 'regular_market_previous_close', None)
            
        df = yf.download(ticker, period=period, interval='1d', progress=False)
        if df is None or df.empty:
            return None, None, None, None
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
            
        df = df.dropna(subset=['Open', 'High', 'Low'])
        if df.empty:
            return None, None, None, None
            
        if rt_price and float(rt_price) > 0:
            rt_price = float(rt_price)
            last_idx = df.index[-1]
            df.loc[last_idx, 'Close'] = rt_price
            if rt_price > df.loc[last_idx, 'High']:
                df.loc[last_idx, 'High'] = rt_price
            if rt_price < df.loc[last_idx, 'Low']:
                df.loc[last_idx, 'Low'] = rt_price
        else:
            rt_price = float(df['Close'].dropna().iloc[-1])
            
        if not prev_close or float(prev_close) <= 0:
            prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else rt_price
        else:
            prev_close = float(prev_close)
            
        chg_pct = ((rt_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
        
        df = compute_all_indicators(df)
        return df, rt_price, prev_close, chg_pct
    except Exception as e:
        print(f"Error for {ticker}: {e}")
        return None, None, None, None

for sym in ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']:
    df, rt, prev, chg = get_realtime_stock_df(sym)
    print(f"{sym} -> RealTime Live Close: Rs {rt:.2f} | Prev Close: Rs {prev:.2f} | Live Change%: {chg:+.2f}%")
