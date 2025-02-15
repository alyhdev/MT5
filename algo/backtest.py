import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .get_data import get_data
from .strategy import mean_reversion_strategy

class Backtest:
    def __init__(self, symbol, timeframe, start_date, end_date, initial_balance=10000, lot_size=0.01):
        self.symbol = symbol
        self.timeframe = timeframe
        self.start_date = start_date
        self.end_date = end_date
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.lot_size = lot_size
        self.positions = []
        self.trades = []
        
    def run(self):
        # Get historical data
        data = get_data(self.symbol, self.timeframe, self.start_date, self.end_date)
        
        # Get signals from mean reversion strategy
        strategy_data = mean_reversion_strategy(data)
        signals = strategy_data['signal']  # Extract just the signal column
        
        # Simulate trading
        position = 0  # 0: no position, 1: long, -1: short
        
        for i in range(1, len(data)):
            current_price = data['close'].iloc[i]
            current_signal = signals.iloc[i]
            
            # Close existing position if opposite signal
            if position != 0 and current_signal != 0 and position != current_signal:
                trade_pnl = self._calculate_pnl(position, 
                                              entry_price=self.positions[-1]['entry_price'],
                                              exit_price=current_price)
                self.balance += trade_pnl
                
                self.trades.append({
                    'entry_time': self.positions[-1]['entry_time'],
                    'exit_time': data.index[i],
                    'position': position,
                    'entry_price': self.positions[-1]['entry_price'],
                    'exit_price': current_price,
                    'pnl': trade_pnl,
                    'stop_loss': strategy_data['stop_loss'].iloc[i],
                    'take_profit': strategy_data['take_profit'].iloc[i]
                })
                position = 0
            
            # Open new position
            if position == 0 and current_signal != 0:
                position = current_signal
                self.positions.append({
                    'entry_time': data.index[i],
                    'entry_price': current_price,
                    'stop_loss': strategy_data['stop_loss'].iloc[i],
                    'take_profit': strategy_data['take_profit'].iloc[i]
                })
        
        # Close any remaining position
        if position != 0:
            trade_pnl = self._calculate_pnl(position, 
                                          entry_price=self.positions[-1]['entry_price'],
                                          exit_price=data['close'].iloc[-1])
            self.balance += trade_pnl
            
            self.trades.append({
                'entry_time': self.positions[-1]['entry_time'],
                'exit_time': data.index[-1],
                'position': position,
                'entry_price': self.positions[-1]['entry_price'],
                'exit_price': data['close'].iloc[-1],
                'pnl': trade_pnl,
                'stop_loss': self.positions[-1]['stop_loss'],
                'take_profit': self.positions[-1]['take_profit']
            })
    
    def _calculate_pnl(self, position, entry_price, exit_price):
        pip_value = 0.0001  # For EURUSD
        pips = (exit_price - entry_price) / pip_value
        return pips * position * self.lot_size * 10  # Approximate USD per pip for 0.01 lot
    
    def get_results(self):
        if not self.trades:  # If no trades were made
            trades_df = pd.DataFrame(columns=[
                'entry_time', 'exit_time', 'position', 'entry_price', 
                'exit_price', 'pnl', 'stop_loss', 'take_profit'
            ])
            results = {
                'Initial Balance': self.initial_balance,
                'Final Balance': self.balance,
                'Total Return %': 0,
                'Number of Trades': 0,
                'Winning Trades': 0,
                'Losing Trades': 0,
                'Win Rate %': 0,
                'Average Profit': 0,
                'Average Loss': 0,
            }
            return results, trades_df
        
        trades_df = pd.DataFrame(self.trades)
        
        # Ensure all required columns exist
        if trades_df.empty:
            return self.get_results()  # Return empty results if no trades
        
        results = {
            'Initial Balance': self.initial_balance,
            'Final Balance': self.balance,
            'Total Return %': ((self.balance - self.initial_balance) / self.initial_balance) * 100,
            'Number of Trades': len(self.trades),
            'Winning Trades': len(trades_df[trades_df['pnl'] > 0]) if 'pnl' in trades_df.columns else 0,
            'Losing Trades': len(trades_df[trades_df['pnl'] < 0]) if 'pnl' in trades_df.columns else 0,
            'Win Rate %': (len(trades_df[trades_df['pnl'] > 0]) / len(trades_df) * 100) if not trades_df.empty and 'pnl' in trades_df.columns else 0,
            'Average Profit': trades_df[trades_df['pnl'] > 0]['pnl'].mean() if not trades_df.empty and 'pnl' in trades_df.columns else 0,
            'Average Loss': trades_df[trades_df['pnl'] < 0]['pnl'].mean() if not trades_df.empty and 'pnl' in trades_df.columns else 0,
        }
        
        return results, trades_df

if __name__ == "__main__":
    # Example usage
    start_date = datetime.now() - timedelta(days=90)
    end_date = datetime.now()
    
    backtest = Backtest("EURUSD", "M15", start_date, end_date, lot_size=0.01)
    backtest.run()
    results, trades = backtest.get_results()
    
    print("\nBacktest Results:")
    for key, value in results.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    print("\nFirst 5 trades:")
    print(trades.head()) 