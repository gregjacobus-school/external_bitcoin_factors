#!/usr/bin/env python3

import pickle
import pandas as pd
import matplotlib.pyplot as plt
from analyze import Analyzer as az
import sys

WINDOW_SIZE = 7 #in days

analyzer = az()

analyzer.df = analyzer.df.set_index('DateTime')
btc_vols = analyzer.df['Volume']
#btc_vols.plot()

abbrev = 'S&P 500'
abbrev = 'GOOGL'

abbrev = abbrev.lower()
with open(f'stock_data/{abbrev}_pd.pickle', 'rb') as f:
    stock_data = pickle.load(f)
stock_data = stock_data.loc['2021-04-02':'2013-12-28']
stock_vols = stock_data['6. volume']

#Need to fill in missing dates because stocks aren't recorded on weekends
idx = pd.date_range('2013-12-28', '2021-04-02')
fill_value = 0.0
stock_vols = stock_vols.reindex(idx, fill_value=fill_value)
for i, val in enumerate(stock_vols):
    if val == fill_value:
        stock_vols[i] = stock_vols[i-1]

#scaling factor to make the graph easier to look at
stock_vols = stock_vols * 1000

stock_vols.plot()

cor = stock_vols.corr(btc_vols)
print(cor)
#plt.show()

#Perform the correlation for each time range
print(btc_vols.shape)
correlations = []
start_time = btc_vols.index[0]
end_time = start_time
timedelta = pd.Timedelta(days=WINDOW_SIZE)
while True:
    start_time = end_time
    end_time = start_time + timedelta
    btc_subset = btc_vols.loc[start_time:end_time]
    stock_subset = stock_vols.loc[start_time:end_time]
    if btc_subset.empty or stock_subset.empty:
        print(len(correlations))
        break
    try:
        cor = stock_subset.corr(btc_subset)
    except RuntimeError:
        continue
    correlations.append(cor)
correlations = pd.Series(correlations)
plt.scatter(correlations.index, correlations)
#correlations.plot(kind='scatter')
plt.show()

