import api


class Settings:

    def __init__(self):
        self.api_key = api.api_key              # write your api_key in api.py
        self.api_secret = api.api_secret        # idem
        self.path = "historical_data.csv"       # historical trade data in csv format (not in use)
        self.recording_path = "record.csv"      # your balance history record in csv format
        self.product = "BTC/USD"                # product code
        self.lost_price = 25                    # loss contract price line
        self.cancelling_line = 10               # 現在価格と注文価格の差がこれより大きくなったらwaiting_timeを変更する
        self.default_waiting_time = 900         # waiting time till cancelling orders
        self.profit_price = 35                   # profit contract price line
        self.spread_limit = 0.5                 # spread allowance limit
        self.starting_time_from = 480           # staring time from now for ohlcv fetching, in minutes
        self.long_period = 360                  # numbers of 1 mins candlestick for calculating ewma
        self.short_period = 60                  # numbers of 1 mins candlestick for calculating ewma
        self.last_ordered_price = None          # nomen est omen
        self.order_margin = 4                   # margin price for making orders
        self.volume_threshold = 3_000_000      # when higher than this value starts making orders
