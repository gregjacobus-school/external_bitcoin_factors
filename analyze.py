#!/usr/bin/env python3
from alpha_vantage.timeseries import TimeSeries
import argparse
from bs4 import BeautifulSoup
import json
import os
import requests
import pandas as pd
from create_wordclouds import create_wordclouds

ALPHA_VANTAGE_API_KEY = "PFPY0HSPR5GUPRNY"
ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY)

class Analyzer:
    def __init__(self, data_fn="data.csv", num_spikes=5, spikes=True):
        self.df = pd.read_csv(data_fn, parse_dates=[0])

        # self.df = self.df[(self.df['DateTime'] > pd.Timestamp('2017-01-01')) & (self.df['DateTime'] < pd.Timestamp('2021-04-20'))]
        if data_fn == "data.csv":
            self.spikes = self.find_top_spikes_troughs(num_spikes, spikes=spikes)
            self.troughs = self.find_top_spikes_troughs(num_spikes, spikes=False)

        # self.get_stock_data('NDAQ')

    def analyze_bitcoin(self):
        self.analyze_list(self.spikes, 'spikes')
        self.analyze_list(self.troughs, 'troughs')

    def get_spikes_troughs(self, num_spikes, spikes=True, time_col="DateTime", analysis_col="Volume"):
        self.spikes = self.find_top_spikes_troughs(num_spikes, spikes=True, time_col=time_col, analysis_col=analysis_col)
        self.troughs = self.find_top_spikes_troughs(num_spikes, spikes=False, time_col=time_col, analysis_col=analysis_col)

    def find_top_spikes_troughs(self, num_spikes, spikes=True, time_col="DateTime", analysis_col="Volume"):
        prev_row = None
        all_diffs = []
        for row in self.df.iterrows():
            row = row[1]
            if prev_row is None:
                prev_row = row
                continue

            # Calculate based on pure increase
            value = row[analysis_col] - prev_row[analysis_col]

            # Calculate based on percentage increase
            if prev_row[analysis_col] == 0:
                continue
            value = (row[analysis_col] - prev_row[analysis_col]) / prev_row[analysis_col]
            
            diff = {
                'value': value,
                'start_time': prev_row[time_col],
                'end_time': row[time_col]
            }
            if spikes and diff['value'] > 0:
                all_diffs.append(diff)
            elif not spikes and diff['value'] < 0:
                all_diffs.append(diff)
            prev_row = row

        # Only reverse sort if we're looking for spikes, not troughs
        all_diffs.sort(reverse=spikes, key=lambda diff: diff['value'])
        
        return all_diffs[:num_spikes]

    def find_mining_top_spikes_troughs(self, num_spikes, spikes=True):
        rename = {'Timestamp': 'DateTime', 'difficulty': 'Volume'}
        self.df = self.df.rename(columns=rename)
        self.df.replace(0, 0.0000001, inplace=True)
        return self.find_top_spikes_troughs(num_spikes=num_spikes, spikes=spikes)

    def analyze_list(self, data, fn):
        f_hand = open(os.path.join('/tmp', fn), 'w')
        one_day_delta = pd.Timedelta(days=1)
        events = []
        for diff in data:
            times_to_analyze = []
            start_time = diff['start_time']
            num_days_back = 1
            times_to_analyze = [start_time]
            times_to_analyze.extend([start_time - one_day_delta*i for i in range(1, 1 + num_days_back)])
            print(times_to_analyze)
            for analyze_time in times_to_analyze:
                date_str = f"{analyze_time.month_name()} {analyze_time.day}, {analyze_time.year}"
                print(f'getting articles from {date_str}')
                articles = self.get_events_on_day(analyze_time)
                #f_hand.write(f'================Articles from {date_str}=========================\n')
                for article in articles:
                    events.append(article)
                    f_hand.write(article)
                    f_hand.write('\n')
                f_hand.write('=' * 70)
                f_hand.write('\n')
        
        f_hand.close()

    def get_events_on_day(self, date):
        # In format like: 2020_October_18
        url_date = f"{date.year}_{date.month_name()}_{date.day}"
        url = f"https://en.wikipedia.org/wiki/Portal:Current_events/{url_date}"

        resp = requests.get(url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        data_region = soup.find(role='region')
        if not data_region:
            data_region = soup.find(class_="description")
        list_items = data_region.find_all('li')

        # Some lists are nested, we don't want duplicates. Flatten the lists
        # so that each bullet, no matter if it's nested, is on the same level
        articles = []
        for li in list_items:
            if li.find('ul'):
                heading = li.find('a')
                articles.append(heading.get_text())
            else:
                articles.append(li.get_text())

        return articles

    
    def get_stock_data(self, abbrev):
        fn = os.path.join('stock_data', abbrev)
        #If we have fetched the data already, just read it instead
        if os.path.exists(fn):
            with open(fn) as f_hand:
                data = json.load(f_hand)
        else:
            data, metadata = ts.get_daily_adjusted(abbrev, outputsize="full")
            with open(fn, 'w') as f_hand:
                json.dump(data, f_hand, indent=2)

    def create_wordclouds(self):
        create_wordclouds()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-file', default="data.csv", help="The file storing Bitcoin Volume data")
    parser.add_argument('--troughs', default=False, action="store_true", help="Analyze troughs (as opposed to spikes)")
    parser.add_argument('--num-spikes', default=5, help="Number of spikes/troughs to analyze")
    args = parser.parse_args()
    a = Analyzer(data_fn=args.data_file, num_spikes=args.num_spikes, spikes=not args.troughs)
