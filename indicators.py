"""
Technical Indicators Module

This module computes 6 technical indicators on OHLCV DataFrames using the `ta` library.
It provides individual functions for RSI, MACD, EMA, Stochastic Oscillator,
Bollinger Bands, and ADX, as well as a single function to compute all and enrich a DataFrame.
"""

import logging
import pandas as pd
import ta

# Configure logger
logger = logging.getLogger(__name__)

def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten MultiIndex columns if present, otherwise return as is.
    Assuming yfinance format where level 0 is price type (e.g., 'Close', 'Open').
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def _check_columns(df: pd.DataFrame, required_columns: list) -> None:
    """
    Check if required columns exist in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to check.
        required_columns (list): List of required column names.
        
    Raises:
        ValueError: If any of the required columns are missing.
    """
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

def compute_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Compute Relative Strength Index (RSI).

    Args:
        df (pd.DataFrame): OHLCV DataFrame.
        period (int): Period for RSI. Default is 14.

    Returns:
        pd.Series: RSI series.
    """
    try:
        df_flat = _flatten_columns(df.copy())
        _check_columns(df_flat, ['Close'])
        rsi = ta.momentum.RSIIndicator(close=df_flat['Close'], window=period)
        return rsi.rsi()
    except Exception as e:
        logger.error(f"Error computing RSI: {e}")
        raise

def compute_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """
    Compute Moving Average Convergence Divergence (MACD).

    Args:
        df (pd.DataFrame): OHLCV DataFrame.
        fast (int): Fast period. Default is 12.
        slow (int): Slow period. Default is 26.
        signal (int): Signal period. Default is 9.

    Returns:
        dict: Dictionary with keys 'macd', 'signal', 'histogram' (each pd.Series).
    """
    try:
        df_flat = _flatten_columns(df.copy())
        _check_columns(df_flat, ['Close'])
        macd_indicator = ta.trend.MACD(
            close=df_flat['Close'], window_slow=slow, window_fast=fast, window_sign=signal
        )
        return {
            'macd': macd_indicator.macd(),
            'signal': macd_indicator.macd_signal(),
            'histogram': macd_indicator.macd_diff()
        }
    except Exception as e:
        logger.error(f"Error computing MACD: {e}")
        raise

def compute_ema(df: pd.DataFrame, short: int = 5, mid: int = 13, long: int = 26) -> dict:
    """
    Compute Exponential Moving Averages (EMA) for 3 different periods.

    Args:
        df (pd.DataFrame): OHLCV DataFrame.
        short (int): Short period. Default is 5.
        mid (int): Mid period. Default is 13.
        long (int): Long period. Default is 26.

    Returns:
        dict: Dictionary with keys 'ema_short', 'ema_mid', 'ema_long' (each pd.Series).
    """
    try:
        df_flat = _flatten_columns(df.copy())
        _check_columns(df_flat, ['Close'])
        
        ema_short = ta.trend.EMAIndicator(close=df_flat['Close'], window=short)
        ema_mid = ta.trend.EMAIndicator(close=df_flat['Close'], window=mid)
        ema_long = ta.trend.EMAIndicator(close=df_flat['Close'], window=long)
        
        return {
            'ema_short': ema_short.ema_indicator(),
            'ema_mid': ema_mid.ema_indicator(),
            'ema_long': ema_long.ema_indicator()
        }
    except Exception as e:
        logger.error(f"Error computing EMA: {e}")
        raise

def compute_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3, smooth: int = 3) -> dict:
    """
    Compute Stochastic Oscillator.

    Args:
        df (pd.DataFrame): OHLCV DataFrame.
        k_period (int): Period for %K. Default is 14.
        d_period (int): Period for %D (smoothing). Default is 3.
        smooth (int): Unused parameter in standard `ta` signature, kept for interface match.

    Returns:
        dict: Dictionary with keys 'k', 'd' (each pd.Series).
    """
    try:
        df_flat = _flatten_columns(df.copy())
        _check_columns(df_flat, ['High', 'Low', 'Close'])
        
        stoch = ta.momentum.StochasticOscillator(
            high=df_flat['High'], low=df_flat['Low'], close=df_flat['Close'], 
            window=k_period, smooth_window=d_period
        )
        return {
            'k': stoch.stoch(),
            'd': stoch.stoch_signal()
        }
    except Exception as e:
        logger.error(f"Error computing Stochastic Oscillator: {e}")
        raise

def compute_bollinger(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> dict:
    """
    Compute Bollinger Bands.

    Args:
        df (pd.DataFrame): OHLCV DataFrame.
        period (int): Period for moving average. Default is 20.
        std_dev (int): Number of standard deviations. Default is 2.

    Returns:
        dict: Dictionary with keys 'upper', 'middle', 'lower', 'pct_b', 'width' (each pd.Series).
    """
    try:
        df_flat = _flatten_columns(df.copy())
        _check_columns(df_flat, ['Close'])
        
        bb = ta.volatility.BollingerBands(
            close=df_flat['Close'], window=period, window_dev=std_dev
        )
        
        return {
            'upper': bb.bollinger_hband(),
            'middle': bb.bollinger_mavg(),
            'lower': bb.bollinger_lband(),
            'pct_b': bb.bollinger_pband(),
            'width': bb.bollinger_wband()
        }
    except Exception as e:
        logger.error(f"Error computing Bollinger Bands: {e}")
        raise

def compute_adx(df: pd.DataFrame, period: int = 14) -> dict:
    """
    Compute Average Directional Index (ADX).

    Args:
        df (pd.DataFrame): OHLCV DataFrame.
        period (int): Period for ADX. Default is 14.

    Returns:
        dict: Dictionary with keys 'adx', 'plus_di', 'minus_di' (each pd.Series).
    """
    try:
        df_flat = _flatten_columns(df.copy())
        _check_columns(df_flat, ['High', 'Low', 'Close'])
        
        adx_ind = ta.trend.ADXIndicator(
            high=df_flat['High'], low=df_flat['Low'], close=df_flat['Close'], window=period
        )
        
        return {
            'adx': adx_ind.adx(),
            'plus_di': adx_ind.adx_pos(),
            'minus_di': adx_ind.adx_neg()
        }
    except Exception as e:
        logger.error(f"Error computing ADX: {e}")
        raise

def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Compute Average True Range (ATR).
    """
    try:
        df_flat = _flatten_columns(df.copy())
        _check_columns(df_flat, ['High', 'Low', 'Close'])
        atr_ind = ta.volatility.AverageTrueRange(
            high=df_flat['High'], low=df_flat['Low'], close=df_flat['Close'], window=period
        )
        return atr_ind.average_true_range()
    except Exception as e:
        logger.error(f"Error computing ATR: {e}")
        raise

def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all indicators and add them as columns to the DataFrame.
    
    Columns added: 
        RSI, MACD, MACD_Signal, MACD_Hist, EMA_5, EMA_13, EMA_26,
        Stoch_K, Stoch_D, BB_Upper, BB_Middle, BB_Lower, BB_PctB, BB_Width,
        ADX, Plus_DI, Minus_DI, ATR
    """
    result_df = df.copy()
    
    def _safe_run(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.debug(f"Indicator calculation warning ({func.__name__}): {e}")
            return None

    # 1. RSI
    rsi_res = _safe_run(compute_rsi, result_df)
    result_df['RSI'] = rsi_res if rsi_res is not None else pd.Series(index=result_df.index, dtype=float)
    
    # 2. MACD
    macd_data = _safe_run(compute_macd, result_df)
    if macd_data:
        result_df['MACD'] = macd_data['macd']
        result_df['MACD_Signal'] = macd_data['signal']
        result_df['MACD_Hist'] = macd_data['histogram']
    else:
        for col in ['MACD', 'MACD_Signal', 'MACD_Hist']:
            result_df[col] = pd.Series(index=result_df.index, dtype=float)
            
    # 3. EMA
    ema_data = _safe_run(compute_ema, result_df)
    if ema_data:
        result_df['EMA_5'] = ema_data['ema_short']
        result_df['EMA_13'] = ema_data['ema_mid']
        result_df['EMA_26'] = ema_data['ema_long']
    else:
        for col in ['EMA_5', 'EMA_13', 'EMA_26']:
            result_df[col] = pd.Series(index=result_df.index, dtype=float)
            
    # 4. Stochastic
    stoch_data = _safe_run(compute_stochastic, result_df)
    if stoch_data:
        result_df['Stoch_K'] = stoch_data['k']
        result_df['Stoch_D'] = stoch_data['d']
    else:
        for col in ['Stoch_K', 'Stoch_D']:
            result_df[col] = pd.Series(index=result_df.index, dtype=float)
            
    # 5. Bollinger Bands
    bb_data = _safe_run(compute_bollinger, result_df)
    if bb_data:
        result_df['BB_Upper'] = bb_data['upper']
        result_df['BB_Middle'] = bb_data['middle']
        result_df['BB_Lower'] = bb_data['lower']
        result_df['BB_PctB'] = bb_data['pct_b']
        result_df['BB_Width'] = bb_data['width']
    else:
        for col in ['BB_Upper', 'BB_Middle', 'BB_Lower', 'BB_PctB', 'BB_Width']:
            result_df[col] = pd.Series(index=result_df.index, dtype=float)
            
    # 6. ADX
    adx_data = _safe_run(compute_adx, result_df)
    if adx_data:
        result_df['ADX'] = adx_data['adx']
        result_df['Plus_DI'] = adx_data['plus_di']
        result_df['Minus_DI'] = adx_data['minus_di']
    else:
        for col in ['ADX', 'Plus_DI', 'Minus_DI']:
            result_df[col] = pd.Series(index=result_df.index, dtype=float)
            
    # 7. ATR
    atr_res = _safe_run(compute_atr, result_df)
    result_df['ATR'] = atr_res if atr_res is not None else pd.Series(index=result_df.index, dtype=float)
    
    return result_df

