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

        ord1 = self.bitmex.create_limit_order(self.product,
                                              data['execution_side'],
                                              position_size,
                                              data['profit_line'],
                                              {
                                               'contingencyType': 'OneCancelsTheOther',
                                               'clOrdLinkID': uniq_id,
                                              }
                                              )
        ord2 = self.bitmex.create_order(self.product,
                                        'StopLimit',
                                        data['execution_side'],
                                        position_size,
                                        params=
                                        {
                                         'contingencyType': 'OneCancelsTheOther',
                                         'stopPx': data['trigger'],
                                         'orderQty': position_size,
                                         'price': data['loss_line'],
                                         'clOrdLinkID': uniq_id,
                                        }
                                        )

        print('profit order:', ord1)
        print('loss exec order', ord2)

        time.sleep(2)

    def cancel_parent_order(self, order_id):
        """
        Nomen est omen
        :param order_id:
        :return:
        """

        self.bitmex.cancel_order(order_id)
        print('order cancelled')
        time.sleep(2)

    def stop_order_maker(self, position_side, size):
        """
        makes stop order to execute loss
        :param position_side:
        :param size:
        :return:
        """
        side = 'buy' if position_side == 'sell' else 'sell'

        self.bitmex.create_market_order(self.product, side, size)

        print('stop market order made')

    def ifdoco_order_maker(self, first_side, size, order_price, balance, order_type):
        """
        IFDOCOオーダーを発注する
        :param first_side:
        :param size:
        :param order_price:
        :param balance      Current Balance
        :param order_type  MARKET or LIMIT
        :return:
        """

        order_price = order_price - self.order_margin if first_side == 'buy' else order_price + self.order_margin

        data = self.order_base_maker(first_side, order_price)

        opposite_side = 'sell' if first_side == 'buy' else 'buy'
        uniq_id = int(time.time())

        if order_type == 'Market':
            ord1 = self.first_market_order_maker_for_ifdoco(first_side, size, uniq_id, order_price, balance)
        else:
            ord1 = self.first_limit_order_maker_for_ifdoco(first_side, size, order_price, uniq_id, balance)

        ord2 = self.bitmex.create_limit_order(self.product,
                                              opposite_side,
                                              size,
                                              data['profit_line'],
                                              {                          # profit order
                                               'contingencyType': 'OneCancelsTheOther',
                                               'clOrdLinkID': uniq_id,
                                              }
                                              )
        ord3 = self.bitmex.create_order(self.product,
                                        'StopLimit',
                                        opposite_side,
                                        size,
                                        params={                      # loss order
                                                'contingencyType': 'OneCancelsTheOther',
                                                'stopPx': data['trigger'],
                                                'orderQty': size,
                                                'price': data['loss_line'],
                                                'clOrdLinkID': uniq_id,
                                                }
                                        )

        print('first order:', ord1)
        print('oco no.1 order:', ord2)
        print('oco no.2 order:', ord3)

        print("ordered: " + str(first_side).capitalize() + ' ' + str(size) + " USD at " + str(order_price))
        self.recorder.balance_recorder(balance, order_price, uniq_id)
        time.sleep(3)

    def first_limit_order_maker_for_ifdoco(self, first_side, size, order_price, uniq_id, balance):
        """
        IFDOCOの一段目を作るやつ。指値注文。
        :return:
        """
        order = self.bitmex.create_limit_order(self.product, first_side, size, order_price, {  # first order
            'contingencyType': 'OneTriggersTheOther',
            'clOrdLinkID': uniq_id,
        })
        self.recorder.balance_recorder(balance, order_price, uniq_id)
        return order

    def first_market_order_maker_for_ifdoco(self, first_side, size, uniq_id, order_price, balance):
        """
        Makes first market order of IFDOCO order.
        :param first_side:
        :param size:
        :param balance:
        :param order_price:
        :param uniq_id:
        :return:
        """

        market = self.bitmex.create_market_order(self.product,
                                                 first_side,
                                                 size
                                                 )
        self.recorder.balance_recorder(balance, order_price, uniq_id)
        return market

    def order_base_maker(self, order_side, order_price):

        profit = None
        loss = None
        trigger = None
        opposite = None

        if order_side == "buy":

            opposite = "sell"

            profit = float(order_price + self.profit_price)
            loss = float(order_price - self.lost_price)
            trigger = loss + 5

        elif order_side == "sell":

            opposite = "buy"

            profit = float(order_price - self.profit_price)
            loss = float(order_price + self.lost_price)
            trigger = loss - 5

        data = {'execution_side': opposite, 'loss_line': loss, 'profit_line': profit, 'trigger': trigger}

        return data
