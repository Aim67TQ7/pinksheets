#!/usr/bin/env python3
"""
Portfolio Management System
Handles $100/day investment simulation with P&L tracking
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PortfolioManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.portfolio_file = self.data_dir / "portfolio.json"
        self.transactions_file = self.data_dir / "transactions.json"
        self.performance_file = self.data_dir / "performance.json"
        
        self.daily_investment = 20.0
        self.stop_loss_pct = -15.0
        self.take_profit_pct = 25.0
        self.max_holding_days = 30
        self.max_position_pct = 20.0
        
        self.portfolio = self._load_portfolio()
        self.transactions = self._load_transactions()
        self.performance = self._load_performance()
    
    def _load_portfolio(self):
        """Load current portfolio holdings"""
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                return json.load(f)
        return {
            'cash': 0.0,
            'total_invested': 0.0,
            'holdings': {},
            'last_update': None
        }
    
    def _save_portfolio(self):
        """Save portfolio to file"""
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.portfolio, f, indent=2)
    
    def _load_transactions(self):
        """Load transaction history"""
        if self.transactions_file.exists():
            with open(self.transactions_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_transactions(self):
        """Save transactions to file"""
        with open(self.transactions_file, 'w') as f:
            json.dump(self.transactions, f, indent=2)
    
    def _load_performance(self):
        """Load performance history"""
        if self.performance_file.exists():
            with open(self.performance_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_performance(self):
        """Save performance to file"""
        with open(self.performance_file, 'w') as f:
            json.dump(self.performance, f, indent=2)
    
    def add_transaction(self, transaction_type, symbol, shares, price, date=None):
        """Add a transaction to the history"""
        if date is None:
            date = datetime.now().isoformat()
        
        transaction = {
            'date': date,
            'type': transaction_type,  # 'buy' or 'sell'
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'total': shares * price
        }
        
        self.transactions.append(transaction)
        self._save_transactions()
        
        logger.info(f"Added transaction: {transaction_type} {shares} shares of {symbol} at ${price}")
    
    def buy_stock(self, symbol, price, amount=None):
        """Buy stock with specified amount or remaining daily budget"""
        if amount is None:
            amount = self.daily_investment
        
        # Check if we have enough cash
        if self.portfolio['cash'] < amount:
            logger.warning(f"Insufficient cash to buy {symbol}. Available: ${self.portfolio['cash']:.2f}")
            return False
        
        shares = amount / price
        
        # Add to holdings
        if symbol not in self.portfolio['holdings']:
            self.portfolio['holdings'][symbol] = {
                'shares': 0,
                'avg_price': 0,
                'purchase_date': datetime.now().isoformat(),
                'total_cost': 0
            }
        
        holding = self.portfolio['holdings'][symbol]
        
        # Update average price
        total_shares = holding['shares'] + shares
        total_cost = holding['total_cost'] + amount
        holding['avg_price'] = total_cost / total_shares
        holding['shares'] = total_shares
        holding['total_cost'] = total_cost
        
        # Update cash
        self.portfolio['cash'] -= amount
        self.portfolio['total_invested'] += amount
        
        # Add transaction
        self.add_transaction('buy', symbol, shares, price)
        
        self._save_portfolio()
        
        logger.info(f"Bought {shares:.4f} shares of {symbol} at ${price:.2f} for ${amount:.2f}")
        return True
    
    def sell_stock(self, symbol, price, shares=None):
        """Sell stock (all shares if shares not specified)"""
        if symbol not in self.portfolio['holdings']:
            logger.warning(f"No holdings found for {symbol}")
            return False
        
        holding = self.portfolio['holdings'][symbol]
        
        if shares is None:
            shares = holding['shares']
        
        if shares > holding['shares']:
            logger.warning(f"Cannot sell {shares} shares of {symbol}. Only have {holding['shares']}")
            return False
        
        sale_amount = shares * price
        
        # Update holdings
        holding['shares'] -= shares
        holding['total_cost'] -= (shares * holding['avg_price'])
        
        # Remove holding if no shares left
        if holding['shares'] <= 0:
            del self.portfolio['holdings'][symbol]
        
        # Update cash
        self.portfolio['cash'] += sale_amount
        
        # Add transaction
        self.add_transaction('sell', symbol, shares, price)
        
        self._save_portfolio()
        
        logger.info(f"Sold {shares:.4f} shares of {symbol} at ${price:.2f} for ${sale_amount:.2f}")
        return True
    
    def check_stop_loss_take_profit(self, current_prices):
        """Check holdings for stop loss and take profit triggers"""
        sales_made = []
        
        for symbol, holding in list(self.portfolio['holdings'].items()):
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            avg_price = holding['avg_price']
            
            # Calculate percentage change
            pct_change = ((current_price - avg_price) / avg_price) * 100
            
            # Check stop loss
            if pct_change <= self.stop_loss_pct:
                logger.info(f"Stop loss triggered for {symbol}: {pct_change:.2f}%")
                if self.sell_stock(symbol, current_price):
                    sales_made.append({
                        'symbol': symbol,
                        'reason': 'stop_loss',
                        'pct_change': pct_change,
                        'price': current_price
                    })
            
            # Check take profit
            elif pct_change >= self.take_profit_pct:
                logger.info(f"Take profit triggered for {symbol}: {pct_change:.2f}%")
                if self.sell_stock(symbol, current_price):
                    sales_made.append({
                        'symbol': symbol,
                        'reason': 'take_profit',
                        'pct_change': pct_change,
                        'price': current_price
                    })
            
            # Check max holding period
            else:
                purchase_date = datetime.fromisoformat(holding['purchase_date'])
                days_held = (datetime.now() - purchase_date).days
                
                if days_held >= self.max_holding_days:
                    logger.info(f"Max holding period reached for {symbol}: {days_held} days")
                    if self.sell_stock(symbol, current_price):
                        sales_made.append({
                            'symbol': symbol,
                            'reason': 'max_holding_period',
                            'pct_change': pct_change,
                            'price': current_price
                        })
        
        return sales_made
    
    def make_daily_investments(self, top_stocks, current_prices):
        """Make daily investments in top-ranked stocks"""
        # Add daily cash
        self.portfolio['cash'] += self.daily_investment
        
        # Check for sales first
        sales = self.check_stop_loss_take_profit(current_prices)
        
        # Calculate current portfolio value for position sizing
        portfolio_value = self.calculate_portfolio_value(current_prices)
        
        purchases_made = []
        remaining_cash = min(self.portfolio['cash'], self.daily_investment)
        
        # Limit to top 3 stocks for diversification
        investment_candidates = top_stocks[:3]
        
        for i, stock in enumerate(investment_candidates):
            if remaining_cash <= 0:
                break
            
            symbol = stock['symbol']
            price = stock['current_price']
            
            # Check if we already have too much of this stock
            if symbol in self.portfolio['holdings']:
                holding_value = self.portfolio['holdings'][symbol]['shares'] * price
                position_pct = (holding_value / portfolio_value) * 100 if portfolio_value > 0 else 0
                
                if position_pct >= self.max_position_pct:
                    logger.info(f"Skipping {symbol} - position too large: {position_pct:.1f}%")
                    continue
            
            # Calculate investment amount (split remaining cash among remaining candidates)
            remaining_candidates = len(investment_candidates) - i
            investment_amount = min(remaining_cash / remaining_candidates, remaining_cash)
            
            if investment_amount >= 10:  # Minimum $10 investment
                if self.buy_stock(symbol, price, investment_amount):
                    purchases_made.append({
                        'symbol': symbol,
                        'amount': investment_amount,
                        'price': price,
                        'shares': investment_amount / price
                    })
                    remaining_cash -= investment_amount
        
        return purchases_made, sales
    
    def calculate_portfolio_value(self, current_prices):
        """Calculate current portfolio value"""
        total_value = self.portfolio['cash']
        
        for symbol, holding in self.portfolio['holdings'].items():
            if symbol in current_prices:
                total_value += holding['shares'] * current_prices[symbol]
            else:
                # Use average price if current price not available
                total_value += holding['shares'] * holding['avg_price']
        
        return total_value
    
    def calculate_daily_pnl(self, current_prices):
        """Calculate daily P&L"""
        current_value = self.calculate_portfolio_value(current_prices)
        
        # Get yesterday's value from performance history
        yesterday_value = current_value
        if self.performance:
            yesterday_value = self.performance[-1].get('total_value', current_value)
        
        daily_pnl = current_value - yesterday_value
        daily_return = (daily_pnl / yesterday_value * 100) if yesterday_value > 0 else 0
        
        # Calculate total P&L
        total_pnl = current_value - self.portfolio['total_invested']
        total_return = (total_pnl / self.portfolio['total_invested'] * 100) if self.portfolio['total_invested'] > 0 else 0
        
        return {
            'current_value': current_value,
            'daily_pnl': daily_pnl,
            'daily_return': daily_return,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'cash': self.portfolio['cash'],
            'invested': self.portfolio['total_invested']
        }
    
    def update_performance(self, current_prices, benchmark_return=0):
        """Update daily performance metrics"""
        pnl = self.calculate_daily_pnl(current_prices)
        
        performance_entry = {
            'date': datetime.now().isoformat(),
            'total_value': pnl['current_value'],
            'cash': pnl['cash'],
            'invested': pnl['invested'],
            'daily_pnl': pnl['daily_pnl'],
            'daily_return': pnl['daily_return'],
            'total_pnl': pnl['total_pnl'],
            'total_return': pnl['total_return'],
            'benchmark_return': benchmark_return,
            'holdings_count': len(self.portfolio['holdings'])
        }
        
        self.performance.append(performance_entry)
        self._save_performance()
        
        # Update portfolio last update time
        self.portfolio['last_update'] = datetime.now().isoformat()
        self._save_portfolio()
        
        return performance_entry
    
    def get_holdings_summary(self, current_prices):
        """Get summary of current holdings"""
        holdings_summary = []
        
        for symbol, holding in self.portfolio['holdings'].items():
            current_price = current_prices.get(symbol, holding['avg_price'])
            current_value = holding['shares'] * current_price
            cost_basis = holding['total_cost']
            pnl = current_value - cost_basis
            pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            purchase_date = datetime.fromisoformat(holding['purchase_date'])
            days_held = (datetime.now() - purchase_date).days
            
            holdings_summary.append({
                'symbol': symbol,
                'shares': holding['shares'],
                'avg_price': holding['avg_price'],
                'current_price': current_price,
                'cost_basis': cost_basis,
                'current_value': current_value,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'days_held': days_held,
                'purchase_date': holding['purchase_date']
            })
        
        return sorted(holdings_summary, key=lambda x: x['current_value'], reverse=True)
    
    def get_recent_transactions(self, days=7):
        """Get recent transactions"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent = []
        for transaction in reversed(self.transactions):
            transaction_date = datetime.fromisoformat(transaction['date'])
            if transaction_date >= cutoff_date:
                recent.append(transaction)
            else:
                break
        
        return recent

