import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from chart_patterns import scan_all_chart_patterns
from pdf_generator import generate_pdf_report
from stock_universe import get_nifty50_tickers

tickers = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
df_pat = scan_all_chart_patterns(tickers, timeframe='Daily')
print(f"Scanned {len(df_pat)} patterns.")

pdf_bytes = generate_pdf_report(
    df_pat,
    title="Institutional Chart Patterns Detailed Report",
    subtitle="Full Field Inspection",
    mode="Daily",
    universe="NIFTY 50"
)
print(f"PDF generated successfully! Size: {len(pdf_bytes)} bytes")
with open("test_output.pdf", "wb") as f:
    f.write(pdf_bytes)
print("Saved to test_output.pdf successfully!")
