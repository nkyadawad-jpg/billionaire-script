import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from elliott_wave import scan_all_elliott_wave_setups

def main():
    tickers = ['SUNPHARMA.NS', 'BAJFINANCE.NS', 'HINDUNILVR.NS', 'TCS.NS', 'DRREDDY.NS']
    df = scan_all_elliott_wave_setups(tickers)
    
    print("\n" + "="*95)
    print("🏛️ WALL STREET TRADER DESK — ELLIOTT WAVE INSTITUTIONAL DIRECTIVE")
    print("="*95)
    for _, r in df.iterrows():
        print(f"📌 {r['Ticker']} ({r['Name']}) — {r['Timeframe']}")
        print(f"   Wave Phase: {r['Wave_Stage']} | Conviction: {r['Conviction']}")
        print(f"   🎯 OPTION BUYING STRATEGY:")
        print(f"      • Action: {r['Option_Action']}")
        print(f"      • Recommended Expiry: {r['Option_Expiry']}")
        print(f"      • Target ROI: {r['Option_Target_ROI']}")
        print(f"      • Risk Parameters: {r['Option_SL']} | Option R:R: {r['Option_RR']}")
        print(f"   💎 CASH EQUITY STRATEGY:")
        print(f"      • Spot Entry: Rs {r['Entry_Price']:.2f} | Invalidation SL: Rs {r['Invalidation_SL']:.2f}")
        print(f"      • Target 1: Rs {r['Target_1']:.2f} | Target 2: Rs {r['Target_2']:.2f} | Cash R:R: {r['Cash_RR']}")
        print(f"   📖 THE ANATOMY (HOW IT HAPPENED):")
        print(f"{r['How_It_Happened']}")
        print("-" * 95)

if __name__ == '__main__':
    main()