def main():
    """Test the portfolio manager"""
    portfolio = PortfolioManager()
    
    # Test data
    test_stocks = [
        {'symbol': 'AAPL', 'current_price': 150.0, 'composite_score': 85},
        {'symbol': 'MSFT', 'current_price': 300.0, 'composite_score': 80},
        {'symbol': 'GOOGL', 'current_price': 2500.0, 'composite_score': 75}
    ]
    
    current_prices = {stock['symbol']: stock['current_price'] for stock in test_stocks}
    
    print("Testing Portfolio Manager...")
    print("=" * 50)
    
    # Make daily investments
    purchases, sales = portfolio.make_daily_investments(test_stocks, current_prices)
    
    print(f"Purchases made: {len(purchases)}")
    for purchase in purchases:
        print(f"  Bought {purchase['shares']:.4f} shares of {purchase['symbol']} at ${purchase['price']:.2f}")
    
    print(f"Sales made: {len(sales)}")
    for sale in sales:
        print(f"  Sold {sale['symbol']} - {sale['reason']}: {sale['pnl_pct']:.2f}%")
    
    # Update performance
    performance = portfolio.update_performance(current_prices)
    print(f"\nPortfolio Performance:")
    print(f"  Total Value: ${performance['total_value']:.2f}")
    print(f"  Daily P&L: ${performance['daily_pnl']:.2f} ({performance['daily_return']:.2f}%)")
    print(f"  Total P&L: ${performance['total_pnl']:.2f} ({performance['total_return']:.2f}%)")
    
    # Show holdings
    holdings = portfolio.get_holdings_summary(current_prices)
    print(f"\nCurrent Holdings ({len(holdings)}):")
    for holding in holdings:
        print(f"  {holding['symbol']}: {holding['shares']:.4f} shares, ${holding['current_value']:.2f} value, {holding['pnl_pct']:.2f}% P&L")

if __name__ == "__main__":
    main()

