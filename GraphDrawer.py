import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


df = pd.read_csv('record.csv',
                 header=None,
                 names=['Bitcoin', 'Date', 'Price', 'USD'],
                 parse_dates=['Date'])

print(df)

d = df['Date']

fig, ax1 = plt.subplots()
ax1.plot(d, df['Bitcoin'], 'g', label='Bitcoin balance')
ax2 = ax1.twinx()
ax2.plot(d, df['USD'], 'r')
ax1.set_xticklabels(d, rotation=45)
ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H'))
plt.xlabel("Date", fontsize=15, fontname='sans-serif')  # x軸のタイトル
plt.ylabel("USD", fontsize=11, fontname='sans-serif')  # y軸
plt.title("Balance History", fontsize=15, fontname='sans-serif')  # タイトル
handler1, label1 = ax1.get_legend_handles_labels()
handler2, label2 = ax2.get_legend_handles_labels()
ax1.legend(handler1 + handler2, label1 + label2)
plt.tight_layout()
plt.show()
