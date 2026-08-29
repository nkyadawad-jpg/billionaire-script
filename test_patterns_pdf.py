import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from chart_patterns import scan_all_chart_patterns
from pdf_generator import generate_pdf_report
from stock_universe import get_nifty50_tickers

print("Testing Chart Pattern Scanner on NIFTY 50...")
tickers = get_nifty50_tickers()[:15]
df_patterns = scan_all_chart_patterns(tickers, timeframe='Daily')
print(f"Found {len(df_patterns)} chart pattern setups!")
if not df_patterns.empty:
    print(df_patterns[['Ticker', 'Name', 'Pattern', 'Direction', 'Status', 'Trigger_Entry', 'Stop_Loss', 'Target_1', 'RR_Ratio', 'Time_Cycle', 'Option_Strike']].head())

print("\nTesting PDF Report Generation...")
pdf_data = generate_pdf_report(df_patterns, title="Chart Patterns Institutional Report", subtitle="Test Scan")
print(f"PDF generated successfully! Size: {len(pdf_data)} bytes")
