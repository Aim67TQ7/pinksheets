#!/usr/bin/env python3
"""
Simplified Stock Analysis Engine
Performs technical analysis, sentiment analysis, and stock scoring
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.sp500_symbols = self._get_sp500_symbols()
        
    def _get_sp500_symbols(self):
        """Get S&P 500 stock symbols"""
        # Top 50 most liquid S&P 500 stocks for demo
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B', 'UNH', 'JNJ',
            'V', 'PG', 'JPM', 'HD', 'CVX', 'MA', 'PFE', 'ABBV', 'BAC', 'KO',
            'AVGO', 'PEP', 'TMO', 'COST', 'DIS', 'ABT', 'ACN', 'VZ', 'ADBE', 'WMT',
            'CRM', 'NFLX', 'XOM', 'NKE', 'DHR', 'CMCSA', 'LIN', 'ORCL', 'BMY', 'PM',
            'INTC', 'TXN', 'UPS', 'QCOM', 'RTX', 'HON', 'AMGN', 'SPGI', 'LOW', 'IBM'
        ]
    
    def get_stock_data(self, symbol, period='3mo'):
        """Fetch stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return None
                
            # Get additional info
            info = stock.info
            
            return {
                'data': data,
                'info': info,
                'symbol': symbol
            }
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_sma(self, data, window):
        """Calculate Simple Moving Average"""
        return data.rolling(window=window).mean()
    
    def calculate_ema(self, data, window):
        """Calculate Exponential Moving Average"""
        return data.ewm(span=window).mean()
    
    def calculate_rsi(self, data, window=14):
        """Calculate Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        ema_fast = self.calculate_ema(data, fast)
        ema_slow = self.calculate_ema(data, slow)
        macd = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd, signal)
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def calculate_bollinger_bands(self, data, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        sma = self.calculate_sma(data, window)
        std = data.rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        return upper_band, sma, lower_band
    
    def calculate_technical_indicators(self, data):
        """Calculate technical analysis indicators"""
        try:
            df = data.copy()
            
            # Moving Averages
            df['SMA_20'] = self.calculate_sma(df['Close'], 20)
            df['SMA_50'] = self.calculate_sma(df['Close'], 50)
            df['EMA_12'] = self.calculate_ema(df['Close'], 12)
            df['EMA_26'] = self.calculate_ema(df['Close'], 26)
            
            # RSI
            df['RSI'] = self.calculate_rsi(df['Close'])
            
            # MACD
            df['MACD'], df['MACD_Signal'], df['MACD_Histogram'] = self.calculate_macd(df['Close'])
            
            # Bollinger Bands
            df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = self.calculate_bollinger_bands(df['Close'])
            
            # Volume indicators
            df['Volume_SMA'] = self.calculate_sma(df['Volume'], 20)
            
            # Price change
            df['Price_Change'] = df['Close'].pct_change()
            df['Price_Change_5d'] = df['Close'].pct_change(periods=5)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return data
    
    def calculate_technical_score(self, df):
        """Calculate composite technical analysis score (0-100)"""
        try:
            latest = df.iloc[-1]
            scores = []
            
            # Trend Indicators (40% weight)
            trend_scores = []
            
            # Moving Average Trend
            if pd.notna(latest['SMA_20']) and pd.notna(latest['SMA_50']):
                if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
                    trend_scores.append(100)  # Strong uptrend
                elif latest['Close'] > latest['SMA_20']:
                    trend_scores.append(75)   # Moderate uptrend
                elif latest['Close'] > latest['SMA_50']:
                    trend_scores.append(50)   # Weak uptrend
                else:
                    trend_scores.append(25)   # Downtrend
            
            # RSI Score
            if pd.notna(latest['RSI']):
                rsi = latest['RSI']
                if 40 <= rsi <= 60:
                    trend_scores.append(100)  # Neutral zone
                elif 30 <= rsi < 40 or 60 < rsi <= 70:
                    trend_scores.append(75)   # Moderate
                elif 20 <= rsi < 30 or 70 < rsi <= 80:
                    trend_scores.append(50)   # Caution zone
                else:
                    trend_scores.append(25)   # Extreme zone
            
            # MACD Score
            if pd.notna(latest['MACD']) and pd.notna(latest['MACD_Signal']):
                if latest['MACD'] > latest['MACD_Signal'] and latest['MACD'] > 0:
                    trend_scores.append(100)  # Bullish above zero
                elif latest['MACD'] > latest['MACD_Signal']:
                    trend_scores.append(75)   # Bullish crossover
                else:
                    trend_scores.append(25)   # Bearish
            
            trend_score = np.mean(trend_scores) if trend_scores else 50
            scores.append(('trend', trend_score, 0.4))
            
            # Momentum Indicators (30% weight)
            momentum_scores = []
            
            # 5-day price change
            if pd.notna(latest['Price_Change_5d']):
                price_change = latest['Price_Change_5d'] * 100
                if price_change > 5:
                    momentum_scores.append(100)
                elif price_change > 2:
                    momentum_scores.append(75)
                elif price_change > -2:
                    momentum_scores.append(50)
                elif price_change > -5:
                    momentum_scores.append(25)
                else:
                    momentum_scores.append(10)
            
            # RSI momentum
            if pd.notna(latest['RSI']):
                rsi = latest['RSI']
                if 50 <= rsi <= 70:
                    momentum_scores.append(100)  # Good momentum
                elif 30 <= rsi < 50:
                    momentum_scores.append(75)   # Building momentum
                elif rsi > 70:
                    momentum_scores.append(50)   # Overbought
                else:
                    momentum_scores.append(25)   # Oversold
            
            momentum_score = np.mean(momentum_scores) if momentum_scores else 50
            scores.append(('momentum', momentum_score, 0.3))
            
            # Volume Indicators (20% weight)
            volume_scores = []
            
            # Volume trend
            if pd.notna(latest['Volume']) and pd.notna(latest['Volume_SMA']):
                volume_ratio = latest['Volume'] / latest['Volume_SMA']
                if volume_ratio > 1.5:
                    volume_scores.append(100)  # High volume
                elif volume_ratio > 1.2:
                    volume_scores.append(75)   # Above average
                elif volume_ratio > 0.8:
                    volume_scores.append(50)   # Normal
                else:
                    volume_scores.append(25)   # Low volume
            
            volume_score = np.mean(volume_scores) if volume_scores else 50
            scores.append(('volume', volume_score, 0.2))
            
            # Volatility Indicators (10% weight)
            volatility_scores = []
            
            # Bollinger Bands Position
            if pd.notna(latest['BB_Lower']) and pd.notna(latest['BB_Upper']):
                bb_position = (latest['Close'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower'])
                if 0.2 <= bb_position <= 0.8:
                    volatility_scores.append(100)  # Normal range
                elif bb_position > 0.8:
                    volatility_scores.append(50)   # Near upper band
                else:
                    volatility_scores.append(50)   # Near lower band
            
            volatility_score = np.mean(volatility_scores) if volatility_scores else 50
            scores.append(('volatility', volatility_score, 0.1))
            
            # Calculate weighted score
            total_score = sum(score * weight for _, score, weight in scores)
            
            return {
                'total_score': round(total_score, 2),
                'breakdown': {name: round(score, 2) for name, score, _ in scores},
                'latest_data': {
                    'price': round(latest['Close'], 2),
                    'rsi': round(latest['RSI'], 2) if pd.notna(latest['RSI']) else None,
                    'volume': int(latest['Volume']),
                    'sma_20': round(latest['SMA_20'], 2) if pd.notna(latest['SMA_20']) else None,
                    'sma_50': round(latest['SMA_50'], 2) if pd.notna(latest['SMA_50']) else None,
                    'price_change_5d': round(latest['Price_Change_5d'] * 100, 2) if pd.notna(latest['Price_Change_5d']) else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical score: {e}")
            return {'total_score': 50, 'breakdown': {}, 'latest_data': {}}
    
    def get_news_sentiment(self, symbol, company_name=None):
        """Get news sentiment for a stock (simplified version)"""
        try:
            # This is a simplified version - in production, you'd use NewsAPI or similar
            # For demo, we'll simulate sentiment based on recent price action
            
            stock_data = self.get_stock_data(symbol, period='1mo')
            if not stock_data or stock_data['data'].empty:
                return {'sentiment_score': 50, 'news_count': 0, 'summary': 'No data available'}
            
            # Calculate recent performance as proxy for sentiment
            recent_data = stock_data['data']
            recent_return = (recent_data['Close'].iloc[-1] / recent_data['Close'].iloc[-5] - 1) * 100
            
            # Convert performance to sentiment score
            if recent_return > 5:
                sentiment_score = 85
                sentiment_summary = "Positive market sentiment"
            elif recent_return > 2:
                sentiment_score = 70
                sentiment_summary = "Moderately positive sentiment"
            elif recent_return > -2:
                sentiment_score = 50
                sentiment_summary = "Neutral sentiment"
            elif recent_return > -5:
                sentiment_score = 30
                sentiment_summary = "Moderately negative sentiment"
            else:
                sentiment_score = 15
                sentiment_summary = "Negative market sentiment"
            
            return {
                'sentiment_score': sentiment_score,
                'news_count': 5,  # Simulated
                'summary': sentiment_summary,
                'recent_return': round(recent_return, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment for {symbol}: {e}")
            return {'sentiment_score': 50, 'news_count': 0, 'summary': 'Error retrieving sentiment'}
    
    def calculate_composite_score(self, technical_score, sentiment_score):
        """Calculate final composite score"""
        return round(technical_score * 0.7 + sentiment_score * 0.3, 2)
    
    def analyze_stock(self, symbol):
        """Complete analysis for a single stock"""
        try:
            logger.info(f"Analyzing {symbol}...")
            
            # Get stock data
            stock_data = self.get_stock_data(symbol)
            if not stock_data:
                return None
            
            # Calculate technical indicators
            df_with_indicators = self.calculate_technical_indicators(stock_data['data'])
            
            # Calculate technical score
            technical_analysis = self.calculate_technical_score(df_with_indicators)
            
            # Get sentiment score
            sentiment_analysis = self.get_news_sentiment(symbol, stock_data['info'].get('longName'))
            
            # Calculate composite score
            composite_score = self.calculate_composite_score(
                technical_analysis['total_score'],
                sentiment_analysis['sentiment_score']
            )
            
            # Get company info
            info = stock_data['info']
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'current_price': technical_analysis['latest_data']['price'],
                'composite_score': composite_score,
                'technical_score': technical_analysis['total_score'],
                'sentiment_score': sentiment_analysis['sentiment_score'],
                'technical_breakdown': technical_analysis['breakdown'],
                'sentiment_summary': sentiment_analysis['summary'],
                'volume': technical_analysis['latest_data']['volume'],
                'rsi': technical_analysis['latest_data']['rsi'],
                'sma_20': technical_analysis['latest_data']['sma_20'],
                'sma_50': technical_analysis['latest_data']['sma_50'],
                'price_change_5d': technical_analysis['latest_data']['price_change_5d'],
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def get_top_stocks(self, limit=10):
        """Analyze all stocks and return top performers"""
        logger.info("Starting comprehensive stock analysis...")
        
        results = []
        
        for symbol in self.sp500_symbols:
            try:
                analysis = self.analyze_stock(symbol)
                if analysis and analysis['market_cap'] > 1e9:  # Min $1B market cap
                    results.append(analysis)
                
                # Add small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
        
        # Sort by composite score
        sorted_results = sorted(results, key=lambda x: x['composite_score'], reverse=True)
        
        logger.info(f"Analysis complete. Found {len(sorted_results)} valid stocks.")
        
        return sorted_results[:limit]

def main():
    """Test the stock analyzer"""
    analyzer = StockAnalyzer()
    
    # Test with a few stocks
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    print("Testing Stock Analyzer...")
    print("=" * 50)
    
    for symbol in test_symbols:
        result = analyzer.analyze_stock(symbol)
        if result:
            print(f"\n{result['symbol']} - {result['company_name']}")
            print(f"Composite Score: {result['composite_score']}")
            print(f"Technical Score: {result['technical_score']}")
            print(f"Sentiment Score: {result['sentiment_score']}")
            print(f"Current Price: ${result['current_price']}")
            print(f"RSI: {result['rsi']}")
            print(f"5-day Change: {result['price_change_5d']}%")
        else:
            print(f"\nFailed to analyze {symbol}")

if __name__ == "__main__":
    main()

