#!/usr/bin/env python3
"""
Real Data Integration with Pink Sheets Support
Enhanced Stock Analysis with Live Data and OTC Markets
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealDataStockAnalyzer:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Enhanced stock universe including OTC/Pink Sheets
        self.stock_universe = {
            # Large Cap Leaders
            'LARGE_CAP': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B', 'UNH', 'JNJ'],
            
            # High Growth Mid-Caps
            'GROWTH_MIDCAP': ['PLTR', 'SNOW', 'CRWD', 'NET', 'RBLX', 'COIN', 'SOFI', 'UPST', 'HOOD', 'SQ'],
            
            # Emerging Tech
            'EMERGING_TECH': ['RIVN', 'LCID', 'CHPT', 'BE', 'PLUG', 'ENPH', 'SEDG', 'FSLR', 'SPWR', 'RUN'],
            
            # Biotech & Pharma
            'BIOTECH': ['MRNA', 'BNTX', 'NVAX', 'VXRT', 'INO', 'OCGN', 'SRNE', 'ATOS', 'CTXR', 'JAGX'],
            
            # Pink Sheets / OTC (High Risk, High Reward)
            'PINK_SHEETS': [
                # Cannabis & Hemp
                'HEMP', 'CBDD', 'GRNH', 'TRTC', 'MCOA', 'MJNA', 'ERBB', 'DEWM', 'GTEH', 'MYDX',
                
                # Mining & Resources  
                'GORO', 'AUNFF', 'SILV', 'GLDG', 'LODE', 'MMTLP', 'HYMC', 'GHDC', 'RTON', 'MINE',
                
                # Tech & Innovation
                'HMBL', 'OZSC', 'AITX', 'ABML', 'ALPP', 'TLSS', 'PASO', 'GVSI', 'PHIL', 'INND',
                
                # Energy & Clean Tech
                'OPTI', 'EEENF', 'PVDG', 'RECO', 'RECAF', 'CGFIA', 'PUGE', 'SIRC', 'SNPW', 'RGGI',
                
                # Biotech & Medical
                'BVTK', 'RLFTF', 'CYDY', 'VBIV', 'ADXS', 'BIEL', 'RVVTF', 'ENZC', 'BBRW', 'GCAN'
            ],
            
            # Penny Stocks (Under $5)
            'PENNY_STOCKS': ['SNDL', 'NOK', 'NAKD', 'CTRM', 'SHIP', 'TOPS', 'GNUS', 'XSPA', 'IDEX', 'UAVS']
        }
    
    def get_all_symbols(self):
        """Get all stock symbols including pink sheets"""
        all_symbols = []
        for category, symbols in self.stock_universe.items():
            all_symbols.extend(symbols)
        return list(set(all_symbols))  # Remove duplicates
    
    def get_real_stock_data(self, symbol, period="3mo"):
        """Get real stock data from Yahoo Finance with OTC support"""
        try:
            # Try different symbol formats for OTC stocks
            symbol_variants = [
                symbol,
                f"{symbol}.PK",  # Pink sheets format
                f"{symbol}.OB",  # OTC Bulletin Board format
                f"{symbol}.OTC"  # Generic OTC format
            ]
            
            for variant in symbol_variants:
                try:
                    stock = yf.Ticker(variant)
                    data = stock.history(period=period)
                    
                    if not data.empty and len(data) > 20:  # Ensure sufficient data
                        logger.info(f"Successfully fetched data for {variant}")
                        return data, variant
                        
                except Exception as e:
                    continue
            
            logger.warning(f"No data found for {symbol} in any format")
            return None, None
            
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None, None
    
    def calculate_enhanced_technical_indicators(self, data):
        """Calculate comprehensive technical indicators"""
        try:
            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data['Volume']
            
            # Price-based indicators
            sma_20 = close.rolling(window=20).mean()
            sma_50 = close.rolling(window=50).mean()
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD
            macd = ema_12 - ema_26
            macd_signal = macd.ewm(span=9).mean()
            macd_histogram = macd - macd_signal
            
            # Bollinger Bands
            bb_middle = close.rolling(window=20).mean()
            bb_std = close.rolling(window=20).std()
            bb_upper = bb_middle + (bb_std * 2)
            bb_lower = bb_middle - (bb_std * 2)
            
            # Volume indicators
            volume_sma = volume.rolling(window=20).mean()
            volume_ratio = volume / volume_sma
            
            # Volatility
            returns = close.pct_change()
            volatility = returns.rolling(window=20).std() * np.sqrt(252) * 100
            
            return {
                'sma_20': sma_20.iloc[-1] if not sma_20.empty else 0,
                'sma_50': sma_50.iloc[-1] if not sma_50.empty else 0,
                'rsi': rsi.iloc[-1] if not rsi.empty else 50,
                'macd': macd.iloc[-1] if not macd.empty else 0,
                'macd_signal': macd_signal.iloc[-1] if not macd_signal.empty else 0,
                'bb_upper': bb_upper.iloc[-1] if not bb_upper.empty else 0,
                'bb_lower': bb_lower.iloc[-1] if not bb_lower.empty else 0,
                'volume_ratio': volume_ratio.iloc[-1] if not volume_ratio.empty else 1,
                'volatility': volatility.iloc[-1] if not volatility.empty else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return {}
    
    def get_stock_category(self, symbol):
        """Determine stock category for risk-adjusted scoring"""
        for category, symbols in self.stock_universe.items():
            if symbol in symbols or symbol.replace('.PK', '').replace('.OB', '').replace('.OTC', '') in symbols:
                return category
        return 'UNKNOWN'
    
    def calculate_enhanced_score(self, symbol, current_price, indicators, price_changes):
        """Enhanced scoring system with category-specific adjustments"""
        try:
            category = self.get_stock_category(symbol)
            base_score = 50
            
            # RSI scoring with category adjustments
            rsi = indicators.get('rsi', 50)
            if category in ['PINK_SHEETS', 'PENNY_STOCKS']:
                # More aggressive scoring for high-risk stocks
                if 20 <= rsi <= 80:
                    base_score += 25
                elif rsi < 20:
                    base_score += 40  # Extremely oversold
            else:
                # Conservative scoring for established stocks
                if 30 <= rsi <= 70:
                    base_score += 20
                elif rsi < 30:
                    base_score += 30
            
            # Moving average trends
            sma_20 = indicators.get('sma_20', 0)
            sma_50 = indicators.get('sma_50', 0)
            
            if current_price > sma_20 > 0:
                base_score += 15
            if current_price > sma_50 > 0:
                base_score += 10
            if sma_20 > sma_50 > 0:  # Bullish crossover
                base_score += 10
            
            # MACD momentum
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            if macd > macd_signal:
                base_score += 10
            
            # Price momentum scoring
            price_1d = price_changes.get('1d', 0)
            price_5d = price_changes.get('5d', 0)
            price_20d = price_changes.get('20d', 0)
            
            # Multi-timeframe momentum
            if price_1d > 0:
                base_score += 5
            if 0 < price_5d < 20:
                base_score += 15
            elif price_5d > 20:
                base_score += 10  # High momentum but risky
            if 0 < price_20d < 50:
                base_score += 10
            
            # Volume confirmation
            volume_ratio = indicators.get('volume_ratio', 1)
            if volume_ratio > 2:
                base_score += 15  # High volume breakout
            elif volume_ratio > 1.5:
                base_score += 10
            
            # Volatility adjustment
            volatility = indicators.get('volatility', 0)
            if category in ['PINK_SHEETS', 'PENNY_STOCKS']:
                # High volatility is expected and potentially rewarding
                if volatility > 100:
                    base_score += 20
                elif volatility > 50:
                    base_score += 15
            else:
                # Prefer moderate volatility for established stocks
                if 20 < volatility < 40:
                    base_score += 10
            
            # Category-specific bonuses
            category_bonuses = {
                'PINK_SHEETS': 25,      # Highest potential
                'PENNY_STOCKS': 20,     # High potential
                'EMERGING_TECH': 15,    # Growth potential
                'BIOTECH': 15,          # Innovation potential
                'GROWTH_MIDCAP': 10,    # Established growth
                'LARGE_CAP': 5          # Stability
            }
            
            base_score += category_bonuses.get(category, 0)
            
            # Risk adjustment for pink sheets
            if category == 'PINK_SHEETS':
                # Additional criteria for pink sheets
                if current_price < 0.01:  # Sub-penny stocks
                    base_score += 30  # Extreme risk/reward
                elif current_price < 0.10:
                    base_score += 20
                elif current_price < 1.00:
                    base_score += 10
            
            return min(base_score, 200)  # Cap at 200 for extreme opportunities
            
        except Exception as e:
            logger.error(f"Error calculating score for {symbol}: {e}")
            return 50
    
    def analyze_stock_real_data(self, symbol):
        """Analyze stock with real market data"""
        logger.info(f"Analyzing {symbol} with real data...")
        
        data, actual_symbol = self.get_real_stock_data(symbol)
        if data is None:
            return None
        
        try:
            current_price = data['Close'].iloc[-1]
            volume = data['Volume'].iloc[-1]
            
            # Calculate price changes
            price_changes = {}
            if len(data) >= 2:
                price_changes['1d'] = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            if len(data) >= 6:
                price_changes['5d'] = ((current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6]) * 100
            if len(data) >= 21:
                price_changes['20d'] = ((current_price - data['Close'].iloc[-21]) / data['Close'].iloc[-21]) * 100
            
            # Technical indicators
            indicators = self.calculate_enhanced_technical_indicators(data)
            
            # Enhanced scoring
            score = self.calculate_enhanced_score(symbol, current_price, indicators, price_changes)
            
            # Category and risk assessment
            category = self.get_stock_category(symbol)
            
            return {
                'symbol': actual_symbol,
                'original_symbol': symbol,
                'price': round(current_price, 4),  # More precision for penny stocks
                'volume': int(volume),
                'category': category,
                'score': round(score, 1),
                'rsi': round(indicators.get('rsi', 50), 1),
                'price_change_1d': round(price_changes.get('1d', 0), 2),
                'price_change_5d': round(price_changes.get('5d', 0), 2),
                'price_change_20d': round(price_changes.get('20d', 0), 2),
                'volume_ratio': round(indicators.get('volume_ratio', 1), 2),
                'volatility': round(indicators.get('volatility', 0), 1),
                'macd_signal': 'BUY' if indicators.get('macd', 0) > indicators.get('macd_signal', 0) else 'NEUTRAL',
                'trend': 'BULLISH' if current_price > indicators.get('sma_20', 0) > indicators.get('sma_50', 0) else 'NEUTRAL',
                'risk_level': self.assess_risk_level(category, current_price, indicators.get('volatility', 0))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def assess_risk_level(self, category, price, volatility):
        """Assess risk level based on category and metrics"""
        if category == 'PINK_SHEETS':
            if price < 0.01:
                return 'EXTREME'
            elif price < 0.10:
                return 'VERY HIGH'
            else:
                return 'HIGH'
        elif category == 'PENNY_STOCKS':
            return 'HIGH'
        elif category in ['BIOTECH', 'EMERGING_TECH']:
            return 'MEDIUM-HIGH'
        elif volatility > 50:
            return 'MEDIUM-HIGH'
        else:
            return 'MEDIUM'
    
    def run_real_analysis(self, max_stocks=50):
        """Run analysis on real market data"""
        print("🚀 REAL DATA STOCK ANALYSIS - Including Pink Sheets")
        print("=" * 70)
        
        all_symbols = self.get_all_symbols()
        print(f"📊 Analyzing {len(all_symbols)} stocks across all categories...")
        print(f"🎯 Including {len(self.stock_universe['PINK_SHEETS'])} Pink Sheet stocks")
        print()
        
        results = []
        analyzed_count = 0
        
        # Prioritize pink sheets and penny stocks for higher potential
        priority_symbols = (
            self.stock_universe['PINK_SHEETS'] + 
            self.stock_universe['PENNY_STOCKS'] + 
            self.stock_universe['EMERGING_TECH']
        )
        
        # Analyze priority symbols first
        for symbol in priority_symbols[:max_stocks//2]:
            if analyzed_count >= max_stocks:
                break
                
            result = self.analyze_stock_real_data(symbol)
            if result:
                results.append(result)
                print(f"   ✓ {result['symbol']} (${result['price']:.4f}) - Score: {result['score']}")
                analyzed_count += 1
        
        # Fill remaining slots with other categories
        remaining_symbols = [s for s in all_symbols if s not in priority_symbols]
        for symbol in remaining_symbols[:max_stocks - analyzed_count]:
            result = self.analyze_stock_real_data(symbol)
            if result:
                results.append(result)
                print(f"   ✓ {result['symbol']} (${result['price']:.4f}) - Score: {result['score']}")
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Display results
        print(f"\n🏆 TOP 15 REAL-TIME RECOMMENDATIONS:")
        print("-" * 70)
        print("Rank | Symbol      | Price      | Score | Risk      | Category")
        print("-" * 70)
        
        for i, stock in enumerate(results[:15], 1):
            category_short = stock['category'].replace('_', ' ')[:10]
            print(f"{i:2d}   | {stock['symbol']:11s} | ${stock['price']:9.4f} | {stock['score']:5.1f} | {stock['risk_level']:9s} | {category_short}")
        
        # Save results
        self.save_analysis_results(results)
        
        return results
    
    def save_analysis_results(self, results):
        """Save analysis results to JSON file"""
        try:
            output_file = self.data_dir / f"real_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            
            analysis_data = {
                'timestamp': datetime.now().isoformat(),
                'total_analyzed': len(results),
                'top_recommendations': results[:10],
                'all_results': results
            }
            
            with open(output_file, 'w') as f:
                json.dump(analysis_data, f, indent=2, default=str)
            
            logger.info(f"Analysis results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")

if __name__ == "__main__":
    analyzer = RealDataStockAnalyzer()
    results = analyzer.run_real_analysis(max_stocks=30)
    
    print(f"\n💡 PINK SHEETS INTEGRATION SUCCESS!")
    print(f"✓ Real-time data from Yahoo Finance")
    print(f"✓ Pink sheet stocks with .PK format support")
    print(f"✓ Enhanced scoring for high-risk/high-reward opportunities")
    print(f"✓ Risk assessment for all categories")
    print(f"✓ Results saved for web integration")

