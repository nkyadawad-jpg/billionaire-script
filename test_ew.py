import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from elliott_wave import analyze_multi_timeframe_elliott

tickers = ['RELIANCE.NS', 'TITAN.NS', 'DIVISLAB.NS', 'SBILIFE.NS', 'BAJAJ-AUTO.NS', 'HINDUNILVR.NS', 'ONGC.NS', 'TCS.NS']

for ticker in tickers:
    res = analyze_multi_timeframe_elliott(ticker)
    if res['valid']:
        d = res['daily']
        w = res['weekly']
        print('='*75)
        print(f"STOCK: {ticker}")
        print(f"  DAILY  -> Phase: {d.get('wave_phase')}")
        print(f"            Setup: {d.get('setup_type')} | Early Confirmed: {d.get('early_confirmation')}")
        if d.get('setup_type') != 'NEUTRAL':
            print(f"            Action: {d.get('direction')}")
            print(f"            Entry: Rs {d.get('current_price')} | Invalidation (SL): Rs {d.get('invalidation_price')}")
            print(f"            Target 1: Rs {d.get('target_1')} | Target 2: Rs {d.get('target_2')} | R:R: {d.get('rr_ratio')}")
            print(f"            Fib Retrace: {d.get('fib_retracement')}%")
            print(f"            Rationale: {d.get('rationale')}")
        print(f"  WEEKLY -> Phase: {w.get('wave_phase')} | Setup: {w.get('setup_type')}")
