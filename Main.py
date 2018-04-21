from ConditionChecker import ConditionChecker
import time
import traceback


if __name__ == '__main__':
    c = ConditionChecker()
    count = 0
    while True:
        try:
            st = time.time()
            c.board_status_checker()          # checks board status
            if count == 0:
                c.renew_chart_data()
                c.current_balance_getter()
                c.current_price_getter()
                count += 1
            elif count % 15 == 0:
                c.order_actually_dead_checker()  # checks orders if they are still available or not
                time.sleep(3)                 # avoid too many request
                print('slept a bit to avoid making too many requests')
                count += 1
            elif count != 100:
                count += 1
            else:
                count = 0
            c.market_reader()                 # gets latest chart and market data
            c.order_checker()                 # checks if there's an orders, and gets order id
            c.position_checker()              # checks positions
            c.only_position_checker()         # checks positions without orders
            c.only_order_checker()            # checks orders and in certain circumstances cancels them
            print(time.time() - st)

            if c.signal:
                c.order_information_checker()   # 全ての条件をクリアしたら、取引を行う

        except:
            time.sleep(3)
            traceback.print_exc()
