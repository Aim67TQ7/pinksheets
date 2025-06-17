#!/usr/bin/env python3
"""
Main Daily Analysis Runner
Orchestrates the complete daily stock analysis and blog generation process
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from stock_analyzer import StockAnalyzer
from portfolio_manager import PortfolioManager
from blog_generator import BlogGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Run the complete daily analysis process"""
    try:
        logger.info("Starting daily stock analysis process...")
        
        # Initialize components
        analyzer = StockAnalyzer()
        portfolio = PortfolioManager()
        blog_generator = BlogGenerator()
        
        # Step 1: Analyze top stocks
        logger.info("Analyzing top stocks...")
        top_stocks = analyzer.get_top_stocks(limit=10)
        
        if not top_stocks:
            logger.error("No stocks analyzed successfully. Exiting.")
            return False
        
        logger.info(f"Successfully analyzed {len(top_stocks)} stocks")
        
        # Step 2: Get current prices for portfolio management
        current_prices = {stock['symbol']: stock['current_price'] for stock in top_stocks}
        
        # Add any existing holdings that might not be in top 10
        for symbol in portfolio.portfolio['holdings'].keys():
            if symbol not in current_prices:
                try:
                    stock_data = analyzer.get_stock_data(symbol, period='1d')
                    if stock_data and not stock_data['data'].empty:
                        current_prices[symbol] = float(stock_data['data']['Close'].iloc[-1])
                except Exception as e:
                    logger.warning(f"Could not get current price for {symbol}: {e}")
        
        # Step 3: Make daily investments and manage portfolio
        logger.info("Managing portfolio...")
        purchases, sales = portfolio.make_daily_investments(top_stocks, current_prices)
        
        logger.info(f"Made {len(purchases)} purchases and {len(sales)} sales")
        
        # Step 4: Update performance metrics
        performance_entry = portfolio.update_performance(current_prices)
        
        # Step 5: Get portfolio data for blog
        holdings_summary = portfolio.get_holdings_summary(current_prices)
        recent_transactions = portfolio.get_recent_transactions(days=1)
        
        # Add recent activity to portfolio data
        portfolio_data = type('obj', (object,), {
            'cash': portfolio.portfolio['cash'],
            'invested': portfolio.portfolio['total_invested'],
            'recent_purchases': purchases,
            'recent_sales': sales
        })
        
        # Step 6: Generate blog content
        logger.info("Generating blog content...")
        blog_file = blog_generator.generate_blog_post(
            top_stocks=top_stocks,
            portfolio_data=portfolio_data,
            performance_data=portfolio.performance,
            holdings_data=holdings_summary
        )
        
        # Step 7: Create HTML version
        html_file = blog_generator.create_html_page(blog_file)
        
        # Step 8: Update React app with real data (optional)
        update_react_data(top_stocks, portfolio_data, performance_entry, holdings_summary)
        
        logger.info("Daily analysis completed successfully!")
        logger.info(f"Blog generated: {blog_file}")
        logger.info(f"HTML page: {html_file}")
        logger.info(f"Portfolio value: ${performance_entry['current_value']:.2f}")
        logger.info(f"Daily P&L: ${performance_entry['daily_pnl']:.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in daily analysis: {e}")
        return False

def update_react_data(top_stocks, portfolio_data, performance_entry, holdings_summary):
    """Update React app with real data"""
    try:
        # Create a data file that the React app can import
        react_data = {
            'lastUpdated': datetime.now().isoformat(),
            'portfolioSummary': {
                'totalValue': performance_entry['current_value'],
                'dailyPnL': performance_entry['daily_pnl'],
                'dailyReturn': performance_entry['daily_return'],
                'totalPnL': performance_entry['total_pnl'],
                'totalReturn': performance_entry['total_return'],
                'cash': portfolio_data.cash,
                'invested': portfolio_data.invested
            },
            'topStocks': top_stocks[:10],
            'holdings': holdings_summary,
            'recentPurchases': portfolio_data.recent_purchases,
            'recentSales': portfolio_data.recent_sales
        }
        
        # Save to React app's public directory
        react_app_dir = Path(__file__).parent / "stock-analysis-website" / "public"
        if react_app_dir.exists():
            with open(react_app_dir / "data.json", 'w') as f:
                import json
                json.dump(react_data, f, indent=2, default=str)
            logger.info("Updated React app data")
        
    except Exception as e:
        logger.warning(f"Could not update React data: {e}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

