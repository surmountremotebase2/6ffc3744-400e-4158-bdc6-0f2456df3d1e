from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log
from surmount.utils import Percent

class TradingStrategy(Strategy):
    
    @property
    def assets(self):
        # Only trading QQQ
        return ["QQQ"]

    @property
    def interval(self):
        # Daily interval for day trading strategy
        return "1day"
    
    def run(self, data):
        qqq_data = data["ohlcv"]
        
        # Ensure we have enough data points for SMA calculation
        if len(qqq_data) < 21:
            return TargetAllocation({})
        
        # Calculate 20-day SMA for QQQ
        sma20 = SMA("QQQ", qqq_data, length=20)
        
        # Define take profit and stop loss percentages
        take_profit_percent = 0.02  # 2% profit
        stop_loss_percent = 0.01    # 1% loss
        
        # Current price data
        current_price = qqq_data[-1]["QQQ"]["close"]
        previous_price = qqq_data[-2]["QQQ"]["close"]
        
        allocation = {}
        
        # Strategy logic - Buy if current price is above the 20 day SMA, and previous close was below
        if current_price > sma20[-1] and previous_price < sma20[-2]:
            log("QQQ meets buy criteria")
            allocation["QQQ"] = Percent(1, take_profit_percent, stop_loss_percent)
        else:
            # No action if criteria not met, or hold existing position without adding to it.
            allocation["QQQ"] = 0
        
        return TargetAllocation(allocation)