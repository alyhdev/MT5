from algo import connect, get_data, mean_reversion_strategy
import MetaTrader5 as mt5
import time
from datetime import datetime
import pandas as pd
import os

def place_order(symbol, order_type, volume=0.01):
    if order_type == 1:  # Buy
        result = mt5.order_send({
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(symbol).ask,
            "deviation": 20,
            "magic": 100,
            "comment": "Mean Reversion Buy",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        })
        return result
    elif order_type == -1:  # Sell
        result = mt5.order_send({
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(symbol).bid,
            "deviation": 20,
            "magic": 100,
            "comment": "Mean Reversion Sell",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        })
        return result

def log_trade(symbol, signal_type, price, stop_loss, take_profit, timestamp):
    """Log trade details to separate CSV files for buy and sell signals"""
    trade_data = {
        'timestamp': [timestamp],
        'symbol': [symbol],
        'action': ['BUY' if signal_type == 1 else 'SELL'],
        'price': [price],
        'stop_loss': [stop_loss],
        'take_profit': [take_profit],
        'pips_to_sl': [abs(price - stop_loss) * 10000],
        'pips_to_tp': [abs(price - take_profit) * 10000]
    }
    
    df = pd.DataFrame(trade_data)
    
    # Determine which file to use based on signal type
    if signal_type == 1:
        filename = 'buy_signals.csv'
    elif signal_type == -1:
        filename = 'sell_signals.csv'
    else:
        raise ValueError(f"Invalid signal type: {signal_type}")
    
    # Create directory if it doesn't exist
    os.makedirs('signals', exist_ok=True)
    filepath = os.path.join('signals', filename)
    
    # Append to existing CSV or create new one
    try:
        if not os.path.exists(filepath):
            df.to_csv(filepath, mode='w', header=True, index=False)
        else:
            df.to_csv(filepath, mode='a', header=False, index=False)
        print(f"Trade logged to {filename}:")
        print(f"  Time: {timestamp}")
        print(f"  Action: {trade_data['action'][0]}")
        print(f"  Price: {price:.5f}")
        print(f"  Stop Loss: {stop_loss:.5f} ({trade_data['pips_to_sl'][0]:.1f} pips)")
        print(f"  Take Profit: {take_profit:.5f} ({trade_data['pips_to_tp'][0]:.1f} pips)")
    except Exception as e:
        print(f"Error logging trade to {filename}: {e}")

def initialize_signal_files():
    """Initialize signal files with headers if they don't exist"""
    columns = [
        'timestamp', 
        'symbol', 
        'action',
        'price', 
        'stop_loss', 
        'take_profit',
        'pips_to_sl',
        'pips_to_tp'
    ]
    
    os.makedirs('signals', exist_ok=True)
    
    for signal_type in ['buy', 'sell']:
        filepath = os.path.join('signals', f'{signal_type}_signals.csv')
        if not os.path.exists(filepath):
            pd.DataFrame(columns=columns).to_csv(filepath, index=False)
            print(f"Created {signal_type}_signals.csv")

if __name__ == "__main__":
    symbol = "EURUSD"
    volume = 0.01
    check_interval = 3600  # 1 hour in seconds
    
    if connect():
        print(f"Bot started at {datetime.now()}")
        
        # Initialize signal files
        initialize_signal_files()
        
        while True:
            try:
                data = get_data(symbol, "M15", None, None)
                signals = mean_reversion_strategy(data)
                
                last_signal = signals['signal'].iloc[-1]
                if last_signal != 0:
                    current_price = data['close'].iloc[-1]
                    stop_loss = signals['stop_loss'].iloc[-1]
                    take_profit = signals['take_profit'].iloc[-1]
                    
                    # Log the trade signal
                    log_trade(
                        symbol=symbol,
                        signal_type=last_signal,
                        price=current_price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        timestamp=datetime.now()
                    )
                    
                    # Place the order
                    result = place_order(symbol, last_signal, volume)
                    signal_type = 'BUY' if last_signal == 1 else 'SELL'
                    print(f"{signal_type} Signal detected at {datetime.now()}")
                    print(f"Price: {current_price:.5f}")
                    print(f"Stop Loss: {stop_loss:.5f}")
                    print(f"Take Profit: {take_profit:.5f}")
                    print(f"Order result: {result}")
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"Error occurred: {e}")
                time.sleep(check_interval)

