import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { Button } from './components/ui/button'
import { Badge } from './components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs'
import { TrendingUp, TrendingDown, DollarSign, PieChart, BarChart3, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react'
import './App.css'

// Enhanced mock data with interactive trading
const mockData = {
  portfolioSummary: {
    totalValue: 48.50,
    dailyPnL: 0.00,
    dailyReturn: 0.00,
    totalPnL: 28.50,
    totalReturn: 142.5,
    cash: 48.50,
    invested: 0.00,
    sellProceeds: 28.50
  },
  
  pendingTrades: [
    {
      id: 'trade_20250609_1',
      symbol: 'SNOW',
      name: 'Snowflake Inc.',
      action: 'BUY',
      price: 211.25,
      shares: 0.0918,
      allocation: 19.40,
      score: 155.0,
      rsi: 77.5,
      sector: 'Growth Mid-Cap',
      reasoning: 'High composite score; Above 20-day moving average; Positive momentum',
      status: 'PENDING',
      priceChange5d: 0.5,
      volatility: 45.2
    },
    {
      id: 'trade_20250609_2', 
      symbol: 'SOFI',
      name: 'SoFi Technologies',
      action: 'BUY',
      price: 14.30,
      shares: 1.1871,
      allocation: 16.97,
      score: 153.0,
      rsi: 58.1,
      sector: 'Emerging Tech',
      reasoning: 'RSI in optimal range; Above 20-day moving average; Positive momentum; High growth potential',
      status: 'PENDING',
      priceChange5d: 4.6,
      volatility: 52.8
    },
    {
      id: 'trade_20250609_3',
      symbol: 'UPST', 
      name: 'Upstart Holdings',
      action: 'BUY',
      price: 55.93,
      shares: 0.2168,
      allocation: 12.12,
      score: 148.0,
      rsi: 72.4,
      sector: 'Emerging Tech',
      reasoning: 'High composite score; Above 20-day moving average; Fintech growth potential',
      status: 'PENDING',
      priceChange5d: 16.8,
      volatility: 68.1
    }
  ],

  topStocks: [
    {
      rank: 1,
      symbol: 'SNOW',
      name: 'Snowflake Inc.',
      price: 211.25,
      score: 155.0,
      rsi: 77.5,
      priceChange5d: 0.5,
      sector: 'Growth Mid-Cap',
      recommendation: 'Strong Buy'
    },
    {
      rank: 2,
      symbol: 'SOFI',
      name: 'SoFi Technologies',
      price: 14.30,
      score: 153.0,
      rsi: 58.1,
      priceChange5d: 4.6,
      sector: 'Emerging Tech',
      recommendation: 'Strong Buy'
    },
    {
      rank: 3,
      symbol: 'UPST',
      name: 'Upstart Holdings',
      price: 55.93,
      score: 148.0,
      rsi: 72.4,
      priceChange5d: 16.8,
      sector: 'Emerging Tech',
      recommendation: 'Strong Buy'
    },
    {
      rank: 4,
      symbol: 'PLUG',
      name: 'Plug Power Inc.',
      price: 1.04,
      score: 141.0,
      rsi: 66.7,
      priceChange5d: 26.8,
      sector: 'Clean Energy',
      recommendation: 'Buy'
    },
    {
      rank: 5,
      symbol: 'SEDG',
      name: 'SolarEdge Technologies',
      price: 18.55,
      score: 136.0,
      rsi: 41.8,
      priceChange5d: 8.5,
      sector: 'Clean Energy',
      recommendation: 'Buy'
    }
  ],

  holdings: [
    // Starting fresh - no holdings yet
  ],

  marketSummary: {
    sp500: '+0.75%',
    nasdaq: '+1.20%',
    dow: '+0.45%',
    vix: '18.5'
  },

  analysisStats: {
    totalStocksAnalyzed: 110,
    sectorsAnalyzed: 11,
    highGrowthStocks: 45,
    emergingTechStocks: 20
  }
}

function App() {
  const [activeTab, setActiveTab] = useState('recommendations')
  const [pendingTrades, setPendingTrades] = useState(mockData.pendingTrades)
  const [portfolioData, setPortfolioData] = useState(mockData.portfolioSummary)

  const handleTradeAction = (tradeId, action) => {
    setPendingTrades(prev => 
      prev.map(trade => 
        trade.id === tradeId 
          ? { ...trade, status: action === 'approve' ? 'APPROVED' : 'REJECTED' }
          : trade
      )
    )

    if (action === 'approve') {
      const trade = pendingTrades.find(t => t.id === tradeId)
      if (trade) {
        // Update portfolio data
        setPortfolioData(prev => ({
          ...prev,
          cash: prev.cash - trade.allocation,
          invested: prev.invested + trade.allocation
        }))
      }
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'PENDING': return 'bg-yellow-100 text-yellow-800'
      case 'APPROVED': return 'bg-green-100 text-green-800'
      case 'REJECTED': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case 'Strong Buy': return 'bg-green-100 text-green-800'
      case 'Buy': return 'bg-blue-100 text-blue-800'
      case 'Hold': return 'bg-yellow-100 text-yellow-800'
      case 'Sell': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <BarChart3 className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Daily Stock Analysis</h1>
                <p className="text-sm text-gray-600">AI-Powered Investment Research</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Last Updated</p>
              <p className="text-lg font-semibold text-gray-900">
                {new Date().toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit',
                  hour12: true 
                })}
              </p>
              <p className="text-sm text-gray-500">{new Date().toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Market Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100">S&P 500</p>
                  <p className="text-2xl font-bold">{mockData.marketSummary.sp500}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-200" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100">NASDAQ</p>
                  <p className="text-2xl font-bold">{mockData.marketSummary.nasdaq}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-blue-200" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100">Dow Jones</p>
                  <p className="text-2xl font-bold">{mockData.marketSummary.dow}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-purple-200" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-orange-500 to-red-500 text-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100">VIX</p>
                  <p className="text-2xl font-bold">{mockData.marketSummary.vix}</p>
                </div>
                <TrendingDown className="h-8 w-8 text-orange-200" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Enhanced Portfolio Performance */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <PieChart className="h-6 w-6" />
              <span>Portfolio Performance</span>
            </CardTitle>
            <CardDescription>Your $20/day investment simulation results</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">${portfolioData.totalValue.toFixed(2)}</div>
                <div className="text-sm text-gray-600">Total Value</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">${portfolioData.dailyPnL.toFixed(2)}</div>
                <div className="text-sm text-gray-600">Daily P&L</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">{portfolioData.dailyReturn.toFixed(2)}%</div>
                <div className="text-sm text-gray-600">Daily Return</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">${portfolioData.totalPnL.toFixed(2)}</div>
                <div className="text-sm text-gray-600">Total P&L</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">{portfolioData.totalReturn.toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Total Return</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">${portfolioData.cash.toFixed(2)}</div>
                <div className="text-sm text-gray-600">Available Cash</div>
              </div>
            </div>
            
            {/* Cash Flow Breakdown */}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">💰 Cash Flow Breakdown</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-blue-700">Base Daily Investment:</span>
                  <span className="font-semibold ml-2">$20.00</span>
                </div>
                <div>
                  <span className="text-green-700">Sell Proceeds:</span>
                  <span className="font-semibold ml-2">+${portfolioData.sellProceeds.toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-blue-700">Total Available:</span>
                  <span className="font-semibold ml-2">${portfolioData.cash.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Analysis Stats */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>🚀 Enhanced Analysis Engine</CardTitle>
            <CardDescription>Expanded universe with high-growth potential stocks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{mockData.analysisStats.totalStocksAnalyzed}</div>
                <div className="text-sm text-gray-600">Total Stocks</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{mockData.analysisStats.sectorsAnalyzed}</div>
                <div className="text-sm text-gray-600">Sectors</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{mockData.analysisStats.highGrowthStocks}</div>
                <div className="text-sm text-gray-600">High-Growth</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{mockData.analysisStats.emergingTechStocks}</div>
                <div className="text-sm text-gray-600">Emerging Tech</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="recommendations">Top Recommendations</TabsTrigger>
            <TabsTrigger value="pending">Pending Trades ({pendingTrades.filter(t => t.status === 'PENDING').length})</TabsTrigger>
            <TabsTrigger value="holdings">Current Holdings</TabsTrigger>
            <TabsTrigger value="analysis">Market Analysis</TabsTrigger>
          </TabsList>

          {/* Pending Trades Tab */}
          <TabsContent value="pending" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="h-6 w-6" />
                  <span>Pending Trade Recommendations</span>
                </CardTitle>
                <CardDescription>
                  Review and approve today's AI-generated trade suggestions
                </CardDescription>
              </CardHeader>
              <CardContent>
                {pendingTrades.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No pending trades at this time
                  </div>
                ) : (
                  <div className="space-y-6">
                    {pendingTrades.map((trade, index) => (
                      <div key={trade.id} className="border rounded-lg p-6 bg-white shadow-sm">
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex items-center space-x-3">
                            <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
                              Trade {index + 1}
                            </div>
                            <Badge className={getStatusColor(trade.status)}>
                              {trade.status}
                            </Badge>
                          </div>
                          <div className="text-right">
                            <div className="text-sm text-gray-500">Trade ID</div>
                            <div className="text-xs font-mono text-gray-400">{trade.id}</div>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                          {/* Stock Info */}
                          <div>
                            <h3 className="text-xl font-bold text-gray-900 mb-1">
                              {trade.action} {trade.symbol}
                            </h3>
                            <p className="text-gray-600 mb-3">{trade.name}</p>
                            <div className="space-y-2 text-sm">
                              <div className="flex justify-between">
                                <span className="text-gray-600">Price:</span>
                                <span className="font-semibold">${trade.price.toFixed(2)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Shares:</span>
                                <span className="font-semibold">{trade.shares.toFixed(4)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Amount:</span>
                                <span className="font-semibold text-blue-600">${trade.allocation.toFixed(2)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Sector:</span>
                                <Badge variant="outline">{trade.sector}</Badge>
                              </div>
                            </div>
                          </div>

                          {/* Analysis Metrics */}
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-3">Analysis Metrics</h4>
                            <div className="space-y-3">
                              <div>
                                <div className="flex justify-between items-center mb-1">
                                  <span className="text-sm text-gray-600">Composite Score</span>
                                  <span className="font-semibold text-green-600">{trade.score.toFixed(1)}/100</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <div 
                                    className="bg-green-600 h-2 rounded-full" 
                                    style={{ width: `${Math.min(trade.score, 100)}%` }}
                                  ></div>
                                </div>
                              </div>
                              
                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <span className="text-gray-600">RSI:</span>
                                  <span className="font-semibold ml-2">{trade.rsi.toFixed(1)}</span>
                                </div>
                                <div>
                                  <span className="text-gray-600">5d Change:</span>
                                  <span className={`font-semibold ml-2 ${trade.priceChange5d >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {trade.priceChange5d >= 0 ? '+' : ''}{trade.priceChange5d.toFixed(1)}%
                                  </span>
                                </div>
                                <div>
                                  <span className="text-gray-600">Volatility:</span>
                                  <span className="font-semibold ml-2">{trade.volatility.toFixed(1)}%</span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Reasoning & Actions */}
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-3">AI Reasoning</h4>
                            <p className="text-sm text-gray-700 mb-4 leading-relaxed">
                              {trade.reasoning}
                            </p>
                            
                            {trade.status === 'PENDING' && (
                              <div className="space-y-2">
                                <Button 
                                  onClick={() => handleTradeAction(trade.id, 'approve')}
                                  className="w-full bg-green-600 hover:bg-green-700 text-white"
                                >
                                  <CheckCircle className="h-4 w-4 mr-2" />
                                  Approve Trade
                                </Button>
                                <Button 
                                  onClick={() => handleTradeAction(trade.id, 'reject')}
                                  variant="outline"
                                  className="w-full border-red-300 text-red-600 hover:bg-red-50"
                                >
                                  <XCircle className="h-4 w-4 mr-2" />
                                  Reject Trade
                                </Button>
                              </div>
                            )}

                            {trade.status === 'APPROVED' && (
                              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                <div className="flex items-center text-green-800">
                                  <CheckCircle className="h-5 w-5 mr-2" />
                                  <span className="font-semibold">Trade Approved</span>
                                </div>
                                <p className="text-sm text-green-700 mt-1">
                                  Order will be executed at market open
                                </p>
                              </div>
                            )}

                            {trade.status === 'REJECTED' && (
                              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                                <div className="flex items-center text-red-800">
                                  <XCircle className="h-5 w-5 mr-2" />
                                  <span className="font-semibold">Trade Rejected</span>
                                </div>
                                <p className="text-sm text-red-700 mt-1">
                                  Funds remain available for other opportunities
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Top Recommendations Tab */}
          <TabsContent value="recommendations" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Top 10 Stock Recommendations</CardTitle>
                <CardDescription>AI-powered analysis from 110+ stocks across 11 sectors</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockData.topStocks.map((stock, index) => (
                    <div key={stock.symbol} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                      <div className="flex items-center space-x-4">
                        <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold min-w-[2rem] text-center">
                          {stock.rank}
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg">{stock.symbol}</h3>
                          <p className="text-gray-600 text-sm">{stock.name}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-6">
                        <div className="text-right">
                          <div className="font-semibold">${stock.price.toFixed(2)}</div>
                          <div className={`text-sm ${stock.priceChange5d >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {stock.priceChange5d >= 0 ? '+' : ''}{stock.priceChange5d.toFixed(1)}% (5d)
                          </div>
                        </div>
                        
                        <div className="text-center">
                          <div className="text-sm text-gray-600">Score</div>
                          <div className="font-semibold text-green-600">{stock.score.toFixed(1)}/100</div>
                        </div>
                        
                        <div className="text-center">
                          <div className="text-sm text-gray-600">RSI</div>
                          <div className="font-semibold">{stock.rsi.toFixed(1)}</div>
                        </div>
                        
                        <Badge className={getRecommendationColor(stock.recommendation)}>
                          {stock.recommendation}
                        </Badge>
                        
                        <Badge variant="outline">{stock.sector}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Current Holdings Tab */}
          <TabsContent value="holdings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Current Portfolio Holdings</CardTitle>
                <CardDescription>Your active positions and their performance</CardDescription>
              </CardHeader>
              <CardContent>
                {mockData.holdings.length === 0 ? (
                  <div className="text-center py-12">
                    <PieChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No Holdings Yet</h3>
                    <p className="text-gray-600 mb-4">
                      Starting fresh with $48.50 available for investment
                    </p>
                    <p className="text-sm text-gray-500">
                      Approve pending trades to begin building your portfolio
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {mockData.holdings.map((holding) => (
                      <div key={holding.symbol} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <h3 className="font-semibold">{holding.symbol}</h3>
                          <p className="text-sm text-gray-600">{holding.shares} shares</p>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">${holding.value}</div>
                          <div className={`text-sm ${holding.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {holding.pnl >= 0 ? '+' : ''}${holding.pnl} ({holding.pnlPct >= 0 ? '+' : ''}{holding.pnlPct}%)
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Market Analysis Tab */}
          <TabsContent value="analysis" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Market Outlook</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-5 w-5 text-green-600" />
                      <span className="font-semibold text-green-600">Moderately Bullish</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed">
                      Current technical indicators suggest continued upward momentum with moderate volatility. 
                      High-growth and emerging tech sectors showing strong potential. Key support levels are 
                      holding while resistance levels show signs of breaking.
                    </p>
                    <div className="grid grid-cols-2 gap-4 mt-4">
                      <div>
                        <div className="text-sm text-gray-600">Market Sentiment</div>
                        <div className="font-semibold text-green-600">Positive</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Volatility (VIX)</div>
                        <div className="font-semibold text-orange-600">18.5 (Moderate)</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Trend Strength</div>
                        <div className="font-semibold text-blue-600">Strong</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Growth Potential</div>
                        <div className="font-semibold text-purple-600">High</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Risk Factors</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                      <div>
                        <div className="font-semibold text-yellow-800">Federal Reserve Policy</div>
                        <p className="text-sm text-gray-600">Upcoming FOMC meetings may impact market direction</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                      <div>
                        <div className="font-semibold text-yellow-800">Earnings Season</div>
                        <p className="text-sm text-gray-600">Q4 earnings results could drive sector rotation</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                      <div>
                        <div className="font-semibold text-red-800">Geopolitical Events</div>
                        <p className="text-sm text-gray-600">Global tensions may increase market volatility</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Trading Strategy */}
            <Card>
              <CardHeader>
                <CardTitle>Enhanced Trading Strategy</CardTitle>
                <CardDescription>Current automated trading parameters with expanded universe</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <DollarSign className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-blue-600">$20</div>
                    <div className="text-sm text-gray-600">Base Daily Investment</div>
                  </div>
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <TrendingDown className="h-8 w-8 text-red-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-red-600">-15%</div>
                    <div className="text-sm text-gray-600">Stop Loss</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <TrendingUp className="h-8 w-8 text-green-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-green-600">+25%</div>
                    <div className="text-sm text-gray-600">Take Profit</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <Clock className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-purple-600">30</div>
                    <div className="text-sm text-gray-600">Max Days Hold</div>
                  </div>
                </div>
                
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">🚀 Enhanced Features</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">• 110+ stocks analyzed daily</span><br/>
                      <span className="text-gray-600">• 11 sectors including emerging tech</span><br/>
                      <span className="text-gray-600">• High-growth mid-cap focus</span>
                    </div>
                    <div>
                      <span className="text-gray-600">• Interactive trade approval</span><br/>
                      <span className="text-gray-600">• Sell proceeds reinvestment</span><br/>
                      <span className="text-gray-600">• Multi-timeframe analysis</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Disclaimer */}
        <Card className="mt-8 border-yellow-200 bg-yellow-50">
          <CardContent className="p-6">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-6 w-6 text-yellow-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-yellow-800 mb-2">Important Disclaimer</h3>
                <p className="text-sm text-yellow-700 leading-relaxed">
                  This system is for educational purposes only and should not be considered financial advice. 
                  All investments carry risk, and past performance does not guarantee future results. The portfolio 
                  tracking is hypothetical and does not reflect actual trading results. Please consult with a 
                  qualified financial advisor before making investment decisions.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App

