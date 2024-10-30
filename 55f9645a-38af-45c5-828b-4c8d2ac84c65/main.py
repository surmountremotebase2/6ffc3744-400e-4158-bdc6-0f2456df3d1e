from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # NVIDIA ticker symbol
        self.ticker = "NVDA"
        # Trade parameters
        self.take_profit_multiplier = 1.03  # Take profit at 3% above buy price
        self.stop_loss_multiplier = 0.97    # Stop loss at 3% below buy price
        self.position_size_fraction = 0.1   # Risk 10% of portfolio on single trade
        
        # Technical indicators periods
        self.short_window = 5
        self.long_window = 20
        
        # Tracking trade entry price
        self.entry_price = None

    @property
    def assets(self):
        # Only trade NVDA
        return [self.ticker]

    @property
    def interval(self):
        # Day trade on a 5 min interval
        return "5min"
    
    def run(self, data):
        # Initialize allocation with no position
        allocation = {self.ticker: 0.0}
        
        # Calculate moving averages
        short_sma = SMA(self.ticker, data["ohlcv"], self.short_window)
        long_sma = SMA(self.ticker, data["ohlcv"], self.long_window)
        
        # Check if we have enough data
        if len(short_sma) > 1 and len(long_sma) > 1:
            recent_short_sma = short_sma[-1]
            recent_long_sma = long_sma[-1]
            previous_short_sma = short_sma[-2]
            previous_long_sma = long_sma[-2]
            
            # Determine if SMA crossover occurred
            crossover_up = (previous_short_sma < previous_long_sma) and (recent_short_sma > recent_long_sma)
            crossover_down = (previous_short_sma > previous_long_sma) and (recent_short_sma < recent_long_sma)
            
            # Current price of NVDA
            current_price = data["ohlcv"][-1][self.ticker]["close"]
            
            # Trading logic
            if crossover_up and self.entry_price is None:
                # Buy signal - allocate a fraction of the portfolio
                allocation[self.ticker] = self.position_size_fraction
                self.entry_price = current_price
                log("Entering trade at {}".format(current_price))
                
            elif self.entry_price:
                # Check for exit conditions
                if current_price >= self.entry_price * self.take_profit_multiplier:
                    # Take profit
                    allocation[self.ticker] = 0.0
                    self.entry_price = None
                    log("Taking profit at {}".format(current_price))
                elif current_price <= self.entry_price * self.stop_loss_multiplier:
                    # Stop loss
                    allocation[self.ticker] = 0.0
                    self.entry_price = None
                    log("Stopping loss at {}".format(current_price))
                    
        # If the end of the day is approaching, close any open position
        current_time = data["ohlcv"][-1][self.ticker]["date"]
        if "15:55" in current_time:  # Format can vary; adjust according to data format
            allocation[self.ticker] = 0.0
            self.entry_price = None
            log("Closing position at end of day")

        return TargetAllocation(allocation)