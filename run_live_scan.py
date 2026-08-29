import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner import scan_stocks, get_bull_stocks, get_bear_stocks
from stock_universe import get_nifty50_tickers, get_nifty200_tickers

def run():
    tickers = get_nifty50_tickers()
    print(f"Scanning {len(tickers)} F&O stocks for Daily (Intraday) Mode...")
    daily_results = scan_stocks(tickers, mode='daily')
    
    print(f"Scanning {len(tickers)} F&O stocks for Positional Mode...")
    pos_results = scan_stocks(tickers, mode='positional')
    
    print("\n" + "="*80)
    print("DAILY / INTRADAY ANALYSIS SUMMARY")
    print("="*80)
    print(daily_results[['Ticker', 'Name', 'Close', 'Change%', 'Composite_Score', 'Signal', 'Action', 'Entry', 'Stop_Loss', 'Target_1', 'Target_2', 'RR_Ratio', 'RSI', 'ADX', 'Rationale']].to_string())
    
    print("\n" + "="*80)
    print("POSITIONAL ANALYSIS SUMMARY")
    print("="*80)
    print(pos_results[['Ticker', 'Name', 'Close', 'Change%', 'Composite_Score', 'Signal', 'Action', 'Entry', 'Stop_Loss', 'Target_1', 'Target_2', 'RR_Ratio', 'RSI', 'ADX', 'Rationale']].to_string())

if __name__ == '__main__':
    run()
