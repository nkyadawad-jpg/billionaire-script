import sys
import os
import io
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_universe import get_nifty50_tickers
from next_day_mover import scan_next_day_movers

def main():
    tickers = get_nifty50_tickers()
    print(f"Scanning {len(tickers)} stocks for Next-Day 4%+ Movers...")
    df = scan_next_day_movers(tickers)
    
    if not df.empty:
        print("\n" + "="*85)
        print("NEXT-DAY 4%+ EXPLOSIVE MOVER CANDIDATES (The Ultimate Edge by Noeman)")
        print("="*85)
        for _, r in df.iterrows():
            print(f"[{r['Direction']}] {r['Ticker']} - {r['Name']}")
            print(f"  Probability Score: {r['Probability']} | Expected Move: {r['Expected_Move']}")
            print(f"  Trigger Entry: Rs {r['Trigger_Entry']:.2f} | Stop Loss: Rs {r['Stop_Loss']:.2f}")
            print(f"  Target 1 (+4.5%): Rs {r['Target_1_4Pct']:.2f} | Target 2 (+7.5%): Rs {r['Target_2_7Pct']:.2f}")
            print(f"  R:R: {r['Risk_Reward']} | Time Cycle: {r['Time_Cycle']}")
            print(f"  Pattern: {r['Setup_Pattern']} | RVOL: {r['RVOL']} | ATR: {r['ATR_Pct']}")
            print(f"  Rationale: {r['Rationale']}")
            print("-" * 80)
    else:
        print("No extreme 4%+ setups triggered in this run.")

if __name__ == '__main__':
    main()
