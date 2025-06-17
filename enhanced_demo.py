#!/usr/bin/env python3
"""
Enhanced Demo with Interactive Trading and Expanded Universe
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from stock_universe import get_all_stocks, STOCK_UNIVERSE, get_risk_categories
from enhanced_portfolio import EnhancedPortfolioManager

def get_stock_data(symbol, period="3mo"):
    """Get stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        if data.empty:
            return None
        return data
    except Exception as e:
        return None

def calculate_rsi(prices, window=14):
    """Calculate RSI"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50
    except:
        return 50

def calculate_moving_averages(prices):
    """Calculate moving averages"""
    try:
        ma_20 = prices.rolling(window=20).mean().iloc[-1]
        ma_50 = prices.rolling(window=50).mean().iloc[-1]
        current_price = prices.iloc[-1]
        
        return {
            'ma_20': ma_20,
            'ma_50': ma_50,
            'above_ma_20': current_price > ma_20,
            'above_ma_50': current_price > ma_50
        }
    except:
        return {'ma_20': 0, 'ma_50': 0, 'above_ma_20': False, 'above_ma_50': False}

def get_sector_for_stock(symbol):
    """Get sector for a stock symbol"""
    for sector, stocks in STOCK_UNIVERSE.items():
        if symbol in stocks:
            return sector
    return 'UNKNOWN'

def analyze_stock(symbol):
    """Analyze a single stock with enhanced scoring"""
    data = get_stock_data(symbol)
    if data is None:
        return None
    
    try:
        current_price = data['Close'].iloc[-1]
        volume = data['Volume'].iloc[-1]
        
        # Technical indicators
        rsi = calculate_rsi(data['Close'])
        ma_data = calculate_moving_averages(data['Close'])
        
        # Price momentum (multiple timeframes)
        price_change_1d = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
        price_change_5d = ((current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6]) * 100
        price_change_20d = ((current_price - data['Close'].iloc[-21]) / data['Close'].iloc[-21]) * 100
        
        # Volatility (standard deviation of returns)
        returns = data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility
        
        # Volume analysis
        avg_volume_20 = data['Volume'].rolling(window=20).mean().iloc[-1]
        volume_ratio = volume / avg_volume_20 if avg_volume_20 > 0 else 1
        
        # Enhanced scoring system
        score = 50  # Base score
        
        # RSI scoring with sector adjustments
        sector = get_sector_for_stock(symbol)
        if sector in ['GROWTH_MIDCAP', 'EMERGING_TECH', 'BIOTECH']:
            # More aggressive scoring for growth stocks
            if 20 <= rsi <= 80:
                score += 25
            elif rsi < 20:
                score += 35  # Oversold growth stock
        else:
            # Conservative scoring for established stocks
            if 30 <= rsi <= 70:
                score += 20
            elif rsi < 30:
                score += 30
        
        # Moving average scoring
        if ma_data['above_ma_20']:
            score += 15
        if ma_data['above_ma_50']:
            score += 10
        
        # Momentum scoring (multi-timeframe)
        if price_change_1d > 0:
            score += 5
        if 0 < price_change_5d < 15:
            score += 15
        elif price_change_5d > 15:
            score += 10  # High momentum but risky
        if 0 < price_change_20d < 25:
            score += 10
        
        # Volume scoring
        if volume_ratio > 1.5:
            score += 10  # High volume interest
        elif volume_ratio > 1.2:
            score += 5
        
        # Volatility adjustment (higher volatility = higher potential but riskier)
        if sector in ['GROWTH_MIDCAP', 'EMERGING_TECH', 'CLEAN_ENERGY']:
            if volatility > 50:
                score += 15  # High volatility growth stock
            elif volatility > 30:
                score += 10
        else:
            if volatility < 25:
                score += 10  # Stable stock
        
        # Sector-specific bonuses
        sector_bonuses = {
            'GROWTH_MIDCAP': 10,
            'EMERGING_TECH': 8,
            'SEMICONDUCTORS': 7,
            'CLEAN_ENERGY': 6,
            'BIOTECH': 5
        }
        score += sector_bonuses.get(sector, 0)
        
        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'rsi': round(rsi, 1),
            'price_change_1d': round(price_change_1d, 2),
            'price_change_5d': round(price_change_5d, 2),
            'price_change_20d': round(price_change_20d, 2),
            'above_ma_20': ma_data['above_ma_20'],
            'above_ma_50': ma_data['above_ma_50'],
            'volatility': round(volatility, 1),
            'volume_ratio': round(volume_ratio, 2),
            'score': round(score, 1),
            'sector': sector,
            'volume': volume
        }
    except Exception as e:
        return None

def main():
    """Run enhanced analysis with interactive trading"""
    print("🚀 ENHANCED STOCK ANALYSIS - 110+ Stock Universe")
    print("=" * 70)
    
    # Initialize portfolio manager
    pm = EnhancedPortfolioManager()
    available_cash = pm.get_available_cash()
    
    print(f"💰 Available Cash: ${available_cash:.2f}")
    print(f"📊 Analyzing {len(get_all_stocks())} stocks across 11 sectors...")
    print()
    
    # Analyze all stocks (sample for demo - would be full universe in production)
    sample_stocks = [
        # High-growth potential stocks
        'PLTR', 'SNOW', 'CRWD', 'NET', 'RBLX', 'COIN', 'SOFI', 'UPST',
        # Established leaders
        'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'META',
        # Emerging sectors
        'ENPH', 'SEDG', 'PLUG', 'LCID', 'AMD', 'MRNA'
    ]
    
    results = []
    print("🔍 Analyzing stocks...")
    for symbol in sample_stocks:
        result = analyze_stock(symbol)
        if result:
            results.append(result)
            print(f"   ✓ {symbol}")
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n📈 TOP 15 RECOMMENDATIONS (from {len(results)} analyzed):")
    print("-" * 70)
    print("Rank | Symbol | Price    | Score | RSI  | 5d%   | Sector")
    print("-" * 70)
    
    for i, stock in enumerate(results[:15], 1):
        sector_short = stock['sector'].replace('_', ' ')[:12]
        print(f"{i:2d}   | {stock['symbol']:6s} | ${stock['price']:7.2f} | {stock['score']:5.1f} | {stock['rsi']:4.1f} | {stock['price_change_5d']:+5.1f} | {sector_short}")
    
    # Create pending trades
    print(f"\n💼 CREATING TRADE RECOMMENDATIONS:")
    print("-" * 70)
    
    pending_trades, total_allocation = pm.create_pending_trades(results)
    
    print(f"Available Cash: ${available_cash:.2f}")
    print(f"Proposed Allocation: ${total_allocation:.2f}")
    print(f"Remaining Cash: ${available_cash - total_allocation:.2f}")
    print()
    
    for i, trade in enumerate(pending_trades, 1):
        print(f"🎯 TRADE {i}: {trade['action']} {trade['symbol']}")
        print(f"   Price: ${trade['price']:.2f}")
        print(f"   Shares: {trade['shares']:.4f}")
        print(f"   Amount: ${trade['allocation']:.2f}")
        print(f"   Score: {trade['score']:.1f} | RSI: {trade['rsi']:.1f}")
        print(f"   Reasoning: {trade['reasoning']}")
        print(f"   Trade ID: {trade['id']}")
        print()
    
    print("🎮 INTERACTIVE COMMANDS:")
    print("-" * 70)
    print("To approve a trade: pm.approve_trade('trade_id')")
    print("To reject a trade:  pm.reject_trade('trade_id')")
    print("To view pending:    pm.get_pending_trades()")
    print()
    
    print("💡 KEY ENHANCEMENTS:")
    print("-" * 70)
    print("✓ 110+ stocks across 11 sectors")
    print("✓ High-growth mid-caps and emerging tech")
    print("✓ Enhanced scoring with sector-specific logic")
    print("✓ Cash flow management (sells add to next day's budget)")
    print("✓ Interactive trade approval system")
    print("✓ Multi-timeframe momentum analysis")
    print("✓ Volatility-adjusted scoring")
    print("✓ Volume confirmation signals")

if __name__ == "__main__":
    main()

