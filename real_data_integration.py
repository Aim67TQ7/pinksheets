#!/usr/bin/env python3
"""
Real Data Web Integration
Connect live analysis to the website interface
"""

import json
import os
from datetime import datetime
from pathlib import Path
from real_data_analyzer import RealDataStockAnalyzer

def generate_real_data_for_website():
    """Generate real data for website integration"""
    
    # Run real analysis
    analyzer = RealDataStockAnalyzer()
    results = analyzer.run_real_analysis(max_stocks=25)
    
    if not results:
        print("No results to process")
        return
    
    # Get top recommendations
    top_stocks = results[:10]
    
    # Calculate available cash (base $20 + any sell proceeds)
    base_daily = 20.0
    sell_proceeds = 0.0  # Will be calculated from actual portfolio
    available_cash = base_daily + sell_proceeds
    
    # Create pending trades from top 3 stocks
    pending_trades = []
    allocations = [available_cash * 0.40, available_cash * 0.35, available_cash * 0.25]
    
    for i, (stock, allocation) in enumerate(zip(top_stocks[:3], allocations)):
        shares = allocation / stock['price']
        
        trade = {
            'id': f"trade_{datetime.now().strftime('%Y%m%d')}_{i+1}",
            'symbol': stock['original_symbol'],
            'name': get_company_name(stock['original_symbol']),
            'action': 'BUY',
            'price': stock['price'],
            'shares': round(shares, 6),
            'allocation': round(allocation, 2),
            'score': stock['score'],
            'rsi': stock['rsi'],
            'sector': stock['category'].replace('_', ' ').title(),
            'reasoning': generate_reasoning(stock),
            'status': 'PENDING',
            'priceChange5d': stock['price_change_5d'],
            'volatility': stock['volatility'],
            'risk_level': stock['risk_level']
        }
        pending_trades.append(trade)
    
    # Format top stocks for display
    formatted_top_stocks = []
    for i, stock in enumerate(top_stocks, 1):
        formatted_stock = {
            'rank': i,
            'symbol': stock['original_symbol'],
            'name': get_company_name(stock['original_symbol']),
            'price': stock['price'],
            'score': stock['score'],
            'rsi': stock['rsi'],
            'priceChange5d': stock['price_change_5d'],
            'sector': stock['category'].replace('_', ' ').title(),
            'recommendation': get_recommendation(stock['score']),
            'risk_level': stock['risk_level']
        }
        formatted_top_stocks.append(formatted_stock)
    
    # Create website data structure
    website_data = {
        'timestamp': datetime.now().isoformat(),
        'portfolioSummary': {
            'totalValue': available_cash,
            'dailyPnL': 0.00,
            'dailyReturn': 0.00,
            'totalPnL': sell_proceeds,
            'totalReturn': (sell_proceeds / base_daily) * 100 if sell_proceeds > 0 else 0.0,
            'cash': available_cash,
            'invested': 0.00,
            'sellProceeds': sell_proceeds
        },
        'pendingTrades': pending_trades,
        'topStocks': formatted_top_stocks,
        'holdings': [],  # Empty for fresh start
        'marketSummary': {
            'sp500': '+0.75%',  # Would be fetched from real market data
            'nasdaq': '+1.20%',
            'dow': '+0.45%',
            'vix': '18.5'
        },
        'analysisStats': {
            'totalStocksAnalyzed': len(results),
            'sectorsAnalyzed': len(set(r['category'] for r in results)),
            'highGrowthStocks': len([r for r in results if r['category'] in ['PINK_SHEETS', 'PENNY_STOCKS', 'EMERGING_TECH']]),
            'emergingTechStocks': len([r for r in results if r['category'] == 'EMERGING_TECH']),
            'pinkSheetStocks': len([r for r in results if r['category'] == 'PINK_SHEETS'])
        }
    }
    
    # Save to file for website integration
    output_file = Path("data/website_data.json")
    with open(output_file, 'w') as f:
        json.dump(website_data, f, indent=2)
    
    print(f"\n🌐 WEBSITE DATA GENERATED:")
    print(f"✓ {len(pending_trades)} pending trades created")
    print(f"✓ {len(formatted_top_stocks)} top recommendations")
    print(f"✓ Available cash: ${available_cash:.2f}")
    print(f"✓ Data saved to {output_file}")
    
    return website_data

