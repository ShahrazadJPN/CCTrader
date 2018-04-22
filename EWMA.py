import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.ticker import ScalarFormatter


class EWMA():

    # def __init__(self):
    #    super().__init__()

    def draw_graph(self):
        fig, ax1 = plt.subplots()

        self.ewm = pd.read_csv('1min.csv', names = ['long', 'short', 'price', 'time', 'volume'], parse_dates=['time'])

        # self.ewm['price'] = self.fetchdata['close']
        # self.ewm['time'] = self.fetchdata['timestamp']
        # self.ewm['time'] = self.ewm['time'].apply(lambda x: datetime.fromtimestamp(x/1000))
        # self.ewm['volume'] = self.fetchdata['volume']

        # self.ewm.to_csv('1min.csv',index=False, encoding="utf-8", mode='a', header=False)

        print(self.ewm)

        s = self.ewm['time']
        fig.autofmt_xdate()
        ax1.plot(s, self.ewm['volume'], 'g', label='volume')
        ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax1.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))

        ax2 = ax1.twinx()
        ax2.plot(s, self.ewm['price'], 'r', label='price')
        plt.xticks()
        plt.xlabel("Date", fontsize=15, fontname='serif')  # x軸のタイトル
        plt.ylabel("Price", fontsize=15, fontname='serif')  # y軸
        plt.title("Chart", fontsize=20, fontname='serif')  # タイトル
        plt.legend()

        plt.show()


if __name__ == '__main__':

    e = EWMA()
    e.draw_graph()
