import yfinance as yf
import pandas as pd

indices_map = {
    'NIFTY 50': ['^NSEI', 'NIFTYBEES.NS'],
    'BANK NIFTY': ['^NSEBANK', 'BANKBEES.NS'],
    'SENSEX': ['^BSESN'],
    'NIFTY FIN SERVICE': ['^CNXFIN', 'FINNIFTY.NS'],
    'NIFTY MID SELECT': ['^NSEMDCP50', 'MID150BEES.NS', 'NIFTY_MID_SELECT.NS'],
    'NIFTY NEXT 50': ['^CRSLDX', 'JUNIORBEES.NS']
}

for name, syms in indices_map.items():
    print(f"\n--- {name} ---")
    for sym in syms:
        try:
            t = yf.Ticker(sym)
            fi = getattr(t, 'fast_info', None)
            last_price = None
            if fi:
                last_price = getattr(fi, 'last_price', None) or getattr(fi, 'regular_market_price', None) or getattr(fi, 'previous_close', None)
            
            df = yf.download(sym, period='5d', interval='1d', progress=False)
            if df is not None and not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
                df = df.dropna(subset=['Close'])
                close_val = float(df['Close'].iloc[-1])
                prev_val = float(df['Close'].iloc[-2]) if len(df) > 1 else close_val
                chg = ((close_val - prev_val) / prev_val) * 100
                print(f"  {sym}: FastInfo={last_price} | DF Latest={close_val:.2f} ({chg:+.2f}%)")
            else:
                print(f"  {sym}: Empty DF, FastInfo={last_price}")
        except Exception as e:
            print(f"  {sym} error: {e}")