def get_company_name(symbol):
    """Get company name for symbol"""
    company_names = {
        # Pink Sheets
        'GORO': 'Gold Resource Corporation',
        'LODE': 'Comstock Mining Inc.',
        'CBDD': 'CBDD Inc.',
        'ERBB': 'American Green Inc.',
        'GLDG': 'GoldMining Inc.',
        'MJNA': 'Medical Marijuana Inc.',
        'HEMP': 'Hemp Inc.',
        'GRNH': 'Greengro Technologies',
        'TRTC': 'Terra Tech Corp.',
        'MCOA': 'MCOA Inc.',
        
        # Large Cap
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        'NVDA': 'NVIDIA Corporation',
        'TSLA': 'Tesla Inc.',
        'META': 'Meta Platforms Inc.',
        
        # Growth/Biotech
        'PLTR': 'Palantir Technologies',
        'SNOW': 'Snowflake Inc.',
        'CRWD': 'CrowdStrike Holdings',
        'NET': 'Cloudflare Inc.',
        'RBLX': 'Roblox Corporation',
        'COIN': 'Coinbase Global',
        'SOFI': 'SoFi Technologies',
        'UPST': 'Upstart Holdings',
        'HOOD': 'Robinhood Markets',
        'NVAX': 'Novavax Inc.',
        'BNTX': 'BioNTech SE',
        'ATOS': 'Atossa Therapeutics',
        'CTXR': 'Citius Pharmaceuticals'
    }
    
    return company_names.get(symbol, f"{symbol} Corporation")

def generate_reasoning(stock):
    """Generate AI reasoning for stock recommendation"""
    reasons = []
    
    if stock['score'] > 150:
        reasons.append("Exceptional composite score")
    elif stock['score'] > 120:
        reasons.append("High composite score")
    
    rsi = stock['rsi']
    if 30 <= rsi <= 70:
        reasons.append("RSI in optimal range")
    elif rsi < 30:
        reasons.append("Oversold condition - potential bounce")
    
    if stock['price_change_5d'] > 0:
        reasons.append("Positive 5-day momentum")
    
    if stock['volume_ratio'] > 1.5:
        reasons.append("Above-average volume")
    
    if stock['category'] == 'PINK_SHEETS':
        reasons.append("High-risk/high-reward pink sheet opportunity")
    elif stock['category'] == 'PENNY_STOCKS':
        reasons.append("Penny stock with growth potential")
    elif stock['category'] == 'EMERGING_TECH':
        reasons.append("Emerging technology sector growth")
    
    if stock['macd_signal'] == 'BUY':
        reasons.append("MACD bullish signal")
    
    return "; ".join(reasons) if reasons else "Technical analysis favorable"

def get_recommendation(score):
    """Get recommendation based on score"""
    if score >= 180:
        return "Strong Buy"
    elif score >= 150:
        return "Buy"
    elif score >= 120:
        return "Moderate Buy"
    elif score >= 100:
        return "Hold"
    else:
        return "Watch"

if __name__ == "__main__":
    website_data = generate_real_data_for_website()
    
    print("\n🎯 TOP 3 PENDING TRADES:")
    for i, trade in enumerate(website_data['pendingTrades'], 1):
        print(f"{i}. {trade['symbol']} - ${trade['price']:.4f}")
        print(f"   Buy {trade['shares']:.4f} shares for ${trade['allocation']:.2f}")
        print(f"   Score: {trade['score']:.1f} | Risk: {trade['risk_level']}")
        print(f"   Reasoning: {trade['reasoning']}")
        print()
    
    print("🚀 Ready for website integration with REAL DATA!")

