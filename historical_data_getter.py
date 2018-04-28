from Information import Information
import pandas as pd
from datetime import datetime
import time


class Getter(Information):

    def __init__(self):
        super().__init__()
        self.start_time = 172800
        self.time_now = time.time()
        self.fetchdata = None
        self.header = True

    def getter(self):

        since = self.since_setter()

        self.fetchdata = pd.DataFrame(self.bitmex.fetch_ohlcv(self.product, '1m', since, 500))
        self.fetchdata.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

        self.fetchdata['long'] = self.fetchdata['close'].ewm(span=self.long_period, adjust=True).mean()
        self.fetchdata['short'] = self.fetchdata['close'].ewm(span=self.short_period, adjust=True).mean()

        self.fetchdata['timestamp'] = self.fetchdata['timestamp'].apply(lambda x: datetime.fromtimestamp(x / 1000))

        self.fetchdata.to_csv('120days_ohlcv.csv', index=False, encoding="utf-8", mode='a', header=self.header)

    def since_setter(self):

        since = (time.time() - self.start_time * 60) * 1000

        self.start_time = self.start_time - 498

        return since

    def since_counter(self):

        if self.start_time < 498:
            return False
        else:
            return True

    def forer(self):

        while self.since_counter():
            self.getter()
            self.header = False
            print('in progress')
            time.sleep(0.5)


if __name__ == '__main__':
    c = Getter()
    c.forer()
