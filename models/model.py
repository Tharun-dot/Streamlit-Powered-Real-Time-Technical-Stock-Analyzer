# models/model.py
import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame):
    """
    Enhanced rule-based strategy with multiple conditions:
    - Buy signal: Multiple bullish conditions
    - Sell signal: Multiple bearish conditions
    - Hold signal: Neutral or conflicting signals
    """
    df = df.copy()
    df["Signal"] = "HOLD"
    
    # Calculate additional indicators for better signals
    df["SMA_20_prev"] = df["SMA_20"].shift(1)
    df["SMA_50_prev"] = df["SMA_50"].shift(1)
    df["RSI_prev"] = df["RSI"].shift(1)
    
    # Price momentum
    df["Price_Change_5d"] = df["Close"].pct_change(5)
    df["Volume_Avg"] = df["Volume"].rolling(20).mean()
    df["Volume_Ratio"] = df["Volume"] / df["Volume_Avg"]
    
    # MACD conditions
    if "MACD" in df.columns:
        df["MACD_prev"] = df["MACD"].shift(1)
        df["MACD_signal_prev"] = df["Signal_Line"].shift(1)
    
    # BUY CONDITIONS (any 2 or more must be true)
    buy_conditions = []
    
    # 1. SMA crossover (SMA_20 crosses above SMA_50)
    sma_crossover = (df["SMA_20"] > df["SMA_50"]) & (df["SMA_20_prev"] <= df["SMA_50_prev"])
    buy_conditions.append(sma_crossover)
    
    # 2. RSI oversold (RSI < 35 and improving)
    rsi_oversold = (df["RSI"] < 35) & (df["RSI"] > df["RSI_prev"])
    buy_conditions.append(rsi_oversold)
    
    # 3. Price above SMA_20 and rising
    price_above_sma = (df["Close"] > df["SMA_20"]) & (df["Close"] > df["Close"].shift(1))
    buy_conditions.append(price_above_sma)
    
    # 4. MACD bullish crossover
    if "MACD" in df.columns:
        macd_bullish = (df["MACD"] > df["Signal_Line"]) & (df["MACD_prev"] <= df["MACD_signal_prev"])
        buy_conditions.append(macd_bullish)
    
    # 5. High volume confirmation
    volume_confirmation = df["Volume_Ratio"] > 1.2
    buy_conditions.append(volume_confirmation)
    
    # 6. Positive momentum
    positive_momentum = df["Price_Change_5d"] > 0.02  # 2% gain in 5 days
    buy_conditions.append(positive_momentum)
    
    # SELL CONDITIONS (any 2 or more must be true)
    sell_conditions = []
    
    # 1. SMA crossover (SMA_20 crosses below SMA_50)
    sma_crossunder = (df["SMA_20"] < df["SMA_50"]) & (df["SMA_20_prev"] >= df["SMA_50_prev"])
    sell_conditions.append(sma_crossunder)
    
    # 2. RSI overbought (RSI > 65 and declining)
    rsi_overbought = (df["RSI"] > 65) & (df["RSI"] < df["RSI_prev"])
    sell_conditions.append(rsi_overbought)
    
    # 3. Price below SMA_20 and falling
    price_below_sma = (df["Close"] < df["SMA_20"]) & (df["Close"] < df["Close"].shift(1))
    sell_conditions.append(price_below_sma)
    
    # 4. MACD bearish crossover
    if "MACD" in df.columns:
        macd_bearish = (df["MACD"] < df["Signal_Line"]) & (df["MACD_prev"] >= df["MACD_signal_prev"])
        sell_conditions.append(macd_bearish)
    
    # 5. High volume on decline
    volume_decline = (df["Volume_Ratio"] > 1.2) & (df["Close"] < df["Close"].shift(1))
    sell_conditions.append(volume_decline)
    
    # 6. Negative momentum
    negative_momentum = df["Price_Change_5d"] < -0.02  # 2% loss in 5 days
    sell_conditions.append(negative_momentum)
    
    # Count conditions for each signal
    buy_score = sum(buy_conditions)
    sell_score = sum(sell_conditions)
    
    # Generate signals based on scores
    buy_mask = buy_score >= 2  # At least 2 buy conditions
    sell_mask = sell_score >= 2  # At least 2 sell conditions
    
    df.loc[buy_mask, "Signal"] = "BUY"
    df.loc[sell_mask & ~buy_mask, "Signal"] = "SELL"
    # HOLD is already set as default above
    
    # Clean up temporary columns
    temp_columns = ["SMA_20_prev", "SMA_50_prev", "RSI_prev", "Price_Change_5d", 
                   "Volume_Avg", "Volume_Ratio"]
    if "MACD" in df.columns:
        temp_columns.extend(["MACD_prev", "MACD_signal_prev"])
    
    df = df.drop(columns=[col for col in temp_columns if col in df.columns])
    
    return df
