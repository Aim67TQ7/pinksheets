#!/usr/bin/env python3
"""
Pink Sheet Automation Engine
Fully automated pink sheet trading system with 4-week simulation
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PinkSheetAutomationEngine:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Pink sheet focused universe
        self.pink_sheet_universe = {
            'CANNABIS_HEMP': [
                'CBDD', 'MJNA', 'HEMP', 'GRNH', 'TRTC', 'MCOA', 'ERBB', 
                'DEWM', 'GTEH', 'MYDX', 'PHBI', 'CNAB', 'CANB', 'MJNE'
            ],
            'MINING_RESOURCES': [
                'GORO', 'LODE', 'GLDG', 'SILV', 'HYMC', 'AUNFF', 'MMTLP',
                'GHDC', 'RTON', 'MINE', 'BMIX', 'SFIO', 'DRGD', 'MNGG'
            ],
            'TECH_INNOVATION': [
                'HMBL', 'OZSC', 'AITX', 'ABML', 'ALPP', 'TLSS', 'PASO',
                'GVSI', 'PHIL', 'INND', 'VPER', 'ILUS', 'IFAN', 'SANP'
            ],
            'ENERGY_CLEANTECH': [
                'OPTI', 'EEENF', 'PVDG', 'RECO', 'RECAF', 'CGFIA', 'PUGE',
                'SIRC', 'SNPW', 'RGGI', 'WNFT', 'BKEN', 'COCP', 'HALB'
            ],
            'BIOTECH_MEDICAL': [
                'BVTK', 'RLFTF', 'CYDY', 'ENZC', 'BIEL', 'RVVTF', 'BBRW',
                'GCAN', 'ADXS', 'VBIV', 'ATOS', 'CTXR', 'JAGX', 'OCGN'
            ]
        }
        
        # Trading parameters optimized for pink sheets
        self.daily_investment = 20.0
        self.stop_loss_pct = -20.0  # Wider for pink sheet volatility
        self.take_profit_pct = 50.0  # Higher target for pink sheets
        self.max_holding_days = 14  # Faster turnover
        self.pink_sheet_allocation = 0.75  # 75% to pink sheets
        
        # Portfolio files
        self.portfolio_file = self.data_dir / "pink_portfolio.json"
        self.transactions_file = self.data_dir / "pink_transactions.json"
        self.performance_file = self.data_dir / "pink_performance.json"
        self.automation_log = self.data_dir / "automation_log.json"
    
    def get_all_pink_sheets(self):
        """Get all pink sheet symbols"""
        all_symbols = []
        for category, symbols in self.pink_sheet_universe.items():
            all_symbols.extend(symbols)
        return list(set(all_symbols))
    
    def get_pink_sheet_data(self, symbol, period="1mo"):
        """Get pink sheet data with multiple format attempts"""
        symbol_variants = [
            symbol,
            f"{symbol}.PK",
            f"{symbol}.OB", 
            f"{symbol}.OTC"
        ]
        
        for variant in symbol_variants:
            try:
                stock = yf.Ticker(variant)
                data = stock.history(period=period)
                
                if not data.empty and len(data) >= 10:
                    logger.info(f"✓ Data found for {variant}")
                    return data, variant
                    
            except Exception as e:
                continue
        
        logger.warning(f"✗ No data for {symbol}")
        return None, None
    
    def calculate_pink_sheet_score(self, symbol, data, variant):
        """Pink sheet specific scoring algorithm"""
        try:
            close = data['Close']
            volume = data['Volume']
            current_price = close.iloc[-1]
            
            # Base score
            score = 50
            
            # Price-based scoring (sub-penny bonus)
            if current_price < 0.001:
                score += 50  # Extreme sub-penny
            elif current_price < 0.01:
                score += 40  # Sub-penny
            elif current_price < 0.10:
                score += 30  # Dime stocks
            elif current_price < 1.00:
                score += 20  # Under $1
            
            # Volume analysis (critical for pink sheets)
            if len(volume) >= 5:
                recent_volume = volume.iloc[-1]
                avg_volume = volume.rolling(window=min(10, len(volume))).mean().iloc[-1]
                
                if recent_volume > avg_volume * 5:
                    score += 40  # Massive volume spike
                elif recent_volume > avg_volume * 3:
                    score += 30  # High volume
                elif recent_volume > avg_volume * 2:
                    score += 20  # Above average volume
            
            # Price momentum (pink sheets can move fast)
            if len(close) >= 5:
                price_5d = ((current_price - close.iloc[-5]) / close.iloc[-5]) * 100
                if price_5d > 100:
                    score += 50  # 100%+ gain
                elif price_5d > 50:
                    score += 40  # 50%+ gain
                elif price_5d > 20:
                    score += 30  # 20%+ gain
                elif price_5d > 0:
                    score += 20  # Positive momentum
            
            # Volatility (high volatility = high opportunity for pink sheets)
            if len(close) >= 10:
                returns = close.pct_change().dropna()
                volatility = returns.std() * np.sqrt(252) * 100
                
                if volatility > 200:
                    score += 30  # Extreme volatility
                elif volatility > 100:
                    score += 25  # High volatility
                elif volatility > 50:
                    score += 20  # Moderate volatility
            
            # Technical indicators (simplified for pink sheets)
            if len(close) >= 10:
                sma_5 = close.rolling(window=5).mean().iloc[-1]
                sma_10 = close.rolling(window=10).mean().iloc[-1]
                
                if current_price > sma_5 > sma_10:
                    score += 25  # Bullish trend
                elif current_price > sma_5:
                    score += 15  # Short-term bullish
            
            # Sector bonuses
            category = self.get_symbol_category(symbol)
            sector_bonuses = {
                'CANNABIS_HEMP': 25,     # Hot sector
                'MINING_RESOURCES': 20,  # Commodity play
                'TECH_INNOVATION': 20,   # Growth potential
                'ENERGY_CLEANTECH': 15,  # Clean energy trend
                'BIOTECH_MEDICAL': 15    # Biotech potential
            }
            score += sector_bonuses.get(category, 10)
            
            # Recent breakout detection
            if len(close) >= 20:
                recent_high = close.iloc[-5:].max()
                period_high = close.iloc[-20:].max()
                
                if recent_high >= period_high * 0.95:  # Near recent highs
                    score += 20
            
            return min(score, 250)  # Cap at 250 for extreme opportunities
            
        except Exception as e:
            logger.error(f"Error scoring {symbol}: {e}")
            return 50
    
    def get_symbol_category(self, symbol):
        """Get category for symbol"""
        for category, symbols in self.pink_sheet_universe.items():
            if symbol in symbols:
                return category
        return 'OTHER'
    
    def analyze_pink_sheet(self, symbol):
        """Analyze individual pink sheet"""
        data, variant = self.get_pink_sheet_data(symbol)
        if data is None:
            return None
        
        try:
            current_price = data['Close'].iloc[-1]
            volume = data['Volume'].iloc[-1]
            score = self.calculate_pink_sheet_score(symbol, data, variant)
            category = self.get_symbol_category(symbol)
            
            # Price changes
            price_changes = {}
            if len(data) >= 2:
                price_changes['1d'] = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            if len(data) >= 5:
                price_changes['5d'] = ((current_price - data['Close'].iloc[-5]) / data['Close'].iloc[-5]) * 100
            
            return {
                'symbol': symbol,
                'variant': variant,
                'price': round(current_price, 6),  # High precision for sub-penny
                'volume': int(volume),
                'score': round(score, 1),
                'category': category,
                'price_change_1d': round(price_changes.get('1d', 0), 2),
                'price_change_5d': round(price_changes.get('5d', 0), 2),
                'risk_level': 'EXTREME' if current_price < 0.01 else 'VERY HIGH',
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def run_daily_analysis(self):
        """Run daily pink sheet analysis"""
        logger.info("🚀 Starting daily pink sheet analysis...")
        
        all_symbols = self.get_all_pink_sheets()
        results = []
        
        logger.info(f"📊 Analyzing {len(all_symbols)} pink sheet stocks...")
        
        for symbol in all_symbols:
            result = self.analyze_pink_sheet(symbol)
            if result:
                results.append(result)
                logger.info(f"   ✓ {symbol}: ${result['price']:.6f} - Score: {result['score']}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"✅ Analysis complete: {len(results)} stocks analyzed")
        return results
    
    def load_portfolio(self):
        """Load current portfolio"""
        try:
            if self.portfolio_file.exists():
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
            return {'holdings': {}, 'cash': self.daily_investment, 'total_invested': 0}
        except Exception as e:
            logger.error(f"Error loading portfolio: {e}")
            return {'holdings': {}, 'cash': self.daily_investment, 'total_invested': 0}
    
    def save_portfolio(self, portfolio):
        """Save portfolio"""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(portfolio, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving portfolio: {e}")
    
    def execute_buy_order(self, symbol, price, allocation, score, category):
        """Execute simulated buy order"""
        shares = allocation / price
        
        transaction = {
            'id': f"buy_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'symbol': symbol,
            'action': 'BUY',
            'shares': shares,
            'price': price,
            'amount': allocation,
            'score': score,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'stop_loss_price': price * (1 + self.stop_loss_pct / 100),
            'take_profit_price': price * (1 + self.take_profit_pct / 100),
            'max_hold_date': (datetime.now() + timedelta(days=self.max_holding_days)).isoformat()
        }
        
        logger.info(f"🟢 BUY: {shares:.2f} shares of {symbol} at ${price:.6f} = ${allocation:.2f}")
        return transaction
    
    def execute_sell_order(self, holding, current_price, reason):
        """Execute simulated sell order"""
        shares = holding['shares']
        amount = shares * current_price
        profit_loss = amount - holding['cost_basis']
        profit_pct = (profit_loss / holding['cost_basis']) * 100
        
        transaction = {
            'id': f"sell_{holding['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'symbol': holding['symbol'],
            'action': 'SELL',
            'shares': shares,
            'price': current_price,
            'amount': amount,
            'profit_loss': profit_loss,
            'profit_pct': profit_pct,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'hold_days': (datetime.now() - datetime.fromisoformat(holding['purchase_date'])).days
        }
        
        logger.info(f"🔴 SELL: {shares:.2f} shares of {holding['symbol']} at ${current_price:.6f} = ${amount:.2f} ({profit_pct:+.1f}%)")
        return transaction
    
    def check_exit_conditions(self, portfolio):
        """Check if any holdings should be sold"""
        sells = []
        
        for symbol, holding in portfolio['holdings'].items():
            # Get current price
            data, variant = self.get_pink_sheet_data(symbol, period="5d")
            if data is None:
                continue
            
            current_price = data['Close'].iloc[-1]
            purchase_price = holding['avg_price']
            
            # Check stop loss
            if current_price <= purchase_price * (1 + self.stop_loss_pct / 100):
                sells.append((symbol, holding, current_price, "STOP_LOSS"))
                continue
            
            # Check take profit
            if current_price >= purchase_price * (1 + self.take_profit_pct / 100):
                sells.append((symbol, holding, current_price, "TAKE_PROFIT"))
                continue
            
            # Check max hold time
            purchase_date = datetime.fromisoformat(holding['purchase_date'])
            if datetime.now() > purchase_date + timedelta(days=self.max_holding_days):
                sells.append((symbol, holding, current_price, "MAX_HOLD_TIME"))
                continue
        
        return sells
    
    def execute_daily_trades(self, analysis_results):
        """Execute daily automated trades"""
        logger.info("💼 Executing daily trades...")
        
        portfolio = self.load_portfolio()
        transactions = []
        
        # Check for sells first
        sells = self.check_exit_conditions(portfolio)
        for symbol, holding, current_price, reason in sells:
            sell_transaction = self.execute_sell_order(holding, current_price, reason)
            transactions.append(sell_transaction)
            
            # Add proceeds to cash
            portfolio['cash'] += sell_transaction['amount']
            
            # Remove from holdings
            del portfolio['holdings'][symbol]
        
        # Add daily investment
        portfolio['cash'] += self.daily_investment
        
        # Execute buys from top recommendations
        available_cash = portfolio['cash']
        top_picks = analysis_results[:3]  # Top 3 picks
        
        if available_cash > 5 and top_picks:  # Minimum $5 to trade
            # Allocate cash among top picks
            allocations = [
                available_cash * 0.50,  # 50% to top pick
                available_cash * 0.30,  # 30% to second pick
                available_cash * 0.20   # 20% to third pick
            ]
            
            for i, (stock, allocation) in enumerate(zip(top_picks, allocations)):
                if allocation < 1:  # Skip tiny allocations
                    continue
                
                symbol = stock['symbol']
                price = stock['price']
                
                # Skip if already holding
                if symbol in portfolio['holdings']:
                    continue
                
                buy_transaction = self.execute_buy_order(
                    symbol, price, allocation, stock['score'], stock['category']
                )
                transactions.append(buy_transaction)
                
                # Add to holdings
                portfolio['holdings'][symbol] = {
                    'shares': buy_transaction['shares'],
                    'avg_price': price,
                    'cost_basis': allocation,
                    'purchase_date': datetime.now().isoformat(),
                    'category': stock['category']
                }
                
                # Deduct from cash
                portfolio['cash'] -= allocation
        
        # Save portfolio and transactions
        self.save_portfolio(portfolio)
        self.save_transactions(transactions)
        
        logger.info(f"✅ Daily trades complete: {len([t for t in transactions if t['action'] == 'BUY'])} buys, {len([t for t in transactions if t['action'] == 'SELL'])} sells")
        
        return portfolio, transactions
    
    def save_transactions(self, new_transactions):
        """Save transactions to file"""
        try:
            all_transactions = []
            if self.transactions_file.exists():
                with open(self.transactions_file, 'r') as f:
                    all_transactions = json.load(f)
            
            all_transactions.extend(new_transactions)
            
            with open(self.transactions_file, 'w') as f:
                json.dump(all_transactions, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving transactions: {e}")
    
    def calculate_performance(self, portfolio):
        """Calculate portfolio performance"""
        try:
            total_value = portfolio['cash']
            total_cost = 0
            
            # Calculate current value of holdings
            for symbol, holding in portfolio['holdings'].items():
                data, variant = self.get_pink_sheet_data(symbol, period="5d")
                if data is not None:
                    current_price = data['Close'].iloc[-1]
                    current_value = holding['shares'] * current_price
                    total_value += current_value
                    total_cost += holding['cost_basis']
            
            # Load transaction history for total invested calculation
            total_invested = portfolio.get('total_invested', 0)
            if self.transactions_file.exists():
                with open(self.transactions_file, 'r') as f:
                    transactions = json.load(f)
                
                buy_total = sum(t['amount'] for t in transactions if t['action'] == 'BUY')
                sell_total = sum(t['amount'] for t in transactions if t['action'] == 'SELL')
                total_invested = buy_total - sell_total + portfolio['cash'] - self.daily_investment
            
            performance = {
                'date': datetime.now().isoformat(),
                'total_value': round(total_value, 2),
                'total_invested': round(total_invested, 2),
                'total_return': round(total_value - total_invested, 2),
                'total_return_pct': round(((total_value - total_invested) / max(total_invested, 1)) * 100, 2),
                'cash': round(portfolio['cash'], 2),
                'holdings_count': len(portfolio['holdings']),
                'holdings_value': round(total_value - portfolio['cash'], 2)
            }
            
            return performance
            
        except Exception as e:
            logger.error(f"Error calculating performance: {e}")
            return {}
    
    def save_performance(self, performance):
        """Save daily performance"""
        try:
            all_performance = []
            if self.performance_file.exists():
                with open(self.performance_file, 'r') as f:
                    all_performance = json.load(f)
            
            all_performance.append(performance)
            
            with open(self.performance_file, 'w') as f:
                json.dump(all_performance, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving performance: {e}")
    
    def run_daily_automation(self):
        """Run complete daily automation"""
        start_time = datetime.now()
        logger.info(f"🤖 Starting daily automation at {start_time}")
        
        try:
            # 1. Run analysis
            analysis_results = self.run_daily_analysis()
            
            # 2. Execute trades
            portfolio, transactions = self.execute_daily_trades(analysis_results)
            
            # 3. Calculate performance
            performance = self.calculate_performance(portfolio)
            self.save_performance(performance)
            
            # 4. Log automation run
            automation_log = {
                'date': datetime.now().isoformat(),
                'runtime_minutes': (datetime.now() - start_time).total_seconds() / 60,
                'stocks_analyzed': len(analysis_results),
                'trades_executed': len(transactions),
                'portfolio_value': performance.get('total_value', 0),
                'top_picks': analysis_results[:5] if analysis_results else []
            }
            
            self.save_automation_log(automation_log)
            
            logger.info(f"✅ Daily automation complete in {automation_log['runtime_minutes']:.1f} minutes")
            logger.info(f"📊 Portfolio value: ${performance.get('total_value', 0):.2f}")
            
            return {
                'success': True,
                'analysis_results': analysis_results,
                'portfolio': portfolio,
                'performance': performance,
                'automation_log': automation_log
            }
            
        except Exception as e:
            logger.error(f"❌ Daily automation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def save_automation_log(self, log_entry):
        """Save automation log"""
        try:
            all_logs = []
            if self.automation_log.exists():
                with open(self.automation_log, 'r') as f:
                    all_logs = json.load(f)
            
            all_logs.append(log_entry)
            
            with open(self.automation_log, 'w') as f:
                json.dump(all_logs, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving automation log: {e}")

if __name__ == "__main__":
    engine = PinkSheetAutomationEngine()
    result = engine.run_daily_automation()
    
    if result['success']:
        print("\n🎉 PINK SHEET AUTOMATION SUCCESS!")
        print(f"✓ {len(result['analysis_results'])} stocks analyzed")
        print(f"✓ Portfolio value: ${result['performance'].get('total_value', 0):.2f}")
        print(f"✓ Return: {result['performance'].get('total_return_pct', 0):.2f}%")
    else:
        print(f"\n❌ Automation failed: {result['error']}")

