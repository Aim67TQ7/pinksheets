#!/usr/bin/env python3
"""
Blog Content Generator
Creates daily stock analysis blog posts with recommendations and portfolio updates
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)

class BlogGenerator:
    def __init__(self, output_dir="public"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "assets").mkdir(exist_ok=True)
        (self.output_dir / "charts").mkdir(exist_ok=True)
        
        # Set up matplotlib for better charts
        plt.style.use('seaborn-v0_8')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def create_performance_chart(self, performance_data, filename="portfolio_performance.png"):
        """Create portfolio performance chart"""
        if not performance_data:
            return None
        
        df = pd.DataFrame(performance_data)
        df['date'] = pd.to_datetime(df['date'])
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Portfolio value over time
        ax1.plot(df['date'], df['total_value'], linewidth=2, color='#2E86AB', label='Portfolio Value')
        ax1.set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Daily returns
        ax2.bar(df['date'], df['daily_return'], color=['green' if x >= 0 else 'red' for x in df['daily_return']], alpha=0.7)
        ax2.set_title('Daily Returns (%)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Daily Return (%)', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        
        chart_path = self.output_dir / "charts" / filename
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return f"charts/{filename}"
    
    def create_holdings_chart(self, holdings_data, filename="current_holdings.png"):
        """Create current holdings pie chart"""
        if not holdings_data:
            return None
        
        # Prepare data
        symbols = [h['symbol'] for h in holdings_data]
        values = [h['current_value'] for h in holdings_data]
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83']
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        wedges, texts, autotexts = ax.pie(values, labels=symbols, autopct='%1.1f%%', 
                                         colors=colors[:len(symbols)], startangle=90)
        
        ax.set_title('Current Portfolio Holdings', fontsize=14, fontweight='bold')
        
        # Add value labels
        for i, (symbol, value) in enumerate(zip(symbols, values)):
            autotexts[i].set_text(f'{symbol}\n${value:.0f}\n{autotexts[i].get_text()}')
            autotexts[i].set_fontsize(9)
        
        plt.tight_layout()
        
        chart_path = self.output_dir / "charts" / filename
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return f"charts/{filename}"
    
    def create_stock_scores_chart(self, top_stocks, filename="stock_scores.png"):
        """Create top stocks scores chart"""
        if not top_stocks:
            return None
        
        symbols = [stock['symbol'] for stock in top_stocks[:10]]
        scores = [stock['composite_score'] for stock in top_stocks[:10]]
        technical_scores = [stock['technical_score'] for stock in top_stocks[:10]]
        sentiment_scores = [stock['sentiment_score'] for stock in top_stocks[:10]]
        
        x = range(len(symbols))
        width = 0.25
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        bars1 = ax.bar([i - width for i in x], technical_scores, width, label='Technical Score', color='#2E86AB', alpha=0.8)
        bars2 = ax.bar(x, sentiment_scores, width, label='Sentiment Score', color='#A23B72', alpha=0.8)
        bars3 = ax.bar([i + width for i in x], scores, width, label='Composite Score', color='#F18F01', alpha=0.8)
        
        ax.set_xlabel('Stock Symbol', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Top 10 Stock Analysis Scores', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(symbols)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        chart_path = self.output_dir / "charts" / filename
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return f"charts/{filename}"
    
    def get_market_summary(self):
        """Get basic market summary (simplified)"""
        # In a real implementation, this would fetch actual market data
        return {
            'sp500_change': '+0.75%',
            'nasdaq_change': '+1.20%',
            'dow_change': '+0.45%',
            'vix': '18.5',
            'market_sentiment': 'Moderately Bullish'
        }
    
    def generate_blog_post(self, top_stocks, portfolio_data, performance_data, holdings_data):
        """Generate complete blog post"""
        
        # Create charts
        performance_chart = self.create_performance_chart(performance_data)
        holdings_chart = self.create_holdings_chart(holdings_data)
        scores_chart = self.create_stock_scores_chart(top_stocks)
        
        # Get market summary
        market_summary = self.get_market_summary()
        
        # Calculate portfolio metrics
        latest_performance = performance_data[-1] if performance_data else {
            'total_value': 0, 'daily_pnl': 0, 'daily_return': 0, 
            'total_pnl': 0, 'total_return': 0
        }
        
        # Blog post template
        template_str = '''# Daily Stock Analysis Report
*Generated on {{ analysis_date }}*

## Market Overview

The markets showed {{ market_summary.market_sentiment.lower() }} sentiment today with the S&P 500 {{ market_summary.sp500_change }}, NASDAQ {{ market_summary.nasdaq_change }}, and Dow Jones {{ market_summary.dow_change }}. The VIX closed at {{ market_summary.vix }}, indicating {{ 'elevated' if market_summary.vix|float > 20 else 'moderate' }} market volatility.

## Portfolio Performance Summary

**Current Portfolio Value:** ${{ "%.2f"|format(latest_performance.total_value) }}  
**Daily P&L:** ${{ "%.2f"|format(latest_performance.daily_pnl) }} ({{ "%.2f"|format(latest_performance.daily_return) }}%)  
**Total P&L:** ${{ "%.2f"|format(latest_performance.total_pnl) }} ({{ "%.2f"|format(latest_performance.total_return) }}%)  
**Cash Available:** ${{ "%.2f"|format(portfolio_data.cash) }}  
**Total Invested:** ${{ "%.2f"|format(portfolio_data.invested) }}

{% if performance_chart %}
![Portfolio Performance]({{ performance_chart }})
{% endif %}

{% if holdings_chart and holdings_data %}
## Current Holdings

![Current Holdings]({{ holdings_chart }})

{% for holding in holdings_data[:5] %}
**{{ holding.symbol }}** - {{ "%.4f"|format(holding.shares) }} shares  
- Current Price: ${{ "%.2f"|format(holding.current_price) }}  
- Current Value: ${{ "%.2f"|format(holding.current_value) }}  
- P&L: ${{ "%.2f"|format(holding.pnl) }} ({{ "%.2f"|format(holding.pnl_pct) }}%)  
- Days Held: {{ holding.days_held }}

{% endfor %}
{% endif %}

## Top 10 Stock Recommendations

Based on our comprehensive analysis combining technical indicators and market sentiment, here are today's top stock picks:

{% if scores_chart %}
![Stock Analysis Scores]({{ scores_chart }})
{% endif %}

{% for stock in top_stocks[:10] %}
### {{ loop.index }}. {{ stock.symbol }} - {{ stock.company_name }}

**Composite Score:** {{ stock.composite_score }}/100  
**Current Price:** ${{ "%.2f"|format(stock.current_price) }}  
**Sector:** {{ stock.sector }}  
**Market Cap:** ${{ "%.2fB"|format(stock.market_cap / 1e9) if stock.market_cap > 1e9 else "%.2fM"|format(stock.market_cap / 1e6) }}

**Technical Analysis ({{ stock.technical_score }}/100):**
- RSI: {{ "%.1f"|format(stock.rsi) if stock.rsi else "N/A" }}
- 20-day SMA: ${{ "%.2f"|format(stock.sma_20) if stock.sma_20 else "N/A" }}
- 50-day SMA: ${{ "%.2f"|format(stock.sma_50) if stock.sma_50 else "N/A" }}
- 5-day Change: {{ "%.2f"|format(stock.price_change_5d) if stock.price_change_5d else "N/A" }}%

**Sentiment Analysis ({{ stock.sentiment_score }}/100):**  
{{ stock.sentiment_summary }}

**Investment Thesis:**  
{% if stock.composite_score >= 80 %}
Strong buy candidate with excellent technical momentum and positive sentiment. Consider for immediate investment.
{% elif stock.composite_score >= 70 %}
Good investment opportunity with solid fundamentals and favorable technical indicators.
{% elif stock.composite_score >= 60 %}
Moderate buy with mixed signals. Suitable for diversification but monitor closely.
{% else %}
Proceed with caution. Consider waiting for better entry point or stronger signals.
{% endif %}

---
{% endfor %}

## Trading Activity

{% if recent_purchases %}
### Recent Purchases
{% for purchase in recent_purchases %}
- **{{ purchase.symbol }}**: Bought {{ "%.4f"|format(purchase.shares) }} shares at ${{ "%.2f"|format(purchase.price) }} (Total: ${{ "%.2f"|format(purchase.amount) }})
{% endfor %}
{% endif %}

{% if recent_sales %}
### Recent Sales
{% for sale in recent_sales %}
- **{{ sale.symbol }}**: Sold due to {{ sale.reason.replace('_', ' ').title() }} ({{ "%.2f"|format(sale.pct_change) }}% change)
{% endfor %}
{% endif %}

## Risk Analysis

**Current Risk Factors:**
- Portfolio concentration in top holdings
- Market volatility (VIX: {{ market_summary.vix }})
- Sector allocation balance

**Risk Management Measures:**
- Stop-loss orders at -15%
- Take-profit targets at +25%
- Maximum 30-day holding period
- Position size limits (20% max per stock)

## Market Outlook

Based on current technical indicators and market sentiment, we maintain a {{ 'bullish' if market_summary.market_sentiment == 'Moderately Bullish' else 'cautious' }} outlook for the near term. Key factors to monitor include:

- Federal Reserve policy decisions
- Earnings season developments
- Geopolitical events
- Economic data releases

## Disclaimer

**Important Notice:** This analysis is for educational purposes only and should not be considered as financial advice. All investments carry risk, and past performance does not guarantee future results. The hypothetical portfolio tracking shown here is for demonstration purposes and does not reflect actual trading results.

**Risk Warning:** Stock trading involves substantial risk of loss and is not suitable for all investors. Please consult with a qualified financial advisor before making investment decisions.

---

*This report was generated automatically using quantitative analysis and market data. For questions or feedback, please contact our team.*

*Next update: Tomorrow at 6:00 AM EST*
'''

        # Render template
        template = Template(template_str)
        
        blog_content = template.render(
            analysis_date=datetime.now().strftime("%B %d, %Y at %I:%M %p EST"),
            top_stocks=top_stocks,
            portfolio_data=portfolio_data,
            latest_performance=latest_performance,
            holdings_data=holdings_data,
            performance_chart=performance_chart,
            holdings_chart=holdings_chart,
            scores_chart=scores_chart,
            market_summary=market_summary,
            recent_purchases=getattr(portfolio_data, 'recent_purchases', []),
            recent_sales=getattr(portfolio_data, 'recent_sales', [])
        )
        
        # Save blog post
        blog_file = self.output_dir / "index.md"
        with open(blog_file, 'w') as f:
            f.write(blog_content)
        
        logger.info(f"Blog post generated: {blog_file}")
        
        return blog_file
    
    def create_html_page(self, markdown_file):
        """Convert markdown to HTML and create a styled page"""
        
        # Read markdown content
        with open(markdown_file, 'r') as f:
            markdown_content = f.read()
        
        # Simple HTML template
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Stock Analysis - AI-Powered Investment Research</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2E86AB;
            border-bottom: 3px solid #2E86AB;
            padding-bottom: 10px;
        }
        h2 {
            color: #A23B72;
            margin-top: 30px;
        }
        h3 {
            color: #F18F01;
        }
        .metric {
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .stock-card {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            background: #f8f9fa;
        }
        .score {
            font-weight: bold;
            font-size: 1.2em;
        }
        .score.high { color: #28a745; }
        .score.medium { color: #ffc107; }
        .score.low { color: #dc3545; }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            margin: 20px 0;
        }
        .disclaimer {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }
        .header-info {
            background: linear-gradient(135deg, #2E86AB, #A23B72);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #e9ecef;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-info">
            <h1 style="border: none; color: white; margin: 0;">📈 Daily Stock Analysis</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.1em;">AI-Powered Investment Research & Portfolio Tracking</p>
        </div>
        
        <div id="content">
            <!-- Markdown content will be inserted here -->
            {{ content }}
        </div>
        
        <div class="footer">
            <p><strong>Powered by AI Analysis</strong> | Updated Daily at 6:00 AM EST</p>
            <p>🤖 Automated Technical Analysis • 📊 Real-time Portfolio Tracking • 📈 Daily Investment Insights</p>
        </div>
    </div>
    
    <script>
        // Simple markdown to HTML conversion for basic formatting
        function convertMarkdownToHTML(markdown) {
            return markdown
                .replace(/^# (.*$)/gim, '<h1>$1</h1>')
                .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/!\[([^\]]*)\]\(([^)]*)\)/g, '<img alt="$1" src="$2">')
                .replace(/\[([^\]]*)\]\(([^)]*)\)/g, '<a href="$2">$1</a>')
                .replace(/^---$/gim, '<hr>')
                .replace(/\n\n/g, '</p><p>')
                .replace(/\n/g, '<br>');
        }
        
        // Convert and insert content
        const markdownContent = `{{ markdown_content|safe }}`;
        const htmlContent = convertMarkdownToHTML(markdownContent);
        document.getElementById('content').innerHTML = '<p>' + htmlContent + '</p>';
    </script>
</body>
</html>'''
        
        # Escape markdown content for JavaScript
        escaped_content = markdown_content.replace('`', '\\`').replace('${', '\\${')
        
        # Render HTML
        template = Template(html_template)
        html_content = template.render(
            content="<!-- Content loaded by JavaScript -->",
            markdown_content=escaped_content
        )
        
        # Save HTML file
        html_file = self.output_dir / "index.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML page generated: {html_file}")
        
        return html_file

def main():
    """Test the blog generator"""
    from stock_analyzer import StockAnalyzer
    from portfolio_manager import PortfolioManager
    
    # Initialize components
    analyzer = StockAnalyzer()
    portfolio = PortfolioManager()
    blog_generator = BlogGenerator()
    
    print("Generating test blog post...")
    
    # Get sample data
    test_stocks = [
        {
            'symbol': 'AAPL', 'company_name': 'Apple Inc.', 'sector': 'Technology',
            'market_cap': 3000000000000, 'current_price': 150.0, 'composite_score': 85,
            'technical_score': 80, 'sentiment_score': 95, 'rsi': 45.5,
            'sma_20': 148.0, 'sma_50': 145.0, 'price_change_5d': 2.5,
            'sentiment_summary': 'Strong positive sentiment from recent earnings'
        },
        {
            'symbol': 'MSFT', 'company_name': 'Microsoft Corporation', 'sector': 'Technology',
            'market_cap': 2800000000000, 'current_price': 300.0, 'composite_score': 82,
            'technical_score': 85, 'sentiment_score': 75, 'rsi': 52.3,
            'sma_20': 295.0, 'sma_50': 290.0, 'price_change_5d': 1.8,
            'sentiment_summary': 'Positive outlook on cloud growth'
        }
    ]
    
    # Mock portfolio data
    portfolio_data = type('obj', (object,), {
        'cash': 50.0,
        'invested': 150.0,
        'recent_purchases': [],
        'recent_sales': []
    })
    
    performance_data = [
        {
            'date': (datetime.now() - timedelta(days=1)).isoformat(),
            'total_value': 195.0,
            'daily_pnl': -5.0,
            'daily_return': -2.5,
            'total_pnl': -5.0,
            'total_return': -2.5
        },
        {
            'date': datetime.now().isoformat(),
            'total_value': 200.0,
            'daily_pnl': 5.0,
            'daily_return': 2.6,
            'total_pnl': 0.0,
            'total_return': 0.0
        }
    ]
    
    holdings_data = [
        {
            'symbol': 'AAPL',
            'shares': 0.5,
            'current_price': 150.0,
            'current_value': 75.0,
            'pnl': 5.0,
            'pnl_pct': 7.1,
            'days_held': 5
        },
        {
            'symbol': 'MSFT',
            'shares': 0.25,
            'current_price': 300.0,
            'current_value': 75.0,
            'pnl': -5.0,
            'pnl_pct': -6.3,
            'days_held': 3
        }
    ]
    
    # Generate blog post
    blog_file = blog_generator.generate_blog_post(
        test_stocks, portfolio_data, performance_data, holdings_data
    )
    
    # Create HTML version
    html_file = blog_generator.create_html_page(blog_file)
    
    print(f"Blog post generated: {blog_file}")
    print(f"HTML page generated: {html_file}")
    print(f"Charts saved in: {blog_generator.output_dir / 'charts'}")

if __name__ == "__main__":
    main()

