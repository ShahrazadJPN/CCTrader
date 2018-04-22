import matplotlib.pyplot as plt
from HistoricalData import HistoricalData
from datetime import datetime
import pandas as pd
from matplotlib.ticker import ScalarFormatter

class EWMA(HistoricalData):

    def __init__(self):
        super().__init__()

    def draw_graph(self):
        fig, ax1 = plt.subplots()
        self.ewma['price'] = self.fetchdata['close']
        self.ewma['time'] = self.fetchdata['timestamp']
        self.ewma['time'] = self.ewma['time'].apply(lambda x: datetime.fromtimestamp(x/1000))
        self.ewma['volume'] = self.fetchdata['volume']

        self.ewma['time'] = pd.to_datetime(self.ewma['time'])
        print(self.ewma)
        print(self.ewma.index)

        s = self.ewma['time']

        ax1.plot(s, self.ewma['volume'], 'g', label='volume')
        ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax1.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
        ax2 = ax1.twinx()
        ax2.plot(s, self.ewma['price'], 'r', label='price')
        plt.xlabel("Date", fontsize=15, fontname='serif')  # x軸のタイトル
        plt.ylabel("Price", fontsize=15, fontname='serif')  # y軸
        plt.title("Chart", fontsize=20, fontname='serif')  # タイトル
        plt.legend()
        plt.show()


if __name__ == '__main__':

    e = EWMA()
    e.draw_graph()
