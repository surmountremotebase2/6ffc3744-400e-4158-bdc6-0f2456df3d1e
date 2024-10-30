from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "NVDA"
    
    @property
    def interval(self):
        # Using daily data for RSI calculation
        return "1day"

    @property
    def assets(self):
        # Targeting only NVIDIA
        return [self.ticker]

    def run(self, data):
        # Calculate the RSI for NVDA
        rsi_values = RSI(self.ticker, data["ohlcv"], length=14)
        
        # Initialize allocation
        allocation_dict = {self.ticker: 0}
        
        if len(rsi_values) > 0:
            current_rsi = rsi_values[-1]  # Get the most recent RSI value
            
            if current_rsi < 30:
                # NVDA is considered oversold, buy signal
                allocation_dict[self.ticker] = 1  # Allocate 100% of the portfolio to NVDA
            elif current_rsi > 70:
                # NVDA is considered overbought, sell signal
                allocation_dict[self.ticker] = 0  # Allocate 0%, suggesting to sell or not buy
            else:
                # NVDA is neither overbought nor oversold, hold position
                # This part could be modified based on whether you want to maintain any existing position or not.
                # For simplicity, it sets the allocation to 0.
                allocation_dict[self.ticker] = 0
        
        return TargetAllocation(allocation_dict)