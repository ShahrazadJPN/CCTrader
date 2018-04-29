from Information import Information
from HistoricalData import HistoricalData
from datetime import datetime
from Recorder import Recorder
from OrderMaker import OrderMaker


class ConditionChecker(Information):
    """
    HitoricalDataとInformationから情報をもらってきて、取引すべき状態か否かチェックする。
    取引を行うと判断した場合には、OrderMakerへ指令を投げ、発注させる。
    HistoricalDataからはcsvに保存されている取引履歴を貰っている
    InformationからはAPIの情報をもらっている
    """

    def __init__(self):
        super().__init__()
        self.order_maker = OrderMaker()
        self.trade_history = HistoricalData()

        self.recorder = Recorder()

        self.df_tail = self.trade_history.ewma.tail(1)    # csvの最後の一行＝最新データを切り取る
        self.ticker_tail = self.trade_history.fetchdata.tail(2)

        self.ewma_1day = self.df_tail['long'].iloc[0]
        self.ewma_6hours = self.df_tail['short'].iloc[0]

        self.order_side = 'buy/sell'  # Will be buy or sell

        self.current_price = self.bitmex.fetch_ticker(symbol=self.product)['last']
        self.current_volume = self.ticker_tail['volume'].iloc[0]
        self.current_open = self.ticker_tail['open'].iloc[0]
        self.current_close = self.ticker_tail['close'].iloc[0]

        self.orders = []                    # 現在の注文が入る
        self.positions = []                 # 現在のポジションが入る
        self.ordering_price = 0             # 注文中の価格が入る

        self.market_flow = "SLEEP"          # 市場の流れ
        self.signal = False                 # True for GO, False for STOP

        self.last_ordered_open = 0                                           # A bin's open price
        self.balance = self.bitmex.fetch_balance()['BTC']['total'] * 0.9985  # 証拠金残高

        self.order_id = None
        self.ordering = False               # 注文中か否か確認用
        self.positioning = False            # ポジションあるか否か確認用

        self.orderbook = self.bitmex.fetch_order_book('BTC/USD')
        self.bid = self.orderbook['bids'][0][0] if len(self.orderbook['bids']) > 0 else None
        self.ask = self.orderbook['asks'][0][0] if len(self.orderbook['asks']) > 0 else None
        self.spread = (self.ask - self.bid) if (self.bid and self.ask) else None

        self.waiting_time = self.default_waiting_time      # キャンセルまでの待ち時間(sec)

    def market_reader(self):
        """
        現在、市場が上昇傾向なのか下落傾向なのかを判断する。
        """

        if self.current_volume > self.volume_threshold:

            print(self.current_open, self.current_close, ' <- OPEN and Close')

            if self.current_open > self.current_close:
                market = "UP"
                self.order_side = "buy"

            elif self.current_open < self.current_close:
                market = "DOWN"
                self.order_side = "sell"

            else:
                market = "SLEEP"

        else:
            market = "SLEEP DUE TO VOLUME THRESHOLD"

        print(market)

        self.market_flow = market

    def renew_chart_data(self):
        """
        CSVに保存されているチャート情報が更新されていると思われるので、最新の状態を読み込みに行く
        かつ、これまで保持していた古い情報を最新の情報へアップデートする
        market_readerなどから使う
        """

        self.trade_history.renew_data()
        self.df_tail = self.trade_history.ewma.tail(1)
        self.ticker_tail = self.trade_history.fetchdata.tail(2)
        self.current_open = self.ticker_tail['open'].iloc[0]
        self.current_close = self.ticker_tail['close'].iloc[0]
        self.current_volume = self.ticker_tail['volume'].iloc[0]

        self.ewma_6hours = self.df_tail['short'].iloc[0]
        self.ewma_1day = self.df_tail['long'].iloc[0]

    def board_status_checker(self):
        """
        スプレッドが大きく開いている時に止めさせる
        """
        if self.spread <= self.spread_limit:
            self.signal = True
        else:
            self.signal = False

    def position_checker(self):

        """
        現在のポジションを確認し、すでにある場合には余計な発注動作をさせないようにする
        """

        positions = self.bitmex.private_get_position()

        if positions:
            no_position = True if positions[0]['simpleQty'] == 0 else False
        else:
            no_position = True

        if no_position:                     # ポジションなし
            self.signal = True
            self.positioning = False
        else:                                  # ポジションあり
            self.signal = False
            self.positioning = True              # 購入サインを消し、ポジション有のフラグを立てる

        self.positions = positions

    def order_checker(self):
        """
        発注しているのかいないのか確認する
        :return:
        """

        self.orders = self.bitmex.fetch_open_orders(symbol=self.product)

        if not self.orders:
            self.signal = True
            self.ordering = False
        else:
            self.signal = False
            self.ordering = True
            self.order_id = self.orders[0]['info']['orderID']     # 注文中ならばオーダーIDを取得しておく

    def only_position_checker(self):
        """
        ポジションだけがあり、注文がない状態になっていないか確認する
        →Trueならば決済注文を行う処理を呼び出す
        :return:
        """
        if self.positioning and self.ordering is False:

            position_size = 0

            for position in self.positions:
                position_size += abs(position['simpleCost'])     # 全ポジションを確実に解消

            position_price = int(self.positions[0]['avgCostPrice'])    # 値段はまあよい
            position_side = 'buy' if self.positions[0]['simpleQty'] > 0 else 'sell'

            order = self.order_maker.oco_order_maker(position_side, position_size, position_price)  # 決済注文を入れる

            print("OCO ORDER SENT:", order)

    def only_order_checker(self):
        """
        ポジションはないが、注文だけが行われている状態で発動する
        →発注から時間が経過していれば、一度注文を解除する指令を出す
        :return:
        """

        if self.ordering and self.positioning is False:
            ordered_time = self.orders[0]['datetime']        # 注文を入れた時刻
            ordered_time = ordered_time.replace("T", " ")
            ordered_time = ordered_time.replace("Z", "")

            if ordered_time.find(".") == -1:
                ordered_time = datetime.strptime(ordered_time, '%Y-%m-%d %H:%M:%S')
                ordered_time = ordered_time.timestamp()
            else:
                ordered_time = datetime.strptime(ordered_time, '%Y-%m-%d %H:%M:%S.%f')
                ordered_time = ordered_time.timestamp()

            passed_time = datetime.now().timestamp() - ordered_time  # 注文を入れてからの経過時間

            print('Time till cancelling:', self.waiting_time + 32400 - passed_time)

            passed_time = self.waiting_time + 32400 - passed_time

            if passed_time < 0:     # 一定時間以上約定なし
                self.order_maker.cancel_parent_order(self.order_id)
                self.waiting_time = self.default_waiting_time            # キャンセルできたらキャンセル待ち時間を初期設定に戻す

    def order_actually_dead_checker(self):
        """
        現在のBTC価格と、自分の発注価格とを比較する
        無理そうならばwaiting_timeを変更し、注文キャンセルの方向へ持っていく
        :return:
        """
        self.current_price_getter()

        if self.ordering:
            self.ordering_price = self.orders[0]['price']   # 注文中の価格

        if abs(self.current_price - self.ordering_price) >= self.cancelling_line:
            self.waiting_time = 45

    def emergency_checker(self):
        """
        ヤバそうなときにポジションを閉じる
        :return:
        """

        if self.positioning:                                                # ポジションがあるとき
            self.current_price_getter()
            position_size = 0

            for position in self.positions:
                position_size += abs(position['simpleCost'])                # 全ポジションを確実に解消

            position_price = int(self.positions[0]['avgCostPrice'])         # ポジション価格取得
            position_side = 'buy' if self.positions[0]['simpleQty'] > 0 else 'sell'

            if ((position_side == 'buy' and (position_price - self.current_price) > self.lost_price) or
               (position_side == 'sell' and (position_price - self.current_price) < self.lost_price * -1)):
                self.order_maker.cancel_parent_order(self.order_id)
                self.order_maker.stop_order_maker(position_side, position_size)
        else:
            pass

    def current_price_getter(self):
        """
        ときどき現在価格を取得するための関数
        :return:
        """
        self.current_price = self.bitmex.fetch_ticker(symbol=self.product)['last']

    def current_balance_getter(self):

        self.balance = self.bitmex.fetch_balance()['BTC']['total'] * 0.995

    def order_information_checker(self):
        """
        注文に必要な情報を収集し、実際の注文指示を出す
        :return:
        """
        if self.market_flow == "UP":
            order_side = "buy"
        elif self.market_flow == "DOWN":
            order_side = "sell"
        else:
            order_side = "NONE"

        if self.current_open == self.last_ordered_open:
            print('Only an order a minute')
        elif order_side == "buy" or order_side == "sell":
            self.current_price_getter()
            self.current_balance_getter()
            purchasable_btc = self.balance * self.current_price
            order_size = int(purchasable_btc)
            order_price = self.current_price
            order_type = 'Market'               # Todo: いつか可変にする

            self.order_maker.ifdoco_order_maker(order_side, order_size, order_price, self.balance, order_type)

            self.last_ordered_open = self.current_open
        else:
            pass

    def orderbook_getter(self):
        """
        updates orderbook
        :return:
        """
        self.orderbook = self.bitmex.fetch_order_book(symbol=self.product)
        self.bid = self.orderbook['bids']
        self.ask = self.orderbook['asks']
        self.spread = (self.ask[0][0] - self.bid[0][0])
