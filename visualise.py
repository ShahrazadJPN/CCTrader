import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

#空のデータフレームを作成 = お金残高用
account = pd.DataFrame(index=[], columns=['money','time'])

#df = pd.read_csv("http://api.bitcoincharts.com/v1/trades.csv?symbol=coincheckJPY",

df = pd.read_csv("1min.csv",
                 header=None,
                 parse_dates=True,
                 date_parser=lambda x: datetime.fromtimestamp(float(x)),
                 names=['price', 'time', 'amount'],
                 )

df.set_index('time')

df["price"].plot()
#df['ewma5'] = pd.ewma(df['price'],span=21000) # だいたい一日あたりの加重移動平均
df['ewma1day'] = pd.ewma(df['price'],span=190000) # 1日の加重移動平均
df['ewma5days'] = pd.ewma(df['price'],span=580000) # だいたい5日あたりの加重移動平均
df['ewma25days'] = pd.ewma(df['price'],span=14400) # だいたい25日あたりの加重移動平均
df['ewma1day'].plot()
df['ewma5days'].plot()
df['ewma25days'].plot()
df['divergence'] = (df['price'] - df['ewma25days']) / df['ewma25days'] * 100 # 5 日移動平均に対する界入り率
df['1dayDiv'] = (df['price'] - df['ewma1day']) / df['ewma1day'] * 100 # 1日移動平均に対するそのときの乖離率
df['5dayDiv'] = (df['price'] - df['ewma5days']) / df['ewma5days'] * 100 # 5日移動平均に対するそのときの乖離率
df['ewma10days'] = pd.ewma(df['price'],span=480)
df['ewma3h'] = pd.ewma(df['price'],span=24000)
df['ewma5mins'] = pd.ewma(df['price'], span=666)
df['ewma1min'] = pd.ewma(df['price'], span= 140)
df['ewma3h'].plot()

# api = pybitflyer.API(api_key="WR95knYrj36CabGWHK1gdV", api_secret="2Gv0skryfEFZTBnJ3/WocvSrRVeIbi1vzsZ9sAurqaU=")

bought = False
sold = False
pos = False # ポジション有無
money = 20000 # 1,000,000円
btc = 0
i = -1
gotPrice = 1
market = "NONE"

# Info = apiInfo.Bitflyer()

for div in df['divergence']: # divは25日平均

    # df.iloc[i,0] <=これがその時のBTCの値段

    i += 1
    lastprofit = df.iloc[i,0]

   # dayDiv = df.iloc[i,6] # 1日移動平均に対する乖離率
   # days5Div = df.iloc[i,7] # 5日移動平均に対する乖離率

    ewma1 = df.iloc[i,2] # 一日移動平均
    ewma3 = df.iloc[i,3]
   # ewma25 = df.iloc[i,4]
    ewma360 = df.iloc[i,8]
    ewma3h = df.iloc[i,9]
    ewma5mins = df.iloc[i,10]
    ewma1min = df.iloc[i,11]

    failed = df.iloc[i,0] - gotPrice  # 現在のポジションの取得値/現在値 <97% or 103%> で諦める？

    price_now = df.iloc[i,0]

    size = df.iloc[i,1]

    if size <= 0.01:
        continue

    currentPrice = df.iloc[i,0]

    if market == "UP":
        targetPrice = lastprofit * 0.9996
    elif market == "DOWN":
        targetPrice = lastprofit * 1.0004
    elif market == "UPWRONG":
        targetPrice = lastprofit * 0.999
    elif market == "DOWNWRONG":
        targetPrice = lastprofit * 1.001
    else:
        targetPrice = currentPrice

    diver = (targetPrice - currentPrice) / targetPrice * 100

    orderbtc = money / df.iloc[i, 0]

    size = df.iloc[i, 1] # amount

    time = df.index.values[i]
    ts = (time - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    time = pd.Timestamp(time)

    if abs(diver) >= 1:
        targetPrice = currentPrice

    print("Current Target Price:",targetPrice, "Market is ", market)
    print("Current Price is:", currentPrice)

    giveBought = -3000
    giveSold = 3000

    if orderbtc > size :     # 注文量より取引高が少ないならパス(取引できない？)
        continue
    elif  pos is False and ((df.iloc[i,0] > ewma1min > ewma5mins) or (price_now < ewma5mins and ewma1min > ewma5mins)): #and  ewma1 > ewma3  :  #div > 4 and pos is False and ewma1 > ewma5: # 25日平均に対する乖離率3%以上、上がり基調なので流れに乗って買う

        if currentPrice <= targetPrice:
            btc = money/df.iloc[i,0]
            money = df.iloc[i,0]*btc
            #print ("bought btc having = "+ str(btc))
            bought = True
            pos = True
            gotPrice = df.iloc[i,0]
            series = pd.Series([money,time],index=account.columns)
            account = account.append(series, ignore_index=True)

    elif pos is False and ((df.iloc[i,0] < ewma1min < ewma5mins) or (price_now > ewma5mins and ewma1min < ewma5mins)) : #and ewma1 < ewma3  : #div < -4 and pos is False and ewma1 < ewma5: # 同上、下げ基調

        if currentPrice >= targetPrice:
            btc = money/df.iloc[i,0]
            money = df.iloc[i, 0] * btc
            #print ("sold btc having = "+ str(btc))
            sold = True
            pos = True
            gotPrice = df.iloc[i, 0]
            series = pd.Series([money,time],index=account.columns)
            account = account.append(series, ignore_index=True)

    elif failed < giveBought and bought: # 買いポジション持ちだが、値段が下がってきたら諦めてポジション解消。-1%
        money = btc * df.iloc[i,0]
        btc = 0
        #print ("諦めた" + str(money))
        bought = False
        pos = False
        gotPrice = 1
        series = pd.Series([money,time],index=account.columns)
        account = account.append(series, ignore_index=True)
        lastprofit = df.iloc[i,0]
        market = "UPWRONG"
        print("-------------ACUTUALLY LOST--------------")
    elif failed > giveSold and sold: # 上記の逆。 +1%1
        money = (btc * gotPrice) + ((btc * gotPrice) - (btc * df.iloc[i,0]))
        btc = 0
       #print ("諦めた" + str(money))
        sold = False
        pos = False
        gotPrice = 1
        series = pd.Series([money,time],index=account.columns)
        account = account.append(series, ignore_index=True)
        lastprofit = df.iloc[i,0]
        market = "DOWNWRONG"
        print("-------------ACUTUALLY LOST--------------")
    elif failed > 700 and bought:  # 買いポジのあるときは0.03%値上がりで利確する
        money = btc * df.iloc[i,0]
        btc = 0
        bought = False
        pos = False
        gotPrice = 1
        series = pd.Series([money,time],index=account.columns)
        account = account.append(series, ignore_index=True)
        lastprofit = df.iloc[i,0]
        market = "UP"
        print("-------------ACUTUALLY WON--------------")
    elif failed < -700 and sold: # 売りポジのときは0.03%値下がり
        money = (btc * gotPrice) + ((btc * gotPrice) - (btc * df.iloc[i,0]))
        btc = 0
        sold = False
        pos = False
        gotPrice = 1
        series = pd.Series([money,time], index=account.columns)
        account = account.append(series, ignore_index=True)
        lastprofit = df.iloc[i,0]
        market ="DOWN"
        print("-------------ACUTUALLY WON--------------")

    print(i)

#print(account)

account.plot(x='time',y = 'money')

plt.show()