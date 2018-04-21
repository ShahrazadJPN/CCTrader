import matplotlib.pyplot as plt
from HistoricalData import HistoricalData
from datetime import datetime


class EWMA(HistoricalData):

    def __init__(self):
        super().__init__()

    def draw_graph(self):
        self.ewma['price'] = self.fetchdata['close']
        self.ewma['time'] = self.fetchdata['timestamp']
        self.ewma['time'] = self.ewma['time'].apply(lambda x: datetime.fromtimestamp(x/1000))
        print(self.ewma)
        self.ewma.plot(x='time')
        plt.xlabel("Date", fontsize=15, fontname='serif')  # x軸のタイトル
        plt.ylabel("Price", fontsize=15, fontname='serif')  # y軸
        plt.title("Chart", fontsize=20, fontname='serif')  # タイトル
        plt.show()


if __name__ == '__main__':

    e = EWMA()
    e.draw_graph()
