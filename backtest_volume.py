import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime
import numpy as np
import numba
from collections import OrderedDict


class BackTester():

    def __init__(self):
        self.margin = {}
        self.order = {}

    # @numba.jit()
    def MakingProfitLine_B(self):
        val = self.order['price']+(self.margin['profit']+(self.order['price']*self.margin['profit_rate']))
        print('元値:'+str(self.order['price'])+'利確ライン:'+str(val))
        return val

    # @numba.jit()
    def MakingStopLine_B(self):
        val = self.order['price']-(self.margin['lost']+(self.order['price']*self.margin['lost_rate']))
        print('元値:'+str(self.order['price'])+'損切ライン:'+str(val))
        return val

    # @numba.jit()
    def MakingProfitLine_S(self):
        val = self.order['price']-(self.margin['profit']+(self.order['price']*self.margin['profit_rate']))
        print('元値:'+str(self.order['price'])+'利確ライン:'+str(val))
        return val

    # @numba.jit()
    def MakingStopLine_S(self):
        val = self.order['price']+(self.margin['lost']+(self.order['price']*self.margin['lost_rate']))
        print('元値:'+str(self.order['price'])+'損切ライン:'+str(val))
        return val

    @numba.jit()
    def volume_handler(self, vol):
        if vol > self.threshold:
            return True
        else:
            return False

    @numba.jit()
    def direction(self):
        pass

    @numba.jit()
    def entry_decider(self, current):
        if current['simple_vol'] > self.threshold['volume']:  # vol is quite abundant
            if current['open'] > current['close']:
                self.order['price'] = current['price'] - self.margin['order']
                self.order['price_cancel_entry'] = current['price'] + self.margin['order_cancel']
                current['pos'] = 'bought_w'
                self.order['size'] = self.money / current['price']
                self.order['profitline'] = self.MakingProfitLine_B()
                self.order['stopline'] = self.MakingStopLine_B()
                self.counter['bpos'] += 1
                current['pos'] = 'bought'
                self.money = self.money - (self.order['size'] * self.order['price'])
            elif current['open'] < current['close']:  # 売りポジ
                self.order['price'] = current['price'] + self.margin['order']
                self.order['price_cancel_entry'] = current['price'] - self.margin['order_cancel']
                current['pos'] = 'sold_w'
                self.order['size'] = self.money / current['price']
                self.order['profitline'] = self.MakingProfitLine_S()
                self.order['stopline'] = self.MakingStopLine_S()
                current['pos'] = 'sold'
                self.counter['spos'] += 1
                self.money = self.money + (self.order['size'] * self.order['price'])
        return current

    @numba.jit()
    def mainpart(self):

        # -----
        # Initial Setting
        # -----

        self.money = 200        # unit = $
        self.threshold = {
            'volume': 1_000_000,
            'div': 0.01,
        }
        self.margin = {
            "order": 0,          # margin price for order
            "order_cancel": 10,
            "profit": 35,        # unit = $
            "profit_rate": 0,    # unit = [100%]
            "lost": 25,          # unit = $
            "lost_rate": 0,      # unit = [100%]
        }
        span = {
            "long": 500,
            "short": 60,
            "volume": 10,
        }

        self.counter = OrderedDict()
        self.counter['bpos'] = 0
        self.counter['bposprofit'] = 0
        self.counter['bposlost'] = 0
        self.counter['spos'] = 0
        self.counter['sposprofit'] = 0
        self.counter['sposlost'] = 0
        self.counter['volume'] = 0

        cashier = OrderedDict()
        cashier['bposprofit'] = 0
        cashier['bposlost'] = 0
        cashier['sposprofit'] = 0
        cashier['sposlost'] = 0

        current = {
            'pos': 'none',
        }
        self.order = {}

        #空のデータフレームを作成 = 残高用
        account = pd.DataFrame(index=[], columns=['money','time'])

        #空のデータフレームを作成 = 利確記録用
        profitdate = pd.DataFrame(index=[], columns=['time','money'])

        #空のデータフレームを作成 = 損切記録用
        lostdate = pd.DataFrame(index=[], columns=['time','money'])

        data = pd.read_csv("120days_ohlcv.csv",
                           index_col='datetime',
                           # names=['datetime', 'price', 'volume'],
                           parse_dates=False,
                           )

        data['price_range'] = data['high'] - data['low']

        data['ewma_long'] = data['close'].ewm(span=span['long'], adjust=True).mean()
        data['ewma_short'] = data['close'].ewm(span=span['short'], adjust=True).mean()
        data['volume_avg'] = data['volume'].ewm(span=span['volume'], adjust=True).mean()

        data['div_long'] = (data['close'] - data['ewma_long']) / data['ewma_long'] * 100 # 長時間移動平均に対する乖離率
        data['div_short'] = (data['close'] - data['ewma_short']) / data['ewma_short'] * 100 # 短時間移動平均に対するそのときの乖離率

        count = 0

        print(data)

        for i, v in data.iterrows():

            count += 1

            if count < span['long']:
                continue

            current['time'] = i
            print(current['time'])
            current['price'] = v['close']
            current['open'] = v['open']
            current['close'] = v['close']
            current['volume'] = v['volume_avg']
            current['ewma_short'] = v['ewma_short']
            current['ewma_long'] = v['ewma_long']
            current['div_short'] = v['div_short']
            current['div_long'] = v['div_long']
            current['simple_vol'] = v['volume']

            #    print ('Time:' + str(i))
            #    print ('Pos:' + str(current['pos']))
            #    print ('Money:' + str(self.money))
            print('Vol' + str(current['volume']))

            if current['pos'] == 'none':
                current = self.entry_decider(current)

            # elif current['pos'] == 'bought_w':               #買いポジエントリーまちの時
            #     if self.order['price'] > current['price']:
            #         self.order['size'] = self.money / current['price']
            #         self.order['profitline'] = self.MakingProfitLine_B()
            #         self.order['stopline'] = self.MakingStopLine_B()
            #         self.counter['bpos'] += 1
            #         current['pos'] = 'bought'
            #         self.money = self.money - (self.order['size'] * self.order['price'])
            #     if self.order['price_cancel_entry'] < current['price']:
            #         current['pos'] = 'none'
            #         print('買いポジエントリー待ちキャンセル')
            #
            # elif current['pos'] == 'sold_w':               #売りポジエントリーまちの時
            #     if self.order['price'] < current['price']:
            #         self.order['size'] = self.money / current['price']
            #         self.order['profitline'] = self.MakingProfitLine_S()
            #         self.order['stopline'] = self.MakingStopLine_S()
            #         current['pos'] = 'sold'
            #         self.counter['spos'] += 1
            #         self.money = self.money + (self.order['size'] * self.order['price'])
            #     if self.order['price_cancel_entry'] > current['price']:
            #         current['pos'] = 'none'
            #         print('売りポジエントリー待ちキャンセル')

            elif current['pos'] == 'bought':                #買いポジ持ってるとき
                if self.order['profitline'] < current['price']:   #利確
                    print('買いポジ利確/利確ライン:'+str(self.order['profitline'])+'現在値:'+str(current['price'])+'エントリー:'+str(self.order['price']))
                    current['pos'] = 'none'
                    self.counter['bposprofit'] += 1
                    cashier['bposprofit'] += self.order['size'] * (self.order['profitline'] - self.order['price'])
                    self.money = self.money + (self.order['size'] * self.order['profitline'])
                    series = pd.Series([self.money, current['time']], index=account.columns)
                    account = account.append(series, ignore_index=True)
                    profitseries = pd.Series([current['time'], current['price']], index=profitdate.columns)
                    profitdate = profitdate.append(profitseries, ignore_index=True)
                elif self.order['stopline'] > current['price']:   #損切り
                    print('買いポジ損切/損切ライン:'+str(self.order['stopline'])+'現在値:'+str(current['price'])+'エントリー:'+str(self.order['price']))
                    current['pos'] = 'none'
                    self.counter['bposlost'] += 1
                    cashier['bposlost'] += self.order['size'] * (self.order['stopline'] - self.order['price'])
                    self.money = self.money + (self.order['size'] * self.order['stopline'])
                    series = pd.Series([self.money, current['time']], index=account.columns)
                    account = account.append(series, ignore_index=True)
                    lostseries = pd.Series([current['time'], current['price']], index=lostdate.columns)
                    lostdate = lostdate.append(lostseries, ignore_index=True)

            elif current['pos'] == 'sold':  # 売りポジ持ってるとき
                if self.order['profitline'] > current['price']:   #利確
                    print('売りポジ利確/利確ライン:'+str(self.order['profitline'])+'現在値:'+str(current['price'])+'エントリー:'+str(self.order['price']))
                    current['pos'] = 'none'
                    self.counter['sposprofit'] += 1
                    self.money = self.money - (self.order['size'] * self.order['profitline'])
                    cashier['sposprofit'] += self.order['size'] * (self.order['price'] - self.order['profitline'])
                    series = pd.Series([self.money, current['time']], index=account.columns)
                    account = account.append(series, ignore_index=True)
                    profitseries = pd.Series([current['time'], current['price']], index=profitdate.columns)
                    profitdate = profitdate.append(profitseries, ignore_index=True)
                elif self.order['stopline'] < current['price']:   #損切り
                    print('売りポジ損切/損切ライン:'+str(self.order['stopline'])+'現在値:'+str(current['price'])+'エントリー:'+str(self.order['price']))

                    current['pos'] = 'none'
                    self.counter['sposlost'] += 1
                    self.money = self.money - (self.order['size'] * self.order['stopline'])
                    cashier['sposlost'] += self.order['size'] * (self.order['price'] - self.order['stopline'])
                    series = pd.Series([self.money, current['time']], index=account.columns)
                    account = account.append(series, ignore_index=True)
                    lostseries = pd.Series([current['time'], current['price']], index=lostdate.columns)
                    lostdate = lostdate.append(lostseries, ignore_index=True)

        #print (account)

        print('------Pos Counter------')
        for key, val in self.counter.items():
            print(key, val)

        print('------Cash Counter------')
        for key, val in cashier.items():
            print(key, val)

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        data["close"].plot(label="label-Price", legend=True, ax=ax1)
        data['ewma_long'].plot(label="ewma long", legend=True, ax=ax1)
        data['ewma_short'].plot(label="ewma short", legend=True, ax=ax1)
        data['div_long'].plot(label="div long", legend=True, ax=ax2, linestyle='dashed')
        data['div_short'].plot(label="div short", legend=True, ax=ax2, linestyle='dashed')
        profitdate.plot(label='profitpoint', x='time', y='money', lw=0, marker='+', markersize=8, markerfacecolor='blue', ax=ax1)
        lostdate.plot(label='lostpoint', x='time', y='money', lw=0, marker='x', markersize=8, markerfacecolor='red', ax=ax1)
        account.plot(x='time', y='money')
        plt.show()

        pd.set_option("display.max_rows", 2000)
        print (data['div_long'])


if __name__ == '__main__':
    c = BackTester()
    c.mainpart()
