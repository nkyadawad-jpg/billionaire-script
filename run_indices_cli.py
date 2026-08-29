import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from index_elliott import scan_all_nse_indices

def main():
    print("Scanning all 6 Major NSE Indices for 1-Hour and 4-Hour Elliott Wave counts...")
    res = scan_all_nse_indices()
    
    print("\n" + "="*85)
    print("MAJOR NSE INDICES ELLIOTT WAVE INTELLIGENCE (1-HOUR & 4-HOUR)")
    print("="*85)
    for r in res:
        print(f"🏛️ {r['name']} ({r['symbol']}) — Price: Rs {r['current_price']:,.2f} ({r['change_pct']:+.2f}%)")
        print(f"   ⏱️ 1-Hour Wave: {r['ew_1h'].get('wave_phase')}")
        print(f"      {r['heading_1h']}")
        print(f"   ⏱️ 4-Hour Wave: {r['ew_4h'].get('wave_phase')}")
        print(f"      {r['heading_4h']}")
        print("-" * 80)

if __name__ == '__main__':
    main()
