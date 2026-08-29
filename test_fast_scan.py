import time
import concurrent.futures
import pandas as pd
import yfinance as yf
from indicators import compute_all_indicators
from scoring import score_stock
from stock_universe import get_stock_info, get_nifty200_tickers

def process_single_ticker(ticker, mode='daily'):
    try:
        df = yf.download(ticker, period='3mo', interval='1d', progress=False)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
        df = df.dropna(subset=['Close'])
        if len(df) < 20:
            return None
            
        df = compute_all_indicators(df)
        scores = score_stock(df, mode)
        info = get_stock_info(ticker)
        
        return {
            'Ticker': ticker,
            'Name': info.get('name', ticker),
            'Sector': info.get('sector', 'Unknown'),
            'Close': scores.get('close', 0.0),
            'Change%': scores.get('change_pct', 0.0),
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
            'Composite_Score': scores.get('composite_score', 0),
            'Signal': scores.get('signal', 'Neutral'),
            'Signal_Color': scores.get('signal_color', '#9CA3AF')
        }
    except Exception:
        return None

def test_fast_scan(tickers):
    results = []
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(process_single_ticker, t): t for t in tickers}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
    elapsed = time.time() - start
    print(f"Scanned {len(tickers)} stocks -> Got {len(results)} valid results in {elapsed:.2f} seconds!")
    return pd.DataFrame(results)

if __name__ == '__main__':
    tickers_200 = get_nifty200_tickers()
    print(f"Testing Fast Scan on {len(tickers_200)} F&O / NIFTY 200 stocks...")
    df = test_fast_scan(tickers_200)
