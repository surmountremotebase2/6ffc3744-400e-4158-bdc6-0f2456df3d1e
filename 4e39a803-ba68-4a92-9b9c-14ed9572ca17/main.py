from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD, BB
from surmount.data import InsiderTrading, SocialSentiment, FinancialStatement, Ratios
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Focused on tech-related tickers with a high probability of volatility and growth
        self.tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]
        self.data_list = []
        
        # Adding data sources for each ticker
        for ticker in self.tickers:
            self.data_list.append(InsiderTrading(ticker))
            self.data_list.append(SocialSentiment(ticker))
            self.data_list.append(FinancialStatement(ticker))
            self.data_list.append(Ratios(ticker))

    @property
    def interval(self):
        # Using daily intervals to capture long-term trends and reduce noise
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {}
        
        for ticker in self.tickers:
            allocation_dict[ticker] = 0.0  # Initialize allocations
            
            sentiment_data = data.get(("social_sentiment", ticker), [])
            insider_data = data.get(("insider_trading", ticker), [])
            financial_data = data.get(("financial_statement", ticker), [])
            ratio_data = data.get(("ratios", ticker), [])
            
            if not sentiment_data or not insider_data or not financial_data or not ratio_data:
                continue  # Skip if any data is missing for a ticker
            
            # Aggressive allocation condition based on positive sentiment and favorable financial indicators
            positive_sentiment = sentiment_data[-1]['twitterSentiment'] > 0.6 or sentiment_data[-1]['stocktwitsSentiment'] > 0.6
            recent_insider_sales = any(x['transactionType'] == 'S-Sale' for x in insider_data)
            strong_financials = financial_data[-1]['netIncome'] > 1000000000 and ratio_data[-1]['returnOnEquity'] > 0.15
            
            # If sentiment is positive, no recent insider sales, and financials are strong, allocate aggressively
            if positive_sentiment and not recent_insider_sales and strong_financials:
                allocation_dict[ticker] = 0.25  # Assign 25% to each qualifying ticker (exceeding 1 will be normalized later)
                
        # Normalize allocations if they exceed 1
        total_allocation = sum(allocation_dict.values())
        if total_allocation > 1:
            allocation_dict = {ticker: allocation / total_allocation for ticker, allocation in allocation_dict.items()}
        
        return TargetAllocation(allocation_dict)