#!/usr/bin/env python3
"""
Website Data Generator for Pink Sheet Automation
Converts automation results to website-ready format
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def generate_website_data():
    """Generate website data from automation results"""
    
    data_dir = Path("data")
    
    # Load automation results
    portfolio_file = data_dir / "pink_portfolio.json"
    performance_file = data_dir / "pink_performance.json"
    transactions_file = data_dir / "pink_transactions.json"
    automation_log = data_dir / "automation_log.json"
    
    # Default values
    portfolio = {'holdings': {}, 'cash': 20.0}
    performance_history = []
    transactions = []
    latest_log = {}
    
    # Load data if files exist
    try:
        if portfolio_file.exists():
            with open(portfolio_file, 'r') as f:
                portfolio = json.load(f)
                
        if performance_file.exists():
            with open(performance_file, 'r') as f:
                performance_history = json.load(f)
                
        if transactions_file.exists():
            with open(transactions_file, 'r') as f:
                transactions = json.load(f)
                
        if automation_log.exists():
            with open(automation_log, 'r') as f:
                logs = json.load(f)
                if logs:
                    latest_log = logs[-1]
                    
    except Exception as e:
        print(f"Error loading data: {e}")
    
    # Get latest performance
    latest_performance = performance_history[-1] if performance_history else {
        'total_value': 20.0,
        'total_invested': 20.0,
        'total_return': 0.0,
        'total_return_pct': 0.0,
        'cash': 20.0,
        'holdings_value': 0.0
    }
    
    # Get recent transactions for pending trades display
    recent_transactions = [t for t in transactions if t.get('action') == 'BUY'][-3:] if transactions else []
    
    # Format holdings
    formatted_holdings = []
    for symbol, holding in portfolio.get('holdings', {}).items():
        # Calculate current value (would need real-time price)
        current_value = holding['cost_basis']  # Simplified for demo
        profit_loss = current_value - holding['cost_basis']
        profit_pct = (profit_loss / holding['cost_basis']) * 100 if holding['cost_basis'] > 0 else 0
        
        formatted_holdings.append({
            'symbol': symbol,
            'name': get_company_name(symbol),
            'shares': round(holding['shares'], 4),
            'avgPrice': round(holding['avg_price'], 6),
            'currentPrice': round(holding['avg_price'] * 1.05, 6),  # Mock 5% gain
            'value': round(current_value, 2),
            'profitLoss': round(profit_loss, 2),
            'profitLossPct': round(profit_pct, 2),
            'category': holding.get('category', 'PINK_SHEETS')
        })
    
    # Format top recommendations from latest log
    top_stocks = []
    if latest_log.get('top_picks'):
        for i, stock in enumerate(latest_log['top_picks'], 1):
            top_stocks.append({
                'rank': i,
                'symbol': stock['symbol'],
                'name': get_company_name(stock['symbol']),
                'price': stock['price'],
                'score': stock['score'],
                'priceChange5d': stock.get('price_change_5d', 0),
                'category': stock['category'].replace('_', ' ').title(),
                'recommendation': get_recommendation(stock['score']),
                'risk_level': stock.get('risk_level', 'EXTREME')
            })
    
    # Create pending trades (next day's potential trades)
    pending_trades = []
    if top_stocks[:3]:  # Top 3 for next day
        available_cash = portfolio.get('cash', 20.0) + 20.0  # Today's cash + tomorrow's $20
        allocations = [available_cash * 0.5, available_cash * 0.3, available_cash * 0.2]
        
        for i, (stock, allocation) in enumerate(zip(top_stocks[:3], allocations)):
            shares = allocation / stock['price']
            pending_trades.append({
                'id': f"pending_{datetime.now().strftime('%Y%m%d')}_{i+1}",
                'symbol': stock['symbol'],
                'name': stock['name'],
                'action': 'BUY',
                'price': stock['price'],
                'shares': round(shares, 4),
                'allocation': round(allocation, 2),
                'score': stock['score'],
                'sector': stock['category'],
                'reasoning': generate_reasoning(stock),
                'status': 'PENDING',
                'risk_level': stock['risk_level']
            })
    
    # Calculate performance metrics
    daily_pnl = 0
    daily_return = 0
    if len(performance_history) >= 2:
        today_value = performance_history[-1]['total_value']
        yesterday_value = performance_history[-2]['total_value']
        daily_pnl = today_value - yesterday_value
        daily_return = (daily_pnl / yesterday_value) * 100 if yesterday_value > 0 else 0
    
    # Create website data structure
    website_data = {
        'timestamp': datetime.now().isoformat(),
        'portfolioSummary': {
            'totalValue': round(latest_performance['total_value'], 2),
            'dailyPnL': round(daily_pnl, 2),
            'dailyReturn': round(daily_return, 2),
            'totalPnL': round(latest_performance['total_return'], 2),
            'totalReturn': round(latest_performance['total_return_pct'], 2),
            'cash': round(latest_performance['cash'], 2),
            'invested': round(latest_performance['holdings_value'], 2),
            'sellProceeds': round(max(0, latest_performance['cash'] - 20.0), 2)
        },
        'pendingTrades': pending_trades,
        'topStocks': top_stocks,
        'holdings': formatted_holdings,
        'marketSummary': {
            'sp500': '+0.75%',
            'nasdaq': '+1.20%', 
            'dow': '+0.45%',
            'vix': '18.5'
        },
        'analysisStats': {
            'totalStocksAnalyzed': latest_log.get('stocks_analyzed', 0),
            'sectorsAnalyzed': 5,  # Pink sheet categories
            'highGrowthStocks': latest_log.get('stocks_analyzed', 0),
            'emergingTechStocks': 14,
            'pinkSheetStocks': latest_log.get('stocks_analyzed', 0)
        },
        'automationStatus': {
            'lastRun': latest_log.get('date', datetime.now().isoformat()),
            'runtime': round(latest_log.get('runtime_minutes', 0), 1),
            'tradesExecuted': latest_log.get('trades_executed', 0),
            'status': 'SUCCESS' if latest_log else 'PENDING'
        }
    }
    
    # Save website data
    output_file = data_dir / "website_data.json"
    with open(output_file, 'w') as f:
        json.dump(website_data, f, indent=2)
    
    print(f"✅ Website data generated: {output_file}")
    print(f"📊 Portfolio value: ${website_data['portfolioSummary']['totalValue']}")
    print(f"💰 Total return: {website_data['portfolioSummary']['totalReturn']:.2f}%")
    print(f"🎯 Pending trades: {len(pending_trades)}")
    
    return website_data

def get_company_name(symbol):
    """Get company name for symbol"""
    company_names = {
        # Cannabis/Hemp
        'CBDD': 'CBDD Inc.',
        'MJNA': 'Medical Marijuana Inc.',
        'HEMP': 'Hemp Inc.',
        'GRNH': 'Greengro Technologies',
        'TRTC': 'Terra Tech Corp.',
        'MCOA': 'MCOA Inc.',
        'ERBB': 'American Green Inc.',
        
        # Mining/Resources
        'GORO': 'Gold Resource Corporation',
        'LODE': 'Comstock Mining Inc.',
        'GLDG': 'GoldMining Inc.',
        'SILV': 'SilverCrest Metals',
        'HYMC': 'Hycroft Mining',
        
        # Tech/Innovation
        'HMBL': 'Humbl Inc.',
        'OZSC': 'Ozop Surgical Corp.',
        'AITX': 'Artificial Intelligence Technology Solutions',
        'ABML': 'American Battery Technology',
        'ALPP': 'Alpine 4 Holdings',
        
        # Energy/CleanTech
        'OPTI': 'Optec International',
        'EEENF': 'Emerald Energy NL',
        'PVDG': 'PVD Global',
        'RECO': 'Reconnaissance Energy Africa',
        'SIRC': 'Solar Integrated Roofing Corp.',
        
        # Biotech/Medical
        'BVTK': 'Bovie Medical Corporation',
        'RLFTF': 'Relief Therapeutics',
        'CYDY': 'CytoDyn Inc.',
        'ENZC': 'Enzolytics Inc.',
        'BIEL': 'BioElectronics Corporation'
    }
    
    return company_names.get(symbol, f"{symbol} Corporation")

def generate_reasoning(stock):
    """Generate reasoning for stock recommendation"""
    reasons = []
    
    if stock['score'] > 200:
        reasons.append("Exceptional pink sheet opportunity")
    elif stock['score'] > 150:
        reasons.append("High-scoring pink sheet pick")
    
    if stock['price'] < 0.01:
        reasons.append("Sub-penny stock with extreme upside")
    elif stock['price'] < 0.10:
        reasons.append("Dime stock with high potential")
    
    if stock.get('priceChange5d', 0) > 0:
        reasons.append("Positive momentum")
    
    category = stock['category'].lower()
    if 'cannabis' in category:
        reasons.append("Cannabis sector opportunity")
    elif 'mining' in category:
        reasons.append("Mining/resources play")
    elif 'tech' in category:
        reasons.append("Technology innovation")
    elif 'energy' in category:
        reasons.append("Clean energy potential")
    elif 'biotech' in category:
        reasons.append("Biotech breakthrough potential")
    
    return "; ".join(reasons) if reasons else "Pink sheet high-risk/high-reward opportunity"

def get_recommendation(score):
    """Get recommendation based on score"""
    if score >= 200:
        return "Extreme Buy"
    elif score >= 150:
        return "Strong Buy"
    elif score >= 120:
        return "Buy"
    elif score >= 100:
        return "Moderate Buy"
    else:
        return "Watch"

if __name__ == "__main__":
    website_data = generate_website_data()
    print("\n🚀 Website data ready for deployment!")

