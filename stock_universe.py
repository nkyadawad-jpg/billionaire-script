"""
Stock Universe module.

Provides NIFTY 500, NIFTY 200 (Full F&O Basket), and NIFTY 50 stock ticker lists for NSE India.
Uses the `niftystocks` library as the primary source with ticker normalizers and hardcoded fallbacks.
"""

import logging
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger(__name__)

# Attempt to import niftystocks
try:
    from niftystocks import ns
    NIFTYSTOCKS_AVAILABLE = True
except ImportError:
    logger.warning("niftystocks library not found. Falling back to hardcoded data.")
    NIFTYSTOCKS_AVAILABLE = False
except Exception as e:
    logger.warning(f"Error importing niftystocks: {e}. Falling back to hardcoded data.")
    NIFTYSTOCKS_AVAILABLE = False

# Mapping for renamed/merged NSE tickers
TICKER_NORMALIZER = {
    'MOTHERSUMI.NS': 'MOTHERSON.NS',
    'LTI.NS': 'LTIM.NS',
    'MINDTREE.NS': 'LTIM.NS',
    'CADILAHC.NS': 'ZYDUSLIFE.NS',
    'ADANITRANS.NS': 'ADANIENSOL.NS',
    'MCDOWELL-N.NS': 'UNITDSPR.NS',
    'GMRINFRA.NS': 'GMRAIRPORT.NS',
    'L&TFH.NS': 'LTF.NS',
    'AMARAJABAT.NS': 'AMARAJA.NS',
    'SRTRANSFIN.NS': 'SHRIRAMFIN.NS',
    'IBULHSGFIN.NS': 'SAMMAANCAP.NS'
}

# Hardcoded Fallback NIFTY 50 Dictionary
NIFTY_50_FALLBACK: Dict[str, Dict[str, str]] = {
    "RELIANCE.NS": {"name": "Reliance Industries Ltd.", "sector": "Energy"},
    "TCS.NS": {"name": "Tata Consultancy Services Ltd.", "sector": "Information Technology"},
    "HDFCBANK.NS": {"name": "HDFC Bank Ltd.", "sector": "Financial Services"},
    "INFY.NS": {"name": "Infosys Ltd.", "sector": "Information Technology"},
    "ICICIBANK.NS": {"name": "ICICI Bank Ltd.", "sector": "Financial Services"},
    "HINDUNILVR.NS": {"name": "Hindustan Unilever Ltd.", "sector": "Consumer Staples"},
    "ITC.NS": {"name": "ITC Ltd.", "sector": "Consumer Staples"},
    "SBIN.NS": {"name": "State Bank of India", "sector": "Financial Services"},
    "BHARTIARTL.NS": {"name": "Bharti Airtel Ltd.", "sector": "Telecommunication"},
    "KOTAKBANK.NS": {"name": "Kotak Mahindra Bank Ltd.", "sector": "Financial Services"},
    "LT.NS": {"name": "Larsen & Toubro Ltd.", "sector": "Industrials"},
    "AXISBANK.NS": {"name": "Axis Bank Ltd.", "sector": "Financial Services"},
    "ASIANPAINT.NS": {"name": "Asian Paints Ltd.", "sector": "Materials"},
    "MARUTI.NS": {"name": "Maruti Suzuki India Ltd.", "sector": "Consumer Discretionary"},
    "HCLTECH.NS": {"name": "HCL Technologies Ltd.", "sector": "Information Technology"},
    "SUNPHARMA.NS": {"name": "Sun Pharmaceutical Industries Ltd.", "sector": "Healthcare"},
    "TITAN.NS": {"name": "Titan Company Ltd.", "sector": "Consumer Discretionary"},
    "BAJFINANCE.NS": {"name": "Bajaj Finance Ltd.", "sector": "Financial Services"},
    "WIPRO.NS": {"name": "Wipro Ltd.", "sector": "Information Technology"},
    "ULTRACEMCO.NS": {"name": "UltraTech Cement Ltd.", "sector": "Materials"},
    "NESTLEIND.NS": {"name": "Nestle India Ltd.", "sector": "Consumer Staples"},
    "NTPC.NS": {"name": "NTPC Ltd.", "sector": "Energy"},
    "POWERGRID.NS": {"name": "Power Grid Corporation of India Ltd.", "sector": "Energy"},
    "TATAMOTORS.NS": {"name": "Tata Motors Ltd.", "sector": "Consumer Discretionary"},
    "JSWSTEEL.NS": {"name": "JSW Steel Ltd.", "sector": "Materials"},
    "TATASTEEL.NS": {"name": "Tata Steel Ltd.", "sector": "Materials"},
    "ADANIENT.NS": {"name": "Adani Enterprises Ltd.", "sector": "Industrials"},
    "ADANIPORTS.NS": {"name": "Adani Ports and Special Economic Zone Ltd.", "sector": "Industrials"},
    "M&M.NS": {"name": "Mahindra & Mahindra Ltd.", "sector": "Consumer Discretionary"},
    "TECHM.NS": {"name": "Tech Mahindra Ltd.", "sector": "Information Technology"},
    "INDUSINDBK.NS": {"name": "IndusInd Bank Ltd.", "sector": "Financial Services"},
    "HINDALCO.NS": {"name": "Hindalco Industries Ltd.", "sector": "Materials"},
    "GRASIM.NS": {"name": "Grasim Industries Ltd.", "sector": "Materials"},
    "DIVISLAB.NS": {"name": "Divi's Laboratories Ltd.", "sector": "Healthcare"},
    "DRREDDY.NS": {"name": "Dr. Reddy's Laboratories Ltd.", "sector": "Healthcare"},
    "CIPLA.NS": {"name": "Cipla Ltd.", "sector": "Healthcare"},
    "APOLLOHOSP.NS": {"name": "Apollo Hospitals Enterprise Ltd.", "sector": "Healthcare"},
    "EICHERMOT.NS": {"name": "Eicher Motors Ltd.", "sector": "Consumer Discretionary"},
    "BAJAJFINSV.NS": {"name": "Bajaj Finserv Ltd.", "sector": "Financial Services"},
    "BAJAJ-AUTO.NS": {"name": "Bajaj Auto Ltd.", "sector": "Consumer Discretionary"},
    "HEROMOTOCO.NS": {"name": "Hero MotoCorp Ltd.", "sector": "Consumer Discretionary"},
    "ONGC.NS": {"name": "Oil & Natural Gas Corporation Ltd.", "sector": "Energy"},
    "COALINDIA.NS": {"name": "Coal India Ltd.", "sector": "Energy"},
    "BPCL.NS": {"name": "Bharat Petroleum Corporation Ltd.", "sector": "Energy"},
    "TATACONSUM.NS": {"name": "Tata Consumer Products Ltd.", "sector": "Consumer Staples"},
    "BRITANNIA.NS": {"name": "Britannia Industries Ltd.", "sector": "Consumer Staples"},
    "SBILIFE.NS": {"name": "SBI Life Insurance Company Ltd.", "sector": "Financial Services"},
    "HDFCLIFE.NS": {"name": "HDFC Life Insurance Company Ltd.", "sector": "Financial Services"},
    "SHRIRAMFIN.NS": {"name": "Shriram Finance Ltd.", "sector": "Financial Services"},
    "LTIM.NS": {"name": "LTIMindtree Ltd.", "sector": "Information Technology"}
}

