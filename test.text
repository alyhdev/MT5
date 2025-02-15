import pandas as pd
import numpy as np

def calculate_rsi(data, period=14):
    """Calculate RSI indicator"""
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

def calculate_stochastic(data, k_period=14, d_period=3, smooth_k=3):
    """Calculate Stochastic Oscillator"""
    low_min = data['low'].rolling(window=k_period).min()
    high_max = data['high'].rolling(window=k_period).max()
    k = 100 * ((data['close'] - low_min) / (high_max - low_min + 1e-10))
    k = k.rolling(window=smooth_k).mean()
    d = k.rolling(window=d_period).mean()
    return k, d

def calculate_atr(data, period=14):
    """Calculate ATR for dynamic stop-loss"""
    high_low = data['high'] - data['low']
    high_close = abs(data['high'] - data['close'].shift())
    low_close = abs(data['low'] - data['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()

def calculate_ema(data, period=50):
    """Calculate Exponential Moving Average"""
    return data['close'].ewm(span=period, adjust=False).mean()

def mean_reversion_strategy(data, atr_mult=1.2, tp_mult=2.5):
    """Mean Reversion Strategy with Trend Filter and ATR-based Stops"""
    data = data.copy()
    
    # Indicators
    data['rsi'] = calculate_rsi(data)
    data['stoch_k'], data['stoch_d'] = calculate_stochastic(data)
    data['atr'] = calculate_atr(data)
    data['ema_50'] = calculate_ema(data)
    
    # Conditions
    uptrend = data['close'] > data['ema_50']
    downtrend = data['close'] < data['ema_50']
    
    buy_condition = (
        (data['rsi'] < 30) & (data['stoch_k'] < 20) &
        (data['stoch_k'] > data['stoch_d']) &
        uptrend  # Only buy in uptrend
    )
    
    sell_condition = (
        (data['rsi'] > 70) & (data['stoch_k'] > 80) &
        (data['stoch_k'] < data['stoch_d']) &
        downtrend  # Only sell in downtrend
    )
    
    signals = pd.Series(0, index=data.index)
    signals[buy_condition] = 1
    signals[sell_condition] = -1
    data['signal'] = signals
    
    # Stop-Loss & Take-Profit
    data['stop_loss'] = np.where(
        signals == 1, data['close'] - (atr_mult * data['atr']),
        np.where(signals == -1, data['close'] + (atr_mult * data['atr']), np.nan)
    )
    
    data['take_profit'] = np.where(
        signals == 1, data['close'] + (tp_mult * data['atr']),
        np.where(signals == -1, data['close'] - (tp_mult * data['atr']), np.nan)
    )
    
    return data[['signal', 'stop_loss', 'take_profit']]