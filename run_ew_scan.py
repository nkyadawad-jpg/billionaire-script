import sys
import os
import io
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_universe import get_nifty50_tickers
from elliott_wave import scan_all_elliott_wave_setups

def main():
    tickers = get_nifty50_tickers()
    print(f"Scanning {len(tickers)} stocks for Multi-Timeframe Elliott Wave Setups...")
    ew_df = scan_all_elliott_wave_setups(tickers)
    
    if not ew_df.empty:
        print("\n" + "="*85)
        print("ACTIVE ELLIOTT WAVE OPPORTUNITIES (WEEKLY + DAILY)")
        print("="*85)
        for _, row in ew_df.iterrows():
            print(f"[{row['Timeframe']}] {row['Ticker']} - {row['Name']}")
            print(f"  Stage: {row['Wave_Stage']}")
            print(f"  Direction: {row['Direction']} | Confirmation: {row['Early_Confirmation']}")
            print(f"  Entry: Rs {row['Entry_Price']:.2f} | Invalidation SL: Rs {row['Invalidation_SL']:.2f}")
            print(f"  Fib Retracement: {row['Fib_Level']} | R:R: {row['RR_Ratio']}")
            print(f"  Target 1: Rs {row['Target_1']:.2f} | Target 2: Rs {row['Target_2']:.2f}")
            print(f"  Rationale: {row['Rationale']}")
            print("-" * 80)
    else:
        print("No active setups found.")

if __name__ == '__main__':
    main()
