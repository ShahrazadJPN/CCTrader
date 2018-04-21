from Information import Information
import time
import pandas as pd
from datetime import datetime as dt


class Recorder(Information):

    def __init__(self):
        super().__init__()

    def market_recorder(self, path):

        current_price = self.bitmex.fetch_ticker(symbol=self.product)['last']

        time_ = time.time()

        print(time_)

        w = pd.DataFrame([[time_, current_price, current_price]])  # 取得したティッカーをデータフレームに入れる

        w.to_csv(path, index=False, encoding="utf-8", mode='a', header=False)  # append to the CSV

    def balance_recorder(self, balance, order_price, time_):

        time_ = dt.fromtimestamp(time_)

        w = pd.DataFrame([[balance, time_, order_price]])

        w.to_csv(self.recording_path, index=False, encoding="utf-8", mode='a', header=False)    # append to the CSV

        print("資産：", str(balance), "売買価格：", str(order_price))


if __name__ == '__main__':

    rec = Recorder()

    while True:
        try:
            rec.market_recorder(rec.path)  #
            time.sleep(300)                             # every 5 mins
        except:
            time.sleep(2)
            import traceback
            traceback.print_exc()
