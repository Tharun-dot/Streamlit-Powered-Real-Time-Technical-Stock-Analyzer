# 📊 Stock Investment Dashboard

A real-time stock analysis dashboard built with Streamlit that provides technical indicators and trading signals.

## Features

- 📈 Real-time stock data from Alpha Vantage API
- 📊 Interactive candlestick charts with technical indicators
- 🚦 Buy/Sell/Hold signals based on technical analysis
- 📱 Responsive web interface
- 🔄 Live data refresh

## Technical Indicators

- **SMA (Simple Moving Average)**: 20-day and 50-day
- **EMA (Exponential Moving Average)**: 20-day
- **RSI (Relative Strength Index)**: 14-day period
- **MACD**: Moving Average Convergence Divergence

## Setup

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Get Alpha Vantage API Key**:

   - Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - Sign up for a free API key
   - Set your API key in `config.py` or as an environment variable:
     ```bash
     export ALPHAVANTAGE_API_KEY="your_api_key_here"
     ```

3. **Run the dashboard**:
   ```bash
   streamlit run dashboard/app.py
   ```

## Usage

1. Enter a stock symbol in the sidebar (e.g., AAPL, MSFT, GOOGL)
2. Click "Refresh Data" to fetch the latest information
3. View the interactive chart with technical indicators
4. Check the latest trading signal (BUY/SELL/HOLD)

## Trading Strategy

The dashboard uses a simple rule-based strategy:

- **BUY Signal**: When SMA_20 crosses above SMA_50 AND RSI < 30 (oversold)
- **SELL Signal**: When SMA_20 crosses below SMA_50 AND RSI > 70 (overbought)
- **HOLD Signal**: All other conditions

## Project Structure

```
stock-dashboard/
├── data/                    # Sample data files
├── models/                  # Trading strategy models
├── services/                # External API services
├── dashboard/               # Streamlit web app
├── notebooks/               # Jupyter notebooks for analysis
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Disclaimer

This dashboard is for educational purposes only. Always do your own research before making investment decisions. Past performance does not guarantee future results.






