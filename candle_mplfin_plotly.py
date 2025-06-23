import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Generate sample data (same function as above)
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
df = generate_sample_data(80)
# Create subplots with secondary y-axis
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.1,
    subplot_titles=('Stock Price', 'Volume'),
    row_width=[0.2, 0.7]
)
# Add candlestick chart
fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='OHLC',
        increasing_line_color='green',
        decreasing_line_color='red'
    ),
    row=1, col=1
)
# Add volume bar chart
fig.add_trace(
    go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        marker_color='lightblue',
        opacity=0.7
    ),
    row=2, col=1
)
# Update layout
fig.update_layout(
    title='Interactive Candlestick Chart with Volume',
    yaxis_title='Price ($)',
    xaxis_rangeslider_visible=False,
    height=800,
    showlegend=True
)
fig.update_yaxes(title_text="Price ($)", row=1, col=1)
fig.update_yaxes(title_text="Volume", row=2, col=1)
# Show the plot (comment out if causing issues)
# fig.show()

# Save as HTML file
fig.write_html("interactive_candlestick.html")
print("Chart saved to interactive_candlestick.html")

