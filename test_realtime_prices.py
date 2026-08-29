import yfinance as yf
import pandas as pd

tickers = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'SBIN.NS']

for t in tickers:
    tick = yf.Ticker(t)
    fi = getattr(tick, 'fast_info', None)
    last_price = None
    prev_close = None
    if fi:
        last_price = getattr(fi, 'last_price', None) or getattr(fi, 'regular_market_price', None)
        prev_close = getattr(fi, 'previous_close', None) or getattr(fi, 'regular_market_previous_close', None)
    
    df = yf.download(t, period='5d', interval='1d', progress=False)
    if df is not None and not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        df_last = float(df['Close'].iloc[-1])
        df_prev = float(df['Close'].iloc[-2]) if len(df) > 1 else df_last
    else:
        df_last = None
        df_prev = None
        
    print(f"{t}:")
    print(f"  FastInfo: Last={last_price}, PrevClose={prev_close}")
    print(f"  DF 1d:    Last={df_last}, PrevClose={df_prev}")
