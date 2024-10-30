from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from datetime import datetime, timedelta

class TradingStrategy(Strategy):
    def __init__(self):
        self.asset = "QQQ"
        self.trade_open = False
        self.entry_time = None
        self.entry_price = 0
        self.stop_loss = 0.80  # 20% stop loss
        self.take_profit = 1.05  # 5% take profit (example value)
        self.trade_duration = timedelta(minutes=30)
        self.allowed_trade_start = datetime.strptime("09:40", "%H:%M").time()

    @property
    def assets(self):
        return [self.asset]

    @property
    def interval(self):
        return "2min"

    def check_time_for_trade(self, current_time):
        # Allow trade if it's past allowed_trade_start time and within trading hours
        return current_time.time() > self.allowed_trade_start

    def should_exit_trade(self, current_price):
        # Check if criteria for exiting the trade are met (stop loss, take profit, duration)
        profit_loss_ratio = current_price / self.entry_price
        elapsed_time = datetime.now() - self.entry_time
        if (profit_loss_ratio <= self.stop_loss or profit_loss_ratio >= self.take_profit or elapsed_time >= self.trade_duration):
            return True
        return False

    def run(self, data):
        current_price = data["ohlcv"][-1][self.asset]["close"]  # Get the latest price of QQQ
        current_time = datetime.now()

        # Check if already in a trade
        if self.trade_open:
            if self.should_exit_trade(current_price):
                self.trade_open = False
                return TargetAllocation({self.asset: 0})  # Exit trade
        else:
            # Check if it's the right time to initiate a trade
            if self.check_time_for_trade(current_time):
                self.trade_open = True
                self.entry_time = current_time
                self.entry_price = current_price
                return TargetAllocation({self.asset: 1})  # Enter trade

        # Default to holding the current position if no criteria are met
        return TargetAllocation({self.asset: 1 if self.trade_open else 0})