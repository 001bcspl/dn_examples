import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

def create_trading_dashboard(symbol='AAPL', period='6mo'):
    """
    Create a complete trading dashboard with real data
    """
    try:
        # Download real data
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if df.empty:
            print(f"No data found for symbol {symbol}")
            return None, None
            
        # Calculate technical indicators
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        df['BB_Std'] = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
        df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(
                f'{symbol} - Price Chart',
                'Volume',
                'RSI',
                'MACD'
            ),
            row_heights=[0.5, 0.15, 0.175, 0.175]
        )
        
        # Add candlestick (without hovertemplate)
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350',
                increasing_fillcolor='rgba(38, 166, 154, 0.8)',
                decreasing_fillcolor='rgba(239, 83, 80, 0.8)'
            ),
            row=1, col=1
        )
        
        # Add moving averages
        colors_ma = {'MA20': 'blue', 'MA50': 'red', 'MA200': 'purple'}
        for ma, color in colors_ma.items():
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[ma],
                    mode='lines',
                    name=ma,
                    line=dict(color=color, width=2),
                    opacity=0.8
                ),
                row=1, col=1
            )
        
        # Add Bollinger Bands
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color='purple', width=1, dash='dash'),
                opacity=0.5
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color='purple', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128, 0, 128, 0.1)',
                opacity=0.5
            ),
            row=1, col=1
        )
        
        # Add volume
        colors = ['#ef5350' if close < open else '#26a69a' 
                 for close, open in zip(df['Close'], df['Open'])]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Add RSI
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='orange', width=2)
            ),
            row=3, col=1
        )
        
        # Add RSI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=3, col=1)
        
        # Add MACD
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=2)
            ),
            row=4, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MACD_Signal'],
                mode='lines',
                name='MACD Signal',
                line=dict(color='red', width=2)
            ),
            row=4, col=1
        )
        
        # MACD Histogram
        colors_macd = ['#26a69a' if val >= 0 else '#ef5350' for val in df['MACD_Histogram']]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['MACD_Histogram'],
                name='MACD Histogram',
                marker_color=colors_macd,
                opacity=0.6
            ),
            row=4, col=1
        )
        
        # Add zero line for MACD
        fig.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.5, row=4, col=1)
        
        # Calculate key levels
        current_price = df['Close'].iloc[-1]
        high_52w = df['High'].rolling(window=min(252, len(df))).max().iloc[-1]
        low_52w = df['Low'].rolling(window=min(252, len(df))).min().iloc[-1]
        
        # Add current price annotation
        fig.add_annotation(
            x=df.index[-1],
            y=current_price,
            text=f"${current_price:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor="yellow",
            arrowwidth=2,
            bgcolor="rgba(255, 255, 0, 0.8)",
            bordercolor="black",
            borderwidth=1,
            font=dict(color="black", size=12),
            row=1, col=1
        )
        
        # Add 52-week high/low lines
        fig.add_hline(
            y=high_52w,
            line_dash="solid",
            line_color="green",
            line_width=2,
            opacity=0.7,
            annotation_text=f"52W High: ${high_52w:.2f}",
            annotation_position="top right",
            row=1, col=1
        )
        
        fig.add_hline(
            y=low_52w,
            line_dash="solid",
            line_color="red",
            line_width=2,
            opacity=0.7,
            annotation_text=f"52W Low: ${low_52w:.2f}",
            annotation_position="bottom right",
            row=1, col=1
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': f'{symbol} - Interactive Trading Dashboard',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': 'white'}
            },
            template='plotly_dark',
            height=1000,
            width=1600,
            
            # Hover settings
            hovermode='x unified',
            
            # Crosshair settings for all subplots
            xaxis_showspikes=True,
            yaxis_showspikes=True,
            xaxis2_showspikes=True,
            yaxis2_showspikes=True,
            xaxis3_showspikes=True,
            yaxis3_showspikes=True,
            xaxis4_showspikes=True,
            yaxis4_showspikes=True,
            
            # Spike styling
            xaxis_spikemode='across',
            yaxis_spikemode='across',
            xaxis_spikesnap='cursor',
            yaxis_spikesnap='cursor',
            xaxis_spikecolor='rgba(255, 255, 255, 0.8)',
            yaxis_spikecolor='rgba(255, 255, 255, 0.8)',
            xaxis_spikethickness=1,
            yaxis_spikethickness=1,
            
            # Range selector
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=7, label="7d", step="day", stepmode="backward"),
                        dict(count=30, label="1m", step="day", stepmode="backward"),
                        dict(count=90, label="3m", step="day", stepmode="backward"),
                        dict(count=180, label="6m", step="day", stepmode="backward"),
                        dict(count=365, label="1y", step="day", stepmode="backward"),
                        dict(step="all", label="All")
                    ]),
                    bgcolor="rgba(50, 50, 50, 0.8)",
                    activecolor="rgba(100, 100, 100, 0.8)",
                    font=dict(color="white")
                ),
                rangeslider=dict(visible=False),
                type="date"
            ),
            
            # Legend
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0, 0, 0, 0.5)"
            )
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=4, col=1)
        
        # Update x-axis labels
        fig.update_xaxes(showticklabels=False, row=1, col=1)
        fig.update_xaxes(showticklabels=False, row=2, col=1)
        fig.update_xaxes(showticklabels=False, row=3, col=1)
        fig.update_xaxes(title_text="Date", row=4, col=1)
        
        return fig, df
        
    except Exception as e:
        print(f"Error creating dashboard: {e}")
        return None, None

# Simple version with better error handling
def create_simple_interactive_chart(symbol='AAPL', period='6mo'):
    """
    Create a simple but fully interactive candlestick chart
    """
    try:
        # Download data
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if df.empty:
            print(f"No data found for symbol {symbol}")
            return None
        
        # Calculate simple indicators
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        
        # Create figure
        fig = go.Figure()
        
        # Add candlestick
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=symbol,
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444',
            increasing_fillcolor='rgba(0, 255, 136, 0.8)',
            decreasing_fillcolor='rgba(255, 68, 68, 0.8)'
        ))
        
        # Add moving averages
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA20'],
            mode='lines',
            name='MA20',
            line=dict(color='blue', width=2),
            opacity=0.8
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA50'],
            mode='lines',
            name='MA50',
            line=dict(color='red', width=2),
            opacity=0.8
        ))
        
        # Update layout with interactive features
        fig.update_layout(
            title={
                'text': f'{symbol} - Interactive Candlestick Chart',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            yaxis_title='Price ($)',
            xaxis_title='Date',
            template='plotly_dark',
            height=700,
            width=1400,
            
            # Interactive features
            hovermode='x unified',
            dragmode='zoom',
            
            # Crosshair cursor
            xaxis_showspikes=True,
            yaxis_showspikes=True,
            xaxis_spikemode='across',
            yaxis_spikemode='across',
            xaxis_spikesnap='cursor',
            yaxis_spikesnap='cursor',
            xaxis_spikecolor='white',
            yaxis_spikecolor='white',
            xaxis_spikethickness=1,
            yaxis_spikethickness=1,
            
            # Range selector
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=7, label="7d", step="day", stepmode="backward"),
                        dict(count=30, label="1m", step="day", stepmode="backward"),
                        dict(count=90, label="3m", step="day", stepmode="backward"),
                        dict(count=180, label="6m", step="day", stepmode="backward"),
                        dict(count=365, label="1y", step="day", stepmode="backward"),
                        dict(step="all", label="All")
                    ]),
                    bgcolor="rgba(50, 50, 50, 0.8)",
                    activecolor="rgba(100, 100, 100, 0.8)",
                    font=dict(color="white")
                ),
                rangeslider=dict(
                    visible=True,
                    thickness=0.1,
                    bgcolor="rgba(30, 30, 30, 0.8)"
                ),
                type="date"
            )
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating simple chart: {e}")
        return None

# Test both versions
print("Creating interactive trading charts...")

# Test simple version first
symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']

for symbol in symbols:
    print(f"\nCreating simple chart for {symbol}...")
    
    # Try simple version first
    fig_simple = create_simple_interactive_chart(symbol, '1y')
    
    if fig_simple is not None:
        # Show the chart
        fig_simple.show(config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': [
                'drawline',
                'drawopenpath',
                'drawclosedpath',
                'drawcircle',
                'drawrect',
                'eraseshape'
            ],
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f'{symbol}_simple_chart',
                'height': 700,
                'width': 1400,
                'scale': 2
            }
        })
        
        # Save as HTML
        fig_simple.write_html(f"{symbol}_simple_interactive.html")
        print(f"✓ Simple chart for {symbol} created successfully")
    
    # Try advanced dashboard
    print(f"Creating advanced dashboard for {symbol}...")
    fig_advanced, df = create_trading_dashboard(symbol, '1y')
    
    if fig_advanced is not None and df is not None:
        # Show the advanced chart
        fig_advanced.show(config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': [
                'drawline',
                'drawopenpath',
                'drawclosedpath',
                'drawcircle',
                'drawrect',
                'eraseshape'
            ],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f'{symbol}_advanced_dashboard',
                'height': 1000,
                'width': 1600,
                'scale': 2
            }
        })
        
        # Save as HTML
        fig_advanced.write_html(f"{symbol}_advanced_dashboard.html")
        
        # Print summary statistics
        current_price = df['Close'].iloc[-1]
        price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2]
        price_change_pct = (price_change / df['Close'].iloc[-2]) * 100
        
        print(f"✓ Advanced dashboard for {symbol} created successfully")
        print(f"  Current Price: ${current_price:.2f}")
        print(f"  Daily Change: ${price_change:.2f} ({price_change_pct:+.2f}%)")
        print(f"  52W High: ${df['High'].rolling(min(252, len(df))).max().iloc[-1]:.2f}")
        print(f"  52W Low: ${df['Low'].rolling(min(252, len(df))).min().iloc[-1]:.2f}")
        if not df['RSI'].isna().iloc[-1]:
            print(f"  Current RSI: {df['RSI'].iloc[-1]:.2f}")
    else:
        print(f"✗ Failed to create advanced dashboard for {symbol}")
    
    print("-" * 60)

print("\n🎉 Interactive trading charts created successfully!")

