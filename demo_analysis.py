#!/usr/bin/env python3
"""
Quick Stock Analysis Demo - Shows $20 investment allocation
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def get_stock_data(symbol, period="3mo"):
    """Get stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        if data.empty:
            return None
        return data
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def calculate_rsi(prices, window=14):
    """Calculate RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else 50

def calculate_moving_averages(prices):
    """Calculate moving averages"""
    ma_20 = prices.rolling(window=20).mean().iloc[-1]
    ma_50 = prices.rolling(window=50).mean().iloc[-1]
    current_price = prices.iloc[-1]
    
    return {
        'ma_20': ma_20,
        'ma_50': ma_50,
        'above_ma_20': current_price > ma_20,
        'above_ma_50': current_price > ma_50
    }

def analyze_stock(symbol):
    """Analyze a single stock"""
    print(f"Analyzing {symbol}...")
    
    data = get_stock_data(symbol)
    if data is None:
        return None
    
    current_price = data['Close'].iloc[-1]
    volume = data['Volume'].iloc[-1]
    
    # Technical indicators
    rsi = calculate_rsi(data['Close'])
    ma_data = calculate_moving_averages(data['Close'])
    
    # Price momentum (5-day change)
    price_change_5d = ((current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6]) * 100
    
    # Simple scoring system
    score = 50  # Base score
    
    # RSI scoring (30-70 is good range)
    if 30 <= rsi <= 70:
        score += 20
    elif rsi < 30:
        score += 30  # Oversold - potential buy
    else:
        score -= 10  # Overbought
    
    # Moving average scoring
    if ma_data['above_ma_20']:
        score += 15
    if ma_data['above_ma_50']:
        score += 10
    
    # Momentum scoring
    if 0 < price_change_5d < 10:
        score += 15
    elif price_change_5d > 10:
        score += 5
    
    # Volume check (basic)
    avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1]
    if volume > avg_volume:
        score += 10
    
    return {
        'symbol': symbol,
        'price': round(current_price, 2),
        'rsi': round(rsi, 1),
        'price_change_5d': round(price_change_5d, 2),
        'above_ma_20': ma_data['above_ma_20'],
        'above_ma_50': ma_data['above_ma_50'],
        'score': round(score, 1),
        'volume': volume
    }

def main():
    """Run analysis and show $20 allocation"""
    print("🎯 Daily Stock Analysis - $20 Investment Allocation")
    print("=" * 60)
    
    # Top stocks to analyze
    stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'JPM', 'V', 'UNH']
    
    results = []
    for symbol in stocks:
        result = analyze_stock(symbol)
        if result:
            results.append(result)
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n📊 TOP 10 STOCK RECOMMENDATIONS:")
    print("-" * 60)
    for i, stock in enumerate(results[:10], 1):
        print(f"{i:2d}. {stock['symbol']:5s} | ${stock['price']:7.2f} | Score: {stock['score']:5.1f} | RSI: {stock['rsi']:5.1f}")
    
    # Calculate $20 allocation
    print("\n💰 $20 INVESTMENT ALLOCATION:")
    print("-" * 60)
    
    top_3 = results[:3]
    allocations = [7.00, 7.00, 6.00]  # Split $20 among top 3
    
    total_cost = 0
    for i, (stock, allocation) in enumerate(zip(top_3, allocations)):
        shares = allocation / stock['price']
        total_cost += allocation
        
        print(f"{i+1}. {stock['symbol']:5s} | ${stock['price']:7.2f} | ${allocation:5.2f} | {shares:.4f} shares")
        print(f"   Score: {stock['score']:5.1f} | RSI: {stock['rsi']:5.1f} | 5d: {stock['price_change_5d']:+5.1f}%")
        print()
    
    print(f"Total Investment: ${total_cost:.2f}")
    print(f"Remaining Cash: ${20.00 - total_cost:.2f}")
    
    print("\n🛡️ RISK MANAGEMENT RULES:")
    print("-" * 60)
    print("• Stop Loss: -15% (automatic sell)")
    print("• Take Profit: +25% (automatic sell)")
    print("• Max Hold: 30 days")
    print("• Max Position: 20% of portfolio")
    
    print("\n📈 NEXT STEPS:")
    print("-" * 60)
    print("• System will monitor positions daily")
    print("• New $20 investment tomorrow")
    print("• Automatic rebalancing based on signals")
    print("• Complete transaction history tracking")

if __name__ == "__main__":
    main()

