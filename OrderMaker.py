from Information import Information
import time
from Recorder import Recorder


class OrderMaker(Information):
    """
    InformationからはAPIの情報だけをもらっておく
    実際にオーダーを行うときは、Mainから指令を受ける
    """
    def __init__(self):
        super().__init__()
        self.recorder = Recorder()

    def oco_order_maker(self, position_side, position_size, position_price):

        data = self.order_base_maker(position_side, position_price)
        uniq_id = time.time()

        self.bitmex.create_limit_order(self.product, data['opposite_side'], position_size, data['profit_line'], {
            'contingencyType': 'OneCancelsTheOther',
            'clOrdLinkID': uniq_id,
        })
        self.bitmex.create_order(self.product, 'StopLimit', data['opposite_side'], position_size, data['loss_line'], {
            'contingencyType': 'OneCancelsTheOther',
            'stopPx': data['loss_line'],
            'orderQty': position_size,
            'price': data['loss_line'],
            'clOrdLinkID': uniq_id,
        })

    def cancel_parent_order(self, order_id):
        """
        Nomen est omen
        :param order_id:
        :return:
        """

        self.bitmex.cancel_order(order_id)

        time.sleep(1)

    def ifdoco_order_maker(self, first_side, size, order_price, balance):
        """
        IFDOCOオーダーを発注する
        取引の要
        :param first_side:
        :param size:
        :param order_price:
        :param balance
        :return:
        """

        order_price = order_price - 3 if first_side == 'buy' else order_price + 3

        data = self.order_base_maker(first_side, order_price)

        opposite_side = 'sell' if first_side == 'buy' else 'buy'
        uniq_id = int(time.time())

        self.bitmex.create_limit_order(self.product, first_side, size, order_price, {           # first order
            'contingencyType': 'OneTriggersTheOther',
            'clOrdLinkID': uniq_id,
        })
        self.bitmex.create_limit_order(self.product, opposite_side, size, data['profit_line'], {    # profit order
            'contingencyType': 'OneCancelsTheOther',
            'clOrdLinkID': uniq_id,
        })
        self.bitmex.create_order(self.product, 'StopLimit', opposite_side, size, data['loss_line'], {   # loss order
            'contingencyType': 'OneCancelsTheOther',
            'stopPx': data['loss_line'],
            'orderQty': size,
            'price': data['loss_line'],
            'clOrdLinkID': uniq_id,
        })

        print("ordered: " + str(first_side) + "BTC at the price of " + str(order_price))
        self.recorder.balance_recorder(balance, order_price, uniq_id)
        time.sleep(1)

    def order_base_maker(self, order_side, order_price):

        profit = None
        loss = None
        opposite = None

        if order_side == "buy":

            opposite = "sell"

            profit = float(order_price + self.profit_price)
            loss = float(order_price - self.lost_price)  # 同上、損切ライン

        elif order_side == "sell":

            opposite = "buy"

            profit = float(order_price - self.profit_price)
            loss = float(order_price + self.lost_price)  # 同上、損切ライン

        data = {'execution_side': opposite, 'loss_line': loss, 'profit_line': profit}

        return data