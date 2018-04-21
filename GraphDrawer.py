import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('record.csv',
                 header=None,
                 names=['Balance', 'Date', 'Price'],
                 parse_dates=['Date'])

print(df)

df.plot(y='Balance', x='Date')
plt.show()
