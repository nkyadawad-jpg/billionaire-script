# 📈 NSE Stock Trading Agent — Bull/Bear Scanner

A Python-based stock screening agent that scans **NIFTY 200** stocks on the NSE (National Stock Exchange of India) and identifies **strong bullish** and **strong bearish** setups for **daily** and **positional** trading.

## Features

- 🔍 **6 Technical Indicators**: RSI, MACD, EMA Crossover (5/13/26), Stochastic (14,3,3), Bollinger Bands, ADX
- 📊 **Scoring System**: Composite score from -6 to +6 classifying stocks as Strong Bull, Moderate Bull, Neutral, Moderate Bear, Strong Bear
- 🕐 **Two Modes**: Daily (short-term momentum) and Positional (medium-term trend)
- 🌐 **Streamlit Dashboard**: Interactive web UI with color-coded tables, summary cards, and Plotly charts
- 📡 **Live Data**: Real-time data from Yahoo Finance (no API key needed)

## Installation

### Prerequisites
- Python 3.9 or higher

### Setup

```bash
# Navigate to the project directory
cd stock_agent

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run the Dashboard

```bash
streamlit run app.py
```

This will open a web browser at `http://localhost:8501` with the stock screening dashboard.

### Dashboard Guide

1. **Select Mode**: Choose "Daily" for short-term trades or "Positional" for swing/positional trades
2. **Select Universe**: Choose "NIFTY 50" for a quick scan (~1 min) or "NIFTY 200" for a comprehensive scan (~5 min)
3. **Click "🚀 Run Scan"**: The scanner will fetch data and analyze all stocks
4. **View Results**: 
   - **Summary Cards** show the count of bullish and bearish stocks
   - **🐂 Bull Stocks** table lists strong and moderate bullish setups
   - **🐻 Bear Stocks** table lists strong and moderate bearish setups
5. **Stock Details**: Expand any stock row to see detailed indicator charts

## Technical Indicators

| Indicator | Parameters | Bullish Signal | Bearish Signal |
|-----------|------------|---------------|----------------|
| **RSI** | 14-period | > 60 | < 40 |
| **MACD** | 12, 26, 9 | MACD > Signal, histogram rising | MACD < Signal, histogram falling |
| **EMA Crossover** | 5/13/26 | EMA5 > EMA13 > EMA26 | EMA5 < EMA13 < EMA26 |
| **Stochastic** | 14, 3, 3 | %K > %D, %K > 50 | %K < %D, %K < 50 |
| **Bollinger Bands** | 20, 2 | %B > 0.8 (near upper band) | %B < 0.2 (near lower band) |
| **ADX** | 14-period | ADX > 25, +DI > -DI | ADX > 25, -DI > +DI |

## Scoring

Each indicator contributes +1 (bullish), 0 (neutral), or -1 (bearish). The composite score ranges from -6 to +6:

- **Strong Bull** (🟢): Score ≥ 5
- **Moderate Bull** (🟩): Score 3 to 4
- **Neutral** (⬜): Score -2 to 2
- **Moderate Bear** (🟧): Score -3 to -4
- **Strong Bear** (🔴): Score ≤ -5

## Disclaimer

⚠️ **This tool is for educational and informational purposes only.** It does not constitute financial advice. Always do your own research and consult a certified financial advisor before making trading decisions. Past performance of technical indicators does not guarantee future results.

## Data Source

Data is fetched from **Yahoo Finance** via the `yfinance` library. This is a free, unofficial API. For production use, consider a paid data provider for reliability.
