#!/usr/bin/env python3
"""
Weekly Report Generator for Pink Sheet Automation
Generates comprehensive weekly performance reports
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_weekly_report():
    """Generate comprehensive weekly report"""
    
    data_dir = Path("data")
    reports_dir = data_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Load data
    performance_file = data_dir / "pink_performance.json"
    transactions_file = data_dir / "pink_transactions.json"
    automation_log = data_dir / "automation_log.json"
    
    performance_data = []
    transactions = []
    automation_logs = []
    
    try:
        if performance_file.exists():
            with open(performance_file, 'r') as f:
                performance_data = json.load(f)
                
        if transactions_file.exists():
            with open(transactions_file, 'r') as f:
                transactions = json.load(f)
                
        if automation_log.exists():
            with open(automation_log, 'r') as f:
                automation_logs = json.load(f)
                
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    if not performance_data:
        print("No performance data available for report")
        return
    
    # Calculate weekly metrics
    week_start = datetime.now() - timedelta(days=7)
    week_data = [p for p in performance_data if datetime.fromisoformat(p['date']) >= week_start]
    week_transactions = [t for t in transactions if datetime.fromisoformat(t['timestamp']) >= week_start]
    
    if not week_data:
        print("No data for the past week")
        return
    
    # Performance metrics
    start_value = week_data[0]['total_value'] if week_data else 20.0
    end_value = week_data[-1]['total_value'] if week_data else 20.0
    weekly_return = ((end_value - start_value) / start_value) * 100 if start_value > 0 else 0
    
    # Transaction analysis
    buys = [t for t in week_transactions if t['action'] == 'BUY']
    sells = [t for t in week_transactions if t['action'] == 'SELL']
    
    total_invested = sum(t['amount'] for t in buys)
    total_proceeds = sum(t['amount'] for t in sells)
    
    # Best and worst trades
    profitable_sells = [t for t in sells if t.get('profit_loss', 0) > 0]
    losing_sells = [t for t in sells if t.get('profit_loss', 0) < 0]
    
    best_trade = max(sells, key=lambda x: x.get('profit_pct', 0)) if sells else None
    worst_trade = min(sells, key=lambda x: x.get('profit_pct', 0)) if sells else None
    
    # Sector analysis
    sector_performance = {}
    for transaction in buys:
        category = transaction.get('category', 'OTHER')
        if category not in sector_performance:
            sector_performance[category] = {'count': 0, 'amount': 0}
        sector_performance[category]['count'] += 1
        sector_performance[category]['amount'] += transaction['amount']
    
    # Generate report
    report = {
        'report_date': datetime.now().isoformat(),
        'week_start': week_start.isoformat(),
        'week_end': datetime.now().isoformat(),
        
        'performance_summary': {
            'starting_value': round(start_value, 2),
            'ending_value': round(end_value, 2),
            'weekly_return': round(weekly_return, 2),
            'total_return': round(week_data[-1]['total_return_pct'], 2) if week_data else 0,
            'best_day': max(week_data, key=lambda x: x.get('total_return', 0))['date'] if week_data else None,
            'worst_day': min(week_data, key=lambda x: x.get('total_return', 0))['date'] if week_data else None
        },
        
        'trading_activity': {
            'total_trades': len(week_transactions),
            'buy_orders': len(buys),
            'sell_orders': len(sells),
            'total_invested': round(total_invested, 2),
            'total_proceeds': round(total_proceeds, 2),
            'win_rate': round((len(profitable_sells) / len(sells)) * 100, 1) if sells else 0,
            'avg_hold_time': round(sum(t.get('hold_days', 0) for t in sells) / len(sells), 1) if sells else 0
        },
        
        'best_worst_trades': {
            'best_trade': {
                'symbol': best_trade['symbol'] if best_trade else None,
                'profit_pct': round(best_trade['profit_pct'], 2) if best_trade else 0,
                'profit_amount': round(best_trade['profit_loss'], 2) if best_trade else 0
            } if best_trade else None,
            'worst_trade': {
                'symbol': worst_trade['symbol'] if worst_trade else None,
                'profit_pct': round(worst_trade['profit_pct'], 2) if worst_trade else 0,
                'profit_amount': round(worst_trade['profit_loss'], 2) if worst_trade else 0
            } if worst_trade else None
        },
        
        'sector_breakdown': sector_performance,
        
        'automation_stats': {
            'successful_runs': len([log for log in automation_logs if log.get('date', '') >= week_start.isoformat()]),
            'avg_runtime': round(sum(log.get('runtime_minutes', 0) for log in automation_logs[-7:]) / min(7, len(automation_logs)), 1) if automation_logs else 0,
            'avg_stocks_analyzed': round(sum(log.get('stocks_analyzed', 0) for log in automation_logs[-7:]) / min(7, len(automation_logs)), 0) if automation_logs else 0
        },
        
        'recommendations': generate_recommendations(week_data, week_transactions, weekly_return)
    }
    
    # Save report
    report_file = reports_dir / f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate text summary
    generate_text_summary(report, reports_dir)
    
    # Generate performance chart
    generate_performance_chart(week_data, reports_dir)
    
    print(f"✅ Weekly report generated: {report_file}")
    print(f"📊 Weekly return: {weekly_return:.2f}%")
    print(f"💼 Total trades: {len(week_transactions)}")
    print(f"🎯 Win rate: {report['trading_activity']['win_rate']:.1f}%")
    
    return report

def generate_recommendations(week_data, week_transactions, weekly_return):
    """Generate recommendations based on performance"""
    recommendations = []
    
    if weekly_return > 10:
        recommendations.append("Excellent performance! Consider maintaining current strategy.")
    elif weekly_return > 0:
        recommendations.append("Positive returns. Monitor for consistency.")
    else:
        recommendations.append("Negative returns. Review risk management and stock selection.")
    
    # Transaction frequency analysis
    if len(week_transactions) > 20:
        recommendations.append("High trading frequency. Consider reducing overtrading.")
    elif len(week_transactions) < 5:
        recommendations.append("Low trading activity. Consider more active position management.")
    
    # Sector diversification
    buys = [t for t in week_transactions if t['action'] == 'BUY']
    sectors = set(t.get('category', 'OTHER') for t in buys)
    
    if len(sectors) < 2:
        recommendations.append("Consider diversifying across more pink sheet sectors.")
    elif len(sectors) > 4:
        recommendations.append("Good sector diversification maintained.")
    
    return recommendations

def generate_text_summary(report, reports_dir):
    """Generate human-readable text summary"""
    
    summary = f"""
