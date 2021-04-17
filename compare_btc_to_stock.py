#!/usr/bin/env python3

import pickle
import pandas as pd
import matplotlib.pyplot as plt
from analyze import Analyzer as az
analyzer = az()

analyzer.df = analyzer.df.set_index('DateTime')
btc_vols = analyzer.df['Volume']
btc_pct_changes = btc_vols.pct_change()
btc_vols.plot()
#btc_pct_changes.plot()

with open('stock_data/google_pd.pickle', 'rb') as f:
    goog_data = pickle.load(f)
goog_data = goog_data.loc['2021-04-02':'2013-12-28']
goog_vols = goog_data['6. volume']

#Need to fill in missing dates because stocks aren't recorded on weekends
idx = pd.date_range('2013-12-28', '2021-04-02')
fill_value = 0.0
goog_vols = goog_vols.reindex(idx, fill_value=fill_value)
for i, val in enumerate(goog_vols):
    if val == fill_value:
        goog_vols[i] = goog_vols[i-1]

goog_vols = goog_vols * 1000

goog_pct_changes = goog_vols.pct_change()
index = [i for i in range(goog_pct_changes.shape[0])]
goog_pct_changes.index = pd.Index(index)
goog_vols.plot()
#goog_pct_changes.plot()

cor = goog_pct_changes.corr(btc_pct_changes)
cor = goog_vols.corr(btc_vols)
print(cor)
plt.show()
