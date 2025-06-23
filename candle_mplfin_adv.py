import pandas as pd
import numpy as np
import mplfinance as mpf

# Using the same data generation function from above
def generate_sample_data(days=100):
    dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
    
    np.random.seed(42)
    close_prices = []
    open_prices = []
    high_prices = []
    low_prices = []
    volumes = []
    
    initial_price = 100
    price = initial_price
    
    for i in range(days):
        daily_return = np.random.normal(0.001, 0.02)
        
        open_price = price
        close_price = open_price * (1 + daily_return)
        
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
df = generate_sample_data(100)

# Calculate moving averages
df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA50'] = df['Close'].rolling(window=50).mean()

# Create additional plots for moving averages
apds = [
    mpf.make_addplot(df['MA20'], color='blue', width=1.5),
    mpf.make_addplot(df['MA50'], color='red', width=1.5)
]

# Advanced candlestick plot with moving averages
mpf.plot(df, type='candle', 
         addplot=apds,
         style='yahoo',
         title='Candlestick Chart with Moving Averages',
         ylabel='Price ($)',
         volume=True,
         figsize=(14, 10),
         savefig='candlestick_chart.png')
