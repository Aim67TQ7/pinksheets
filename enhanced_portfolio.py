#!/usr/bin/env python3
"""
Enhanced Portfolio Manager with Interactive Trading
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging

class EnhancedPortfolioManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.portfolio_file = self.data_dir / "portfolio.json"
        self.transactions_file = self.data_dir / "transactions.json"
        self.pending_trades_file = self.data_dir / "pending_trades.json"
        self.cash_file = self.data_dir / "cash_balance.json"
        
        # Trading parameters
        self.base_daily_investment = 20.0
        self.stop_loss_pct = -15.0
        self.take_profit_pct = 25.0
        self.max_holding_days = 30
        self.max_position_pct = 20.0
        
        self.logger = logging.getLogger(__name__)
    
    def get_available_cash(self):
        """Get total available cash for today's investment"""
        try:
            if self.cash_file.exists():
                with open(self.cash_file, 'r') as f:
                    cash_data = json.load(f)
                return cash_data.get('available_cash', self.base_daily_investment)
            else:
                return self.base_daily_investment
        except Exception as e:
            self.logger.error(f"Error reading cash balance: {e}")
            return self.base_daily_investment
    
    def update_cash_balance(self, amount, transaction_type="daily_add"):
        """Update available cash balance"""
        try:
            current_cash = self.get_available_cash()
            
            if transaction_type == "daily_add":
                new_cash = current_cash + amount
            elif transaction_type == "sell":
                new_cash = current_cash + amount
            elif transaction_type == "buy":
                new_cash = current_cash - amount
            else:
                new_cash = current_cash
            
            cash_data = {
                'available_cash': new_cash,
                'last_updated': datetime.now().isoformat(),
                'base_daily': self.base_daily_investment
            }
            
            with open(self.cash_file, 'w') as f:
                json.dump(cash_data, f, indent=2)
            
            return new_cash
        except Exception as e:
            self.logger.error(f"Error updating cash balance: {e}")
            return self.base_daily_investment
    
    def create_pending_trades(self, recommendations):
        """Create pending trades for user approval"""
        available_cash = self.get_available_cash()
        
        # Select top 3 stocks for investment
        top_stocks = recommendations[:3]
        
        # Allocate cash (can be more than $20 if we have sell proceeds)
        if available_cash <= 25:
            allocations = [available_cash * 0.35, available_cash * 0.35, available_cash * 0.30]
        else:
            # For larger amounts, use percentage-based allocation
            allocations = [available_cash * 0.40, available_cash * 0.35, available_cash * 0.25]
        
        pending_trades = []
        total_allocated = 0
        
        for i, (stock, allocation) in enumerate(zip(top_stocks, allocations)):
            if allocation < 1.0:  # Skip very small allocations
                continue
                
            shares = allocation / stock['price']
            total_allocated += allocation
            
            trade = {
                'id': f"trade_{datetime.now().strftime('%Y%m%d')}_{i+1}",
                'symbol': stock['symbol'],
                'action': 'BUY',
                'shares': round(shares, 6),
                'price': stock['price'],
                'allocation': round(allocation, 2),
                'score': stock['score'],
                'rsi': stock.get('rsi', 50),
                'reasoning': self.get_trade_reasoning(stock),
                'status': 'PENDING',
                'created_at': datetime.now().isoformat()
            }
            pending_trades.append(trade)
        
        # Save pending trades
        with open(self.pending_trades_file, 'w') as f:
            json.dump({
                'trades': pending_trades,
                'total_allocation': round(total_allocated, 2),
                'available_cash': available_cash,
                'remaining_cash': round(available_cash - total_allocated, 2),
                'created_at': datetime.now().isoformat()
            }, f, indent=2)
        
        return pending_trades, total_allocated
    
    def get_trade_reasoning(self, stock):
        """Generate reasoning for trade recommendation"""
        reasons = []
        
        if stock['score'] > 100:
            reasons.append("High composite score")
        
        rsi = stock.get('rsi', 50)
        if 30 <= rsi <= 70:
            reasons.append("RSI in optimal range")
        elif rsi < 30:
            reasons.append("Oversold condition - potential bounce")
        
        if stock.get('above_ma_20', False):
            reasons.append("Above 20-day moving average")
        
        price_change = stock.get('price_change_5d', 0)
        if 0 < price_change < 10:
            reasons.append("Positive momentum")
        
        return "; ".join(reasons) if reasons else "Technical analysis favorable"
    
    def approve_trade(self, trade_id):
        """Approve a pending trade"""
        try:
            if not self.pending_trades_file.exists():
                return False, "No pending trades found"
            
            with open(self.pending_trades_file, 'r') as f:
                pending_data = json.load(f)
            
            # Find the trade
            trade_found = None
            for trade in pending_data['trades']:
                if trade['id'] == trade_id:
                    trade_found = trade
                    break
            
            if not trade_found:
                return False, "Trade not found"
            
            # Execute the trade
            success = self.execute_trade(trade_found)
            
            if success:
                # Update trade status
                trade_found['status'] = 'APPROVED'
                trade_found['executed_at'] = datetime.now().isoformat()
                
                # Save updated pending trades
                with open(self.pending_trades_file, 'w') as f:
                    json.dump(pending_data, f, indent=2)
                
                return True, "Trade approved and executed"
            else:
                return False, "Failed to execute trade"
                
        except Exception as e:
            self.logger.error(f"Error approving trade: {e}")
            return False, f"Error: {e}"
    
    def reject_trade(self, trade_id):
        """Reject a pending trade"""
        try:
            if not self.pending_trades_file.exists():
                return False, "No pending trades found"
            
            with open(self.pending_trades_file, 'r') as f:
                pending_data = json.load(f)
            
            # Find and update the trade
            for trade in pending_data['trades']:
                if trade['id'] == trade_id:
                    trade['status'] = 'REJECTED'
                    trade['rejected_at'] = datetime.now().isoformat()
                    break
            
            # Save updated pending trades
            with open(self.pending_trades_file, 'w') as f:
                json.dump(pending_data, f, indent=2)
            
            return True, "Trade rejected"
            
        except Exception as e:
            self.logger.error(f"Error rejecting trade: {e}")
            return False, f"Error: {e}"
    
    def execute_trade(self, trade):
        """Execute an approved trade"""
        try:
            # Load current portfolio
            portfolio = self.load_portfolio()
            
            if trade['action'] == 'BUY':
                # Add to portfolio
                symbol = trade['symbol']
                if symbol in portfolio:
                    # Average down/up
                    current_shares = portfolio[symbol]['shares']
                    current_avg_price = portfolio[symbol]['avg_price']
                    new_shares = trade['shares']
                    new_price = trade['price']
                    
                    total_shares = current_shares + new_shares
                    total_cost = (current_shares * current_avg_price) + (new_shares * new_price)
                    new_avg_price = total_cost / total_shares
                    
                    portfolio[symbol].update({
                        'shares': total_shares,
                        'avg_price': new_avg_price,
                        'last_updated': datetime.now().isoformat()
                    })
                else:
                    # New position
                    portfolio[symbol] = {
                        'shares': trade['shares'],
                        'avg_price': trade['price'],
                        'purchase_date': datetime.now().isoformat(),
                        'last_updated': datetime.now().isoformat()
                    }
                
                # Update cash balance
                self.update_cash_balance(trade['allocation'], 'buy')
                
            # Save portfolio
            self.save_portfolio(portfolio)
            
            # Record transaction
            self.record_transaction(trade)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return False
    
    def load_portfolio(self):
        """Load current portfolio"""
        try:
            if self.portfolio_file.exists():
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading portfolio: {e}")
            return {}
    
    def save_portfolio(self, portfolio):
        """Save portfolio to file"""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(portfolio, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving portfolio: {e}")
    
    def record_transaction(self, trade):
        """Record transaction in history"""
        try:
            transactions = []
            if self.transactions_file.exists():
                with open(self.transactions_file, 'r') as f:
                    transactions = json.load(f)
            
            transaction = {
                'id': trade['id'],
                'symbol': trade['symbol'],
                'action': trade['action'],
                'shares': trade['shares'],
                'price': trade['price'],
                'amount': trade['allocation'],
                'timestamp': datetime.now().isoformat(),
                'reasoning': trade.get('reasoning', '')
            }
            
            transactions.append(transaction)
            
            with open(self.transactions_file, 'w') as f:
                json.dump(transactions, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error recording transaction: {e}")
    
    def get_pending_trades(self):
        """Get all pending trades"""
        try:
            if self.pending_trades_file.exists():
                with open(self.pending_trades_file, 'r') as f:
                    return json.load(f)
            return {'trades': [], 'total_allocation': 0, 'available_cash': self.base_daily_investment}
        except Exception as e:
            self.logger.error(f"Error loading pending trades: {e}")
            return {'trades': [], 'total_allocation': 0, 'available_cash': self.base_daily_investment}

if __name__ == "__main__":
    # Test the enhanced portfolio manager
    pm = EnhancedPortfolioManager()
    print(f"Available cash: ${pm.get_available_cash():.2f}")
    
    # Add daily investment
    pm.update_cash_balance(20.0, 'daily_add')
    print(f"After daily add: ${pm.get_available_cash():.2f}")
    
    # Simulate a sell
    pm.update_cash_balance(8.50, 'sell')
    print(f"After sell proceeds: ${pm.get_available_cash():.2f}")

