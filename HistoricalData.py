import pandas as pd
from datetime import datetime
from Information import Information
import time
import numpy as np


class HistoricalData(Information):

    def __init__(self):  # Dataframeを作成する
        super().__init__()

        since = (time.time() - self.starting_time_from * 60) * 1000

        self.fetchdata = pd.DataFrame(self.bitmex.fetch_ohlcv(self.product, '5m', since, 500))
        self.fetchdata.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

        self.ewma = pd.DataFrame()

        self.ewma['long'] = self.fetchdata['close'].ewm(span=self.long_period, adjust=True).mean()
        self.ewma['short'] = self.fetchdata['close'].ewm(span=self.short_period, adjust=True).mean()


    def renew_data(self):

        since = (time.time() - self.starting_time_from * 60) * 1000

        self.fetchdata = pd.DataFrame(self.bitmex.fetch_ohlcv(self.product, '5m', since, 500))
        self.fetchdata.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

        self.ewma['long'] = self.fetchdata['close'].ewm(span=self.long_period, adjust=True).mean()
        self.ewma['short'] = self.fetchdata['close'].ewm(span=self.short_period, adjust=True).mean()
