import yfinance as yf
import pandas as pd

test_symbols = [
    ('NIFTY 50', '^NSEI'),
    ('BANK NIFTY', '^NSEBANK'),
    ('SENSEX', '^BSESN'),
    ('NIFTY FIN SERVICE', '^CNXFIN'),
    ('NIFTY NEXT 50', '^CNXNXT50'),
    ('NIFTY MIDCAP 50', '^NSEMDCP50'),
    ('NIFTY MIDCAP 100', '^CRSLDX'),
    ('NIFTY 50 ETF', 'NIFTYBEES.NS'),
    ('BANK NIFTY ETF', 'BANKBEES.NS')
]

print("Testing Indices...")
for name, sym in test_symbols:
    try:
        df = yf.download(sym, period='1mo', interval='1h', progress=False)
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            df = df.dropna(subset=['Close'])
            print(f"SUCCESS: {name} ({sym}) -> {len(df)} 1h bars | Latest: {float(df['Close'].iloc[-1]):.2f}")
        else:
            print(f"FAILED (Empty): {name} ({sym})")
    except Exception as e:
        print(f"ERROR: {name} ({sym}) -> {e}")
