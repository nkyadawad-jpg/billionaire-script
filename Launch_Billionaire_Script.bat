@echo off
title BILLIONAIRE SCRIPT by Noeman NK
echo Starting BILLIONAIRE SCRIPT Server...
cd /d "C:\Users\Noman\.gemini\antigravity\scratch\stock_agent"
start http://localhost:8501
python -m streamlit run app.py --server.port 8501
pause
