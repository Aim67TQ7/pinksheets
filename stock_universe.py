#!/usr/bin/env python3
"""
Enhanced Stock Universe - 100+ stocks across market caps and sectors
"""

# Expanded stock universe for analysis
STOCK_UNIVERSE = {
    # Large Cap Tech Leaders
    'MEGA_TECH': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'NFLX', 'ADBE', 'CRM'],
    
    # Financial Sector
    'FINANCIALS': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'AXP', 'SCHW', 'USB'],
    
    # Healthcare & Biotech
    'HEALTHCARE': ['UNH', 'JNJ', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN'],
    
    # Consumer & Retail
    'CONSUMER': ['WMT', 'HD', 'PG', 'KO', 'PEP', 'COST', 'NKE', 'SBUX', 'MCD', 'DIS'],
    
    # Industrial & Energy
    'INDUSTRIAL': ['BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'RTX', 'LMT', 'DE', 'EMR'],
    'ENERGY': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'OXY', 'KMI'],
    
    # High Growth Mid-Caps
    'GROWTH_MIDCAP': ['PLTR', 'SNOW', 'CRWD', 'ZS', 'DDOG', 'NET', 'OKTA', 'TWLO', 'ZM', 'DOCU'],
    
    # Emerging Tech & Innovation
    'EMERGING_TECH': ['RBLX', 'U', 'PATH', 'COIN', 'HOOD', 'SOFI', 'UPST', 'AFRM', 'SQ', 'PYPL'],
    
    # Biotech & Pharma Growth
    'BIOTECH': ['MRNA', 'BNTX', 'GILD', 'BIIB', 'REGN', 'VRTX', 'ILMN', 'INCY', 'ALXN', 'CELG'],
    
    # Clean Energy & EV
    'CLEAN_ENERGY': ['ENPH', 'SEDG', 'FSLR', 'PLUG', 'BE', 'CHPT', 'LCID', 'RIVN', 'NIO', 'XPEV'],
    
    # Semiconductor Leaders
    'SEMICONDUCTORS': ['INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'MRVL', 'MCHP']
}

def get_all_stocks():
    """Get complete list of stocks to analyze"""
    all_stocks = []
    for sector, stocks in STOCK_UNIVERSE.items():
        all_stocks.extend(stocks)
    return list(set(all_stocks))  # Remove duplicates

def get_sector_allocation():
    """Get recommended sector allocation percentages"""
    return {
        'MEGA_TECH': 25,      # 25% in proven tech leaders
        'GROWTH_MIDCAP': 20,  # 20% in high-growth mid-caps
        'EMERGING_TECH': 15,  # 15% in emerging technologies
        'FINANCIALS': 10,     # 10% in financial sector
        'HEALTHCARE': 10,     # 10% in healthcare
        'SEMICONDUCTORS': 8,  # 8% in chip makers
        'CLEAN_ENERGY': 7,    # 7% in clean energy
        'CONSUMER': 3,        # 3% in consumer staples
        'BIOTECH': 2,         # 2% in biotech speculation
    }

def get_risk_categories():
    """Categorize stocks by risk level"""
    return {
        'LOW_RISK': STOCK_UNIVERSE['MEGA_TECH'] + STOCK_UNIVERSE['CONSUMER'][:5],
        'MEDIUM_RISK': STOCK_UNIVERSE['FINANCIALS'] + STOCK_UNIVERSE['HEALTHCARE'] + STOCK_UNIVERSE['SEMICONDUCTORS'],
        'HIGH_RISK': STOCK_UNIVERSE['GROWTH_MIDCAP'] + STOCK_UNIVERSE['EMERGING_TECH'] + STOCK_UNIVERSE['CLEAN_ENERGY'],
        'SPECULATIVE': STOCK_UNIVERSE['BIOTECH'][:5]
    }

if __name__ == "__main__":
    all_stocks = get_all_stocks()
    print(f"Total stocks in universe: {len(all_stocks)}")
    print(f"Sectors covered: {len(STOCK_UNIVERSE)}")
    
    for sector, stocks in STOCK_UNIVERSE.items():
        print(f"{sector}: {len(stocks)} stocks")