PINK SHEET AUTOMATION - WEEKLY REPORT
=====================================
Report Date: {datetime.now().strftime('%B %d, %Y')}
Week: {datetime.fromisoformat(report['week_start']).strftime('%m/%d')} - {datetime.fromisoformat(report['week_end']).strftime('%m/%d')}

PERFORMANCE SUMMARY
-------------------
Starting Value: ${report['performance_summary']['starting_value']:,.2f}
Ending Value: ${report['performance_summary']['ending_value']:,.2f}
Weekly Return: {report['performance_summary']['weekly_return']:+.2f}%
Total Return: {report['performance_summary']['total_return']:+.2f}%

TRADING ACTIVITY
----------------
Total Trades: {report['trading_activity']['total_trades']}
Buy Orders: {report['trading_activity']['buy_orders']}
Sell Orders: {report['trading_activity']['sell_orders']}
Amount Invested: ${report['trading_activity']['total_invested']:,.2f}
Proceeds: ${report['trading_activity']['total_proceeds']:,.2f}
Win Rate: {report['trading_activity']['win_rate']:.1f}%
Avg Hold Time: {report['trading_activity']['avg_hold_time']:.1f} days

BEST/WORST TRADES
-----------------"""
    
    if report['best_worst_trades']['best_trade']:
        best = report['best_worst_trades']['best_trade']
        summary += f"\nBest Trade: {best['symbol']} (+{best['profit_pct']:.1f}%, ${best['profit_amount']:+.2f})"
    
    if report['best_worst_trades']['worst_trade']:
        worst = report['best_worst_trades']['worst_trade']
        summary += f"\nWorst Trade: {worst['symbol']} ({worst['profit_pct']:+.1f}%, ${worst['profit_amount']:+.2f})"
    
    summary += f"""

SECTOR BREAKDOWN
----------------"""
    
    for sector, data in report['sector_breakdown'].items():
        summary += f"\n{sector.replace('_', ' ').title()}: {data['count']} trades, ${data['amount']:.2f}"
    
    summary += f"""

AUTOMATION STATS
----------------
Successful Runs: {report['automation_stats']['successful_runs']}
Avg Runtime: {report['automation_stats']['avg_runtime']:.1f} minutes
Avg Stocks Analyzed: {report['automation_stats']['avg_stocks_analyzed']}

RECOMMENDATIONS
---------------"""
    
    for rec in report['recommendations']:
        summary += f"\n• {rec}"
    
    summary += f"""

NEXT WEEK OUTLOOK
-----------------
• Continue focusing on pink sheet opportunities
• Monitor for volume spikes and breakout patterns
• Maintain risk management with stop losses
• Target 50%+ gains for quick profit taking

Generated by Pink Sheet Automation Engine
"""
    
    # Save text summary
    summary_file = reports_dir / f"weekly_summary_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    print(f"📄 Text summary saved: {summary_file}")

def generate_performance_chart(week_data, reports_dir):
    """Generate performance chart"""
    try:
        if len(week_data) < 2:
            return
        
        # Prepare data
        dates = [datetime.fromisoformat(d['date']) for d in week_data]
        values = [d['total_value'] for d in week_data]
        returns = [d['total_return_pct'] for d in week_data]
        
        # Create chart
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Portfolio value chart
        ax1.plot(dates, values, 'b-', linewidth=2, marker='o', markersize=4)
        ax1.set_title('Pink Sheet Portfolio Value - Weekly Performance', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        
        # Return percentage chart
        ax2.plot(dates, returns, 'g-', linewidth=2, marker='s', markersize=4)
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        ax2.set_title('Total Return Percentage', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Return (%)', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        
        plt.tight_layout()
        
        # Save chart
        chart_file = reports_dir / f"performance_chart_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Performance chart saved: {chart_file}")
        
    except Exception as e:
        print(f"Error generating chart: {e}")

if __name__ == "__main__":
    report = generate_weekly_report()
    if report:
        print("\n🎉 Weekly report generation complete!")
    else:
        print("\n❌ Failed to generate weekly report")

