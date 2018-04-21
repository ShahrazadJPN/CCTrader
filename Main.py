from ConditionChecker import ConditionChecker
import time
import traceback
import requests
import ccxt


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
            elif count % 5 == 0:
                c.order_actually_dead_checker()  # checks orders if they are still available or not
                time.sleep(5)                 # avoid too many request
                print('slept a bit to avoid making too many requests')
                count += 1
            elif count == 70:
                count = 0
            else:
                count += 1
            c.market_reader()                 # gets latest chart and market data
            c.order_checker()                 # checks if there's an orders, and gets order id
            c.position_checker()              # checks positions
            c.only_position_checker()         # checks positions without orders
            c.only_order_checker()            # checks orders and in certain circumstances cancels them
            c.emergency_checker()             # closes all the positions
            time.sleep(1)
            print(time.time() - st)
            if c.signal and not c.ordering:
                c.order_information_checker()   # 全ての条件をクリアしたら、取引を行う

        except ccxt.BaseError:
            print('Market Too Busy')
            time.sleep(15)

        except Exception:
            time.sleep(5)
            traceback.print_exc()
