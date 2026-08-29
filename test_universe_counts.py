import time
import concurrent.futures
from stock_universe import get_nifty50_tickers, get_nifty200_tickers, get_nifty500_tickers

print("Testing Universe Lengths:")
n50 = get_nifty50_tickers()
n200 = get_nifty200_tickers()
n500 = get_nifty500_tickers()

print(f"NIFTY 50 Count: {len(n50)}")
print(f"NIFTY 200 / F&O Count: {len(n200)}")
print(f"NIFTY 500 Count: {len(n500)}")
