from ConditionChecker import ConditionChecker
import time
import traceback


if __name__ == '__main__':
    c = ConditionChecker()
    try:
        while True:
            c.board_status_checker()          # checks board status
            c.market_reader()                 # gets latest chart and market data
            c.order_checker()                 # checks if there's an orders
            c.position_checker()              # checks positions
            c.only_position_checker()         # checks positions without orders
            c.order_actually_dead_checker()   # checks orders if they are still available or not
            c.only_order_checker()            # checks orders and in certain circumstances cancels them
            c.orderbook_getter()

            if c.signal:
                c.order_information_checker()   # 全ての条件をクリアしたら、取引を行う

    except:
        time.sleep(2)
        traceback.print_exc()