def clean_ticker_list(raw_tickers: List[str]) -> List[str]:
    """Normalize and deduplicate tickers."""
    cleaned = []
    seen = set()
    for t in raw_tickers:
        t_clean = TICKER_NORMALIZER.get(t, t)
        if t_clean not in seen and t_clean != 'HDFC.NS' and t_clean != 'DHANI.NS' and t_clean != 'PEL.NS':
            seen.add(t_clean)
            cleaned.append(t_clean)
    return cleaned

def get_nifty50_tickers() -> List[str]:
    """Returns all 50 NIFTY 50 stock tickers."""
    if NIFTYSTOCKS_AVAILABLE:
        try:
            return clean_ticker_list(list(ns.get_nifty50_with_ns()))
        except Exception as e:
            logger.error(f"Error fetching NIFTY 50 from niftystocks: {e}. Using fallback.")
            
    return list(NIFTY_50_FALLBACK.keys())

def get_nifty200_tickers() -> List[str]:
    """Returns all 200 NIFTY 200 / F&O stock tickers."""
    if NIFTYSTOCKS_AVAILABLE:
        try:
            raw = list(ns.get_nifty200_with_ns())
            return clean_ticker_list(raw)
        except Exception as e:
            logger.error(f"Error fetching NIFTY 200 from niftystocks: {e}. Falling back to NIFTY 50.")
            
    return list(NIFTY_50_FALLBACK.keys())

def get_nifty500_tickers() -> List[str]:
    """Returns all 500 NIFTY 500 stock tickers."""
    if NIFTYSTOCKS_AVAILABLE:
        try:
            raw = list(ns.get_nifty500_with_ns())
            return clean_ticker_list(raw)
        except Exception as e:
            logger.error(f"Error fetching NIFTY 500 from niftystocks: {e}. Falling back to NIFTY 200.")
            
    return get_nifty200_tickers()

def get_fno_tickers() -> List[str]:
    """Returns all 200 F&O stock tickers on NSE."""
    return get_nifty200_tickers()

def get_stock_info(ticker: str) -> Dict[str, str]:
    """Returns name and sector for a ticker."""
    clean_sym = ticker.replace('.NS', '')
    return NIFTY_50_FALLBACK.get(ticker, {"name": clean_sym, "sector": "NSE Equities / F&O"})

def get_available_universes() -> Dict[str, str]:
    """Returns available stock universes."""
    return {
        '📊 Full 200 F&O Universe': 'fno',
        '🌐 Full 500 Broad Market Universe': 'nifty500',
        'NIFTY 200': 'nifty200',
        'NIFTY 500': 'nifty500'
    }
