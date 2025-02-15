from datetime import datetime, timedelta
from algo.backtest import Backtest
from algo.mt_connect import connect
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for better visualization
plt.style.use('seaborn-v0_8-darkgrid')  # Using a valid style name
sns.set_theme()  # Use seaborn's default theme

def plot_backtest_results(trades_df, results):
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[2, 1])
    
    # Calculate cumulative balance
    trades_df['cumulative_pnl'] = trades_df['pnl'].cumsum() + results['Initial Balance']
    
    # Plot balance curve
    ax1.plot(trades_df.index, trades_df['cumulative_pnl'], label='Account Balance', linewidth=2)
    ax1.set_title('Backtest Results - Triple RSI Strategy (EURUSD)')
    ax1.set_ylabel('Account Balance ($)')
    ax1.legend()
    ax1.grid(True)
    
    # Plot individual trades
    positive_trades = trades_df[trades_df['pnl'] > 0]
    negative_trades = trades_df[trades_df['pnl'] < 0]
    
    # Plot trade profits/losses
    ax2.bar(positive_trades.index, positive_trades['pnl'], color='green', alpha=0.6, label='Winning Trades')
    ax2.bar(negative_trades.index, negative_trades['pnl'], color='red', alpha=0.6, label='Losing Trades')
    ax2.set_ylabel('Trade P/L ($)')
    ax2.legend()
    ax2.grid(True)
    
    # Add key statistics as text
    stats_text = (
        f"Total Return: {results['Total Return %']:.2f}%\n"
        f"Win Rate: {results['Win Rate %']:.2f}%\n"
        f"Total Trades: {results['Number of Trades']}\n"
        f"Avg Profit: ${results['Average Profit']:.2f}\n"
        f"Avg Loss: ${results['Average Loss']:.2f}"
    )
    plt.figtext(0.02, 0.02, stats_text, fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save plot
    plt.savefig('backtest_results.png')
    print("Results chart saved as 'backtest_results.png'")
    
    # Save detailed trade data to CSV
    trades_df.to_csv('trade_history.csv')
    print("Detailed trade history saved as 'trade_history.csv'")

# First connect to MT5
if connect():
    print("Connected to MT5 successfully")
    
    # Test last 90 days
    start_date = datetime.now() - timedelta(days=90)
    end_date = datetime.now()

    backtest = Backtest("EURUSD", "M15", start_date, end_date, initial_balance=200, lot_size=0.01)
    backtest.run()
    results, trades = backtest.get_results()

    print("\nBacktest Results:")
    for key, value in results.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")

    # Plot results
    plot_backtest_results(trades, results)
    
    print("\nFirst 5 trades:")
    print(trades.head())
else:
    print("Failed to connect to MT5. Please check your credentials and MT5 terminal.") 