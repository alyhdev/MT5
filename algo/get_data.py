import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

def get_data(symbol, timeframe, start_date=None, end_date=None):
    """
    Get historical price data from MT5
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=100)
    if end_date is None:
        end_date = datetime.now()
        
    timeframe_map = {
        "D1": mt5.TIMEFRAME_D1,
        "H1": mt5.TIMEFRAME_H1,
        "M15": mt5.TIMEFRAME_M15
    }
    
    rates = mt5.copy_rates_range(symbol, timeframe_map[timeframe], start_date, end_date)
    df = pd.DataFrame(rates)
    
    # Ensure we have all required columns
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
    
    # Make sure we have a 'close' column
    if 'close' not in df.columns and 'close' in df.columns:
        df['close'] = df['close']
    
    # Required columns for the strategy
    required_columns = ['open', 'high', 'low', 'close', 'tick_volume']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in MT5 data")
    
    return df 