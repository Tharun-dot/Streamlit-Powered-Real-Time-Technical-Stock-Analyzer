# services/alphavantage_api.py
import requests
import pandas as pd
from config import ALPHAVANTAGE_API_KEY, REQUEST_TIMEOUT
import time

BASE_URL = "https://www.alphavantage.co/query"

def fetch_daily_data(symbol="AAPL"):
    """Fetch daily stock data from Alpha Vantage API"""
    if ALPHAVANTAGE_API_KEY == "YOUR_API_KEY_HERE":
        raise ValueError("Please set your Alpha Vantage API key in config.py or as an environment variable")
    
    url = f"{BASE_URL}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}&outputsize=compact"
    
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")
    except ValueError as e:
        raise Exception(f"JSON decode error: {e}")

    # Check for API errors
    if "Error Message" in data:
        raise Exception(f"API Error: {data['Error Message']}")
    if "Note" in data:
        raise Exception(f"API Rate Limit: {data['Note']}")
    if "Time Series (Daily)" not in data:
        raise Exception(f"Invalid data format: {data}")

    try:
        df = pd.DataFrame(data["Time Series (Daily)"]).T
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        }).astype(float)

        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        
        # Check if we have enough data
        if len(df) < 50:
            raise Exception(f"Insufficient data: only {len(df)} days available")
            
        return df
    except Exception as e:
        raise Exception(f"Data processing error: {e}")
