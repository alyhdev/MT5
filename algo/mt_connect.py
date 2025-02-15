import MetaTrader5 as mt5

# Define login credentials
ACCOUNT =   # Replace with your MT5 account number
PASSWORD = ""
SERVER = "MetaQuotes-Demo"  # Example: "ICMarkets-Demo"

def connect():
    if not mt5.initialize():
        print("MT5 Initialization failed")
        return False
    
    authorized = mt5.login(ACCOUNT, password=PASSWORD, server=SERVER)
    if not authorized:
        print("Login failed:", mt5.last_error())
        return False
    5
    print("Connected to MT5")
    return True

if __name__ == "__main__":
    connect()
