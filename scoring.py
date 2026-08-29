import pandas as pd

def score_indicator_rsi(df: pd.DataFrame) -> int:
    """
    Score the RSI indicator based on the latest value.
    
    - Bull (+1): RSI > 60
    - Neutral (0): 40 <= RSI <= 60  
    - Bear (-1): RSI < 40
    """
    rsi = df['RSI'].iloc[-1]
    if pd.isna(rsi):
        return 0
    if rsi > 60:
        return 1
    elif rsi < 40:
        return -1
    return 0

def score_indicator_macd(df: pd.DataFrame) -> int:
    """
    Score the MACD indicator based on the latest value.
    
    - Bull (+1): MACD > MACD_Signal AND MACD_Hist > 0 AND MACD_Hist > previous MACD_Hist (histogram rising)
    - Bear (-1): MACD < MACD_Signal AND MACD_Hist < 0 AND MACD_Hist < previous MACD_Hist (histogram falling)
    - Neutral (0): otherwise
    """
    if len(df) < 2:
        return 0
    
    macd = df['MACD'].iloc[-1]
    macd_signal = df['MACD_Signal'].iloc[-1]
    macd_hist = df['MACD_Hist'].iloc[-1]
    prev_macd_hist = df['MACD_Hist'].iloc[-2]
    
    if pd.isna(macd) or pd.isna(macd_signal) or pd.isna(macd_hist) or pd.isna(prev_macd_hist):
        return 0
        
    if macd > macd_signal and macd_hist > 0 and macd_hist > prev_macd_hist:
        return 1
    elif macd < macd_signal and macd_hist < 0 and macd_hist < prev_macd_hist:
        return -1
    return 0

def score_indicator_ema(df: pd.DataFrame) -> int:
    """
    Score the EMA Crossover indicator based on the latest value.
    
    - Bull (+1): EMA_5 > EMA_13 > EMA_26 (perfect bullish alignment)
    - Bear (-1): EMA_5 < EMA_13 < EMA_26 (perfect bearish alignment)
    - Neutral (0): mixed alignment
    """
    ema_5 = df['EMA_5'].iloc[-1]
    ema_13 = df['EMA_13'].iloc[-1]
    ema_26 = df['EMA_26'].iloc[-1]
    
    if pd.isna(ema_5) or pd.isna(ema_13) or pd.isna(ema_26):
        return 0
        
    if ema_5 > ema_13 and ema_13 > ema_26:
        return 1
    elif ema_5 < ema_13 and ema_13 < ema_26:
        return -1
    return 0

def score_indicator_stochastic(df: pd.DataFrame) -> int:
    """
    Score the Stochastic indicator based on the latest value.
    
    - Bull (+1): %K > %D AND %K > 50
    - Bear (-1): %K < %D AND %K < 50
    - Neutral (0): otherwise
    """
    stoch_k = df['Stoch_K'].iloc[-1]
    stoch_d = df['Stoch_D'].iloc[-1]
    
    if pd.isna(stoch_k) or pd.isna(stoch_d):
        return 0
        
    if stoch_k > stoch_d and stoch_k > 50:
        return 1
    elif stoch_k < stoch_d and stoch_k < 50:
        return -1
    return 0

def score_indicator_bollinger(df: pd.DataFrame) -> int:
    """
    Score the Bollinger Bands indicator based on the latest value.
    
    - Bull (+1): BB_PctB > 0.8 (price near/above upper band — breakout strength)
    - Bear (-1): BB_PctB < 0.2 (price near/below lower band — breakdown)
    - Neutral (0): 0.2 <= BB_PctB <= 0.8
    """
    bb_pctb = df['BB_PctB'].iloc[-1]
    
    if pd.isna(bb_pctb):
        return 0
        
    if bb_pctb > 0.8:
        return 1
    elif bb_pctb < 0.2:
        return -1
    return 0

def score_indicator_adx(df: pd.DataFrame) -> int:
    """
    Score the ADX indicator based on the latest value.
    
    - Bull (+1): ADX > 25 AND Plus_DI > Minus_DI (strong uptrend)
    - Bear (-1): ADX > 25 AND Minus_DI > Plus_DI (strong downtrend)
    - Neutral (0): ADX <= 25 (weak/no trend)
    """
    adx = df['ADX'].iloc[-1]
    plus_di = df['Plus_DI'].iloc[-1]
    minus_di = df['Minus_DI'].iloc[-1]
    
    if pd.isna(adx) or pd.isna(plus_di) or pd.isna(minus_di):
        return 0
        
    if adx > 25:
        if plus_di > minus_di:
            return 1
        elif minus_di > plus_di:
            return -1
    return 0

def get_signal_label(score: int) -> str:
    """
    Returns 'Strong Bull', 'Moderate Bull', 'Neutral', 'Moderate Bear', 'Strong Bear'
    based on the composite score.
    """
    if score >= 5:
        return 'Strong Bull'
    elif 3 <= score <= 4:
        return 'Moderate Bull'
    elif -2 <= score <= 2:
        return 'Neutral'
    elif -4 <= score <= -3:
        return 'Moderate Bear'
    else:
        return 'Strong Bear'

def get_signal_color(label: str) -> str:
    """
    Returns hex color for the signal label. Green shades for bull, red for bear, gray for neutral.
    """
    colors = {
        'Strong Bull': '#22C55E',      # Tailwind Green 500
        'Moderate Bull': '#86EFAC',    # Tailwind Green 300
        'Neutral': '#9CA3AF',          # Tailwind Gray 400
        'Moderate Bear': '#FCA5A5',    # Tailwind Red 300
        'Strong Bear': '#EF4444'       # Tailwind Red 500
    }
    return colors.get(label, '#9CA3AF')

def compute_trade_plan(df: pd.DataFrame, composite_score: int, mode: str = 'daily') -> dict:
    """
    Compute Trade Plan with Entry, Stop Loss, Targets, and Risk-Reward (RR) ratio.
    """
    last_row = df.iloc[-1]
    close = float(last_row.get('Close', 0.0))
    atr = float(last_row.get('ATR', close * 0.015))
    if pd.isna(atr) or atr <= 0:
        atr = close * 0.015

    # Reasons list
    reasons = []
    rsi = float(last_row.get('RSI', 50))
    macd_hist = float(last_row.get('MACD_Hist', 0))
    adx = float(last_row.get('ADX', 0))
    stoch_k = float(last_row.get('Stoch_K', 50))

    if composite_score >= 3:
        action = "BUY (LONG)"
        if rsi > 60: reasons.append(f"RSI Strong ({rsi:.1f})")
        if macd_hist > 0: reasons.append("MACD Bullish Histogram")
        if adx > 25: reasons.append(f"Strong Trend (ADX {adx:.1f})")
        if stoch_k > 50: reasons.append(f"Stochastic Bullish ({stoch_k:.1f})")
        
        if mode == 'daily':
            # Intraday Trade Setup
            sl_buffer = 1.0 * atr
            stop_loss = round(close - sl_buffer, 2)
            risk = max(round(close - stop_loss, 2), 0.05)
            target1 = round(close + (1.5 * risk), 2)
            target2 = round(close + (2.5 * risk), 2)
            rr_ratio = "1:2.0"
            est_sessions = max(1, int(round((target1 - close) / (atr * 0.85))))
            time_cycle = f"⚡ {est_sessions} - {est_sessions + 1} Sessions (Intraday/T+1)"
        else:
            # Positional Trade Setup
            sl_buffer = 2.0 * atr
            stop_loss = round(close - sl_buffer, 2)
            risk = max(round(close - stop_loss, 2), 0.05)
            target1 = round(close + (2.0 * risk), 2)
            target2 = round(close + (3.0 * risk), 2)
            rr_ratio = "1:2.5"
            est_days = max(4, int(round((target1 - close) / (atr * 0.45))))
            time_cycle = f"📅 {est_days} - {est_days + 5} Trading Days"

        return {
            'action': action,
            'entry': close,
            'stop_loss': stop_loss,
            'target_1': target1,
            'target_2': target2,
            'risk_per_share': risk,
            'reward_target_1': round(abs(target1 - close), 2),
            'reward_target_2': round(abs(target2 - close), 2),
            'rr_ratio': rr_ratio,
            'time_cycle': time_cycle,
            'rationale': " | ".join(reasons) if reasons else "Multiple Bullish Confirmations"
        }

    elif composite_score <= -3:
        action = "SELL (SHORT)"
        if rsi < 40: reasons.append(f"RSI Weak ({rsi:.1f})")
        if macd_hist < 0: reasons.append("MACD Bearish Histogram")
        if adx > 25: reasons.append(f"Strong Trend (ADX {adx:.1f})")
        if stoch_k < 50: reasons.append(f"Stochastic Bearish ({stoch_k:.1f})")
        
        if mode == 'daily':
            # Intraday Short Setup
            sl_buffer = 1.0 * atr
            stop_loss = round(close + sl_buffer, 2)
            risk = max(round(stop_loss - close, 2), 0.05)
            target1 = round(close - (1.5 * risk), 2)
            target2 = round(close - (2.5 * risk), 2)
            rr_ratio = "1:2.0"
            est_sessions = max(1, int(round((close - target1) / (atr * 0.85))))
            time_cycle = f"⚡ {est_sessions} - {est_sessions + 1} Sessions (Intraday/T+1)"
        else:
            # Positional Short Setup
            sl_buffer = 2.0 * atr
            stop_loss = round(close + sl_buffer, 2)
            risk = max(round(stop_loss - close, 2), 0.05)
            target1 = round(close - (2.0 * risk), 2)
            target2 = round(close - (3.0 * risk), 2)
            rr_ratio = "1:2.5"
            est_days = max(4, int(round((close - target1) / (atr * 0.45))))
            time_cycle = f"📅 {est_days} - {est_days + 5} Trading Days"

        return {
            'action': action,
            'entry': close,
            'stop_loss': stop_loss,
            'target_1': target1,
            'target_2': target2,
            'risk_per_share': risk,
            'reward_target_1': round(abs(close - target1), 2),
            'reward_target_2': round(abs(close - target2), 2),
            'rr_ratio': rr_ratio,
            'time_cycle': time_cycle,
            'rationale': " | ".join(reasons) if reasons else "Multiple Bearish Confirmations"
        }
    else:
        return {
            'action': "NO TRADE (NEUTRAL)",
            'entry': close,
            'stop_loss': 0.0,
            'target_1': 0.0,
            'target_2': 0.0,
            'risk_per_share': 0.0,
            'reward_target_1': 0.0,
            'reward_target_2': 0.0,
            'rr_ratio': "N/A",
            'time_cycle': "N/A",
            'rationale': "Signals are mixed/neutral"
        }

def score_stock(df: pd.DataFrame, mode: str = 'daily') -> dict:
    """
    Score a single stock based on technical indicators and generate Trade Plan.
    """
    if df.empty:
        raise ValueError("DataFrame cannot be empty.")
        
    rsi_score = score_indicator_rsi(df)
    macd_score = score_indicator_macd(df)
    ema_score = score_indicator_ema(df)
    stoch_score = score_indicator_stochastic(df)
    bb_score = score_indicator_bollinger(df)
    adx_score = score_indicator_adx(df)
    
    # If mode is positional, ensure the EMA trend has been consistent for at least 3 days.
    if mode == 'positional' and len(df) >= 3:
        ema_last_3_scores = [score_indicator_ema(df.iloc[:i+1]) for i in range(len(df)-3, len(df))]
        if len(set(ema_last_3_scores)) != 1:
            ema_score = 0
            
    composite_score = rsi_score + macd_score + ema_score + stoch_score + bb_score + adx_score
    signal_label = get_signal_label(composite_score)
    signal_color = get_signal_color(signal_label)
    
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2] if len(df) > 1 else last_row
    
    close = float(last_row.get('Close', 0.0))
    prev_close = float(prev_row.get('Close', close))
    
    # Safely compute percentage change
    change_pct = ((close - prev_close) / prev_close * 100) if prev_close and prev_close != 0 else 0.0
    
    trade_plan = compute_trade_plan(df, composite_score, mode=mode)
    
    return {
        'rsi_score': rsi_score,
        'macd_score': macd_score,
        'ema_score': ema_score,
        'stoch_score': stoch_score,
        'bb_score': bb_score,
        'adx_score': adx_score,
        'composite_score': composite_score,
        'signal': signal_label,
        'signal_color': signal_color,
        'rsi_value': float(last_row.get('RSI', 0.0)) if 'RSI' in df.columns else 0.0,
        'macd_value': float(last_row.get('MACD', 0.0)) if 'MACD' in df.columns else 0.0,
        'stoch_k_value': float(last_row.get('Stoch_K', 0.0)) if 'Stoch_K' in df.columns else 0.0,
        'adx_value': float(last_row.get('ADX', 0.0)) if 'ADX' in df.columns else 0.0,
        'bb_pctb_value': float(last_row.get('BB_PctB', 0.0)) if 'BB_PctB' in df.columns else 0.0,
        'atr_value': float(last_row.get('ATR', 0.0)) if 'ATR' in df.columns else 0.0,
        'close': close,
        'change_pct': change_pct,
        'volume': float(last_row.get('Volume', 0.0)) if 'Volume' in df.columns else 0.0,
        'action': trade_plan['action'],
        'entry': trade_plan['entry'],
        'stop_loss': trade_plan['stop_loss'],
        'target_1': trade_plan['target_1'],
        'target_2': trade_plan['target_2'],
        'risk_per_share': trade_plan['risk_per_share'],
        'reward_target_1': trade_plan['reward_target_1'],
        'reward_target_2': trade_plan['reward_target_2'],
        'rr_ratio': trade_plan['rr_ratio'],
        'time_cycle': trade_plan['time_cycle'],
        'rationale': trade_plan['rationale']
    }
