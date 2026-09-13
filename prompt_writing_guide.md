# ⚡ Master Prompt Specification & Guide for FinTech & Stock Trading Engines

This document serves as a portable **Master Prompt & Engineering Specification** that you can copy and paste directly into any AI assistant or coding tool (such as **Claude**, **ChatGPT**, **Cursor**, **v0**, **Bolt.new**, or **Windsurf**) to build, maintain, or prompt complex stock analysis applications.

---

## 🎯 Master Prompt Template (Copy-Paste for Other AI Tools)

```markdown
You are an expert Quantitative Developer and Lead UI/UX Engineer specializing in Institutional FinTech Applications, Stock Market Analytics, and Multi-Timeframe Trading Engines.

### CORE OBJECTIVE
Build a high-performance, production-grade Stock Screening & Technical Analysis Dashboard tailored for the Indian Stock Market (NSE NIFTY 500 / F&O universe) with an ultra-sleek, Pure Liquid Glass Dark Mode UI.

### SYSTEM ARCHITECTURE & REQUIREMENTS

1. TECHNICAL INDICATOR ENGINE
   - RSI (14-period) with overbought/oversold momentum scoring
   - MACD (12, 26, 9) with histogram momentum rising/falling checks
   - EMA Triple Crossover (5, 13, 26) for trend alignment scoring
   - Stochastic Oscillator (14, 3, 3)
   - Bollinger Bands (20, 2) with %B breakout/breakdown detection
   - ADX (14) trend strength detector (ADX > 25 filter)

2. ADVANCED ANALYTICS MODULES
   - Multi-Timeframe Elliott Wave Engine (15-min, 1-hour, Daily, Weekly) detecting Impulse Waves (1-2-3-4-5) and Corrective Waves (A-B-C) with automated Fibonacci targets (0.382, 0.500, 0.618, 1.618).
   - Pre-Market Catalyst News Alert Radar scraping & aggregating news from Moneycontrol, CNBC-TV18, Economic Times, and NSE Announcements, assigning market impact intensity (+3 High Bullish, -3 High Bearish) and 1-day advance price reaction expectations.
   - Futures & Options (F&O) Analytics: PCR (Put-Call Ratio), Max Pain strike calculation, IV Rank (Implied Volatility percentile), and Option Chain heatmap.
   - Classical Chart Pattern Scanner identifying Double Bottoms/Tops, Head & Shoulders, Ascending/Descending Triangles, and Bullish/Bearish Flags.
   - Institutional Quant Scorecard assigning composite scores (-6 to +6) and classifying stocks into Strong Bull, Moderate Bull, Neutral, Moderate Bear, Strong Bear.

3. UI & DESIGN SYSTEM (PURE LIQUID GLASS THEME)
   - Theme: Deep Midnight Onyx (`#0B0F19`) background with translucent frosted glass containers (`backdrop-filter: blur(16px)`).
   - Accent Colors: Electric Neon Cyan (`#38BDF8`), Emerald Gain (`#10B981`), Crimson Loss (`#EF4444`), Amethyst Accent (`#A855F7`).
   - Typography: Clean sans-serif, high legibility, clean visual hierarchy, unbranded institutional header.
   - Micro-animations: Smooth hover glows, dynamic badges, border-glow highlights.

4. RESILIENCE & ZERO-CRASH ARCHITECTURE
   - Top-Level Imports: Always import `numpy as np`, `math`, `pandas as pd`, `yfinance as yf`.
   - Data Safeguards: All currency, percentage, and score formatting functions MUST gracefully handle `np.nan`, `None`, and empty/missing string placeholders (`'—'`, `'N/A'`) without raising `NameError`, `ValueError`, or `TypeError`.
   - Data Download Safety: yfinance data downloads must handle MultiIndex columns by flattening them automatically and catch rate-limit or missing ticker errors per symbol without crashing the scan pipeline.
```

---

## 🛠️ Section-by-Section Prompting Directives

### 1. Data Pipeline Prompt Directive
```markdown
Write a Python module `scanner.py` using `yfinance` to download OHLCV stock data for NSE tickers (e.g. `RELIANCE.NS`). Ensure multi-index column handling:
- If columns are MultiIndex, flatten them cleanly using `df.columns = df.columns.get_level_values(0)`.
- Wrap downloads in try-except blocks to catch delisted tickers or Yahoo Finance rate-limiting.
- Implement progress callbacks and exponential backoff retry loops.
```

### 2. Multi-Timeframe Elliott Wave Directive
```markdown
Implement an Elliott Wave analysis module `elliott_wave.py`:
- Identify local swing highs and lows using scipy signal peaks.
- Detect 5-wave impulse patterns: Wave 3 must not be the shortest; Wave 4 must not overlap Wave 1 price territory.
- Calculate key Fibonacci projection levels: Wave 3 target = Wave 1 * 1.618; Wave 5 target = Wave 1 * 0.618; Wave C target = Wave A * 1.000 / 1.618.
- Scan across 15m, 1h, Daily, and Weekly timeframes and compute confluence scores.
```

### 3. News Catalyst & Impact Radar Directive
```markdown
Create a pre-market news scraper and sentiment analyzer `market_news_catalyst.py`:
- Fetch RSS feeds and web articles from Moneycontrol, CNBC-TV18, Economic Times, and NSE India official announcements.
- Extract corporate action triggers: Orders won, merger & acquisitions, earnings beats/misses, regulatory updates.
- Calculate News Intensity (-3 to +3) and estimate next-day price reaction direction.
```

### 4. Pure Liquid Glass Styling Directive
```css
/* Copyable CSS Design System for Liquid Glass UI */
.stApp {
    background: radial-gradient(circle at 50% 0%, #1E293B 0%, #0F172A 50%, #0B0F19 100%) !important;
    color: #F8FAFC !important;
}

.glass-card {
    background: rgba(15, 23, 42, 0.65) !important;
    backdrop-filter: blur(16px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.glass-card:hover {
    border-color: rgba(56, 189, 248, 0.4) !important;
    box-shadow: 0 12px 40px 0 rgba(56, 189, 248, 0.15) !important;
    transform: translateY(-2px);
}
```

---

## 💡 Best Practices for Prompting AI Tools (Cursor, ChatGPT, Claude)

| Principle | Actionable Prompt Rule |
| :--- | :--- |
| **Defensive Math** | Instruct the AI: *"Always check `if val is None or np.isnan(val)` before performing string formatting or math operations."* |
| **Strict Return Contracts** | Instruct the AI: *"Utility formatters must return safe default strings like `'—'` on failure, never throw exceptions."* |
| **Multi-Timeframe Scans** | Instruct the AI: *"Separate data fetching into discrete granular timeframes (`15m`, `1h`, `1d`, `1wk`) with cache invalidation."* |
| **UI Aesthetics** | Instruct the AI: *"Never use plain red/green/blue. Use curated HSL dark mode palettes with frosted glass containers (`backdrop-filter`)."* |

---
*Created for use across all major AI development tools.*
