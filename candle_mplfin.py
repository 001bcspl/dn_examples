import pandas as pd
import numpy as np
import mplfinance as mpf
from datetime import datetime, timedelta

# Generate sample stock data
def generate_sample_data(days=100):
    dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
    
    # Generate realistic OHLC data
    np.random.seed(42)
    close_prices = []
    open_prices = []
    high_prices = []
    low_prices = []
    volumes = []
    
    initial_price = 100
    price = initial_price
    
    for i in range(days):
        # Random walk for price movement
        daily_return = np.random.normal(0.001, 0.02)
        
        open_price = price
        close_price = open_price * (1 + daily_return)
        
        # High and low based on intraday volatility
        intraday_range = abs(np.random.normal(0, 0.015))
        high_price = max(open_price, close_price) * (1 + intraday_range)
        low_price = min(open_price, close_price) * (1 - intraday_range)
        
        volume = np.random.randint(1000000, 5000000)
        
        open_prices.append(open_price)
        high_prices.append(high_price)
        low_prices.append(low_price)
        close_prices.append(close_price)
        volumes.append(volume)
        
        price = close_price
    
    df = pd.DataFrame({
        'Open': open_prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': close_prices,
        'Volume': volumes
    }, index=dates)
    
    return df

# Generate data
df = generate_sample_data(60)

# Basic candlestick plot
mpf.plot(df, type='candle', style='charles', 
         title='Basic Candlestick Chart',
         ylabel='Price ($)',
         volume=True,
         figsize=(12, 8))
