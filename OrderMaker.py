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

    def cancel_parent_order(self, order_id):
        """
        Nomen est omen
        :param order_id:
        :return:
        """
        self.api.cancelparentorder(product_code=self.product,
                                   parent_order_acceptance_id=order_id)
        time.sleep(2)

    def profit_price_decider(self, order_side, order_price):

        """
        発注する際の利確ラインを決定する
        :return:
        """

        self.orderbook_getter()

        ask_size = 0
        ask_price = 0

        bid_size = 0
        bid_price = 0

        default_target = 300

        bottom_line = 400  # 最低でもこの価格までは利確を待つ
        upper_line = 1200  # 最高でもこの価格までで利確する

        if order_side == "buy":

            for ask in asks:
                if (bottom_line <= ask['price'] - order_price <= upper_line) and (ask['_size'] >= ask_size):
                    ask_size = ask['_size']
                    ask_price = ask['price']
                    if ask_size >= 2:
                        break

            if ask_price == 0:
                ask_price = order_price + default_target
            elif -100 <= int(order_price - ask_price) <= 100:
                ask_price += 200

            return int(ask_price - 10)

        elif order_side == "sell":
            for bid in bids:
                if (bottom_line <= order_price - bid['price'] <= upper_line) and (bid['_size'] >= bid_size):
                    bid_size = bid['_size']
                    bid_price = bid['price']
                    if bid_size >= 2:
                        break

            if bid_price == 0:
                bid_price = order_price - default_target
            elif -100 <= int(order_price - bid_price) <= 100:
                bid_price -= 200

            return int(bid_price + 10)

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

        data = self.order_base_maker(first_side, order_price)

        opposite_side = 'sell' if first_side == 'buy' else 'buy'
        uniq_id = int(time.time())

        self.bitmex.create_limit_order(self.product, first_side, size, order_price, {
            'contingencyType': 'OneTriggersTheOther',
            'clOrdLinkID': uniq_id,
        })
        self.bitmex.create_limit_order(self.product, opposite_side, size, data['profit_line'], {
            'contingencyType': 'OneCancelsTheOther',
            'clOrdLinkID': uniq_id,
        })
        self.bitmex.create_order(self.product, 'StopLimit', opposite_side, size, data['loss_line'], {
            'contingencyType': 'OneCancelsTheOther',
            'stopPx': data['loss_line'],
            'orderQty': size,
            'price': data['loss_line'],
            'clOrdLinkID': uniq_id,
        })

        print("ordered: " + first_side, str(first_side) + "BTC at the price of " + str(order_price))
        self.recorder.balance_recorder(balance, order_price)
        time.sleep(1)

    def order_base_maker(self, order_side, order_price):

        loss = None
        opposite = None

        if order_side == "buy":

            opposite = "sell"

            loss = int(order_price - self.lost_price)  # 同上、損切ライン

        elif order_side == "sell":

            opposite = "buy"

            loss = int(order_price + self.lost_price)  # 同上、損切ライン

        profit = self.profit_price_decider(order_side, order_price)

        data = {'execution_side': opposite, 'loss_line': loss, 'profit_line': profit}

        return data
