# services/indicators.py
import pandas as pd
import numpy as np

def add_indicators(df: pd.DataFrame):
    """Add SMA, EMA, RSI, MACD indicators to stock dataframe"""
    # Simple Moving Averages
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["SMA_50"] = df["Close"].rolling(50).mean()
    
    # Exponential Moving Average
    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    
    # RSI calculation
    df["RSI"] = calculate_rsi(df["Close"], 14)
    
    # MACD calculation
    df["MACD"], df["Signal_Line"], df["MACD_Histogram"] = calculate_macd(df["Close"])
    
    return df

def calculate_rsi(prices, period=14):
    """Calculate RSI (Relative Strength Index)"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal).mean()
    macd_histogram = macd - macd_signal
    return macd, macd_signal, macd_histogram
