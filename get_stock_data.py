#!/usr/bin/env python3
from analyze import Analyzer as az
import time
a = az()

choice = ['AMZN', 'CAC', 'CARG', 'CCBG', 'EVOL', 'FB', 'FEUZ', 'FNCH', 'GOOG', 'GOOGL', 'IBM', 'IMUX', 'LMAOU', 'LSTR', 'NHIC', 'OMP', 'OPGN', 'PALI', 'REDU', 'ROLL', 'SLP', 'TWTR', 'VLYPP', 'VRAY', 'ZEAL']

for abbrev in choice:
    while True:
        try:
            a.get_stock_data(abbrev)
            break
        except Exception as e:
            print(e)
            print(f'found an exception while getting {abbrev}, need to sleep before trying again')
            time.sleep(15)
