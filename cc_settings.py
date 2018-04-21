import api


class Settings:

    def __init__(self):
        self.api_key = api.api_key              # must be string
        self.api_secret = api.api_secret        # string too
        self.path = "historical_data.csv"       # historical trade data in csv format
        self.recording_path = "record.csv"      # your balance history record in csv format
        self.product = "BTC/USD"                # product code
        self.lost_price = 30                    # loss contract price line
        self.cancelling_line = 10               # 現在価格と注文価格の差がこれより大きくなったらwaiting_timeを変更する
        self.default_waiting_time = 600         # waiting time till cancelling orders
        self.profit_price = 12                  # profit contract price line
        self.spread_limit = 0.5                 # spread allowance limit
        self.starting_time_from = 2160          # staring time from now for ohlcv fetching, in minutes
        self.long_period = 288                  # numbers of 5 mins candlestick for calculating ewma
        self.short_period = 36                  # numbers of 5 mins candlestick for calculating ewma
        self.last_ordered_price = None          # nomen est omen
