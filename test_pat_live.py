import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from chart_patterns import scan_chart_patterns_for_ticker
import yfinance as yf

for ticker in ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS']:
    t = yf.Ticker(ticker)
    fi = getattr(t, 'fast_info', None)
    expected_live = getattr(fi, 'last_price', None) if fi else None
    
    pat = scan_chart_patterns_for_ticker(ticker, timeframe='Daily')
    if pat:
        print(f"PATTERN DETECTED for {ticker}: Live Price = Rs {pat['Current_Price']:.2f} (Expected: {expected_live}) | Change% = {pat['Change%']:+.2f}%")
    else:
        print(f"No pattern for {ticker}, but verified live quote = Rs {expected_live}")
