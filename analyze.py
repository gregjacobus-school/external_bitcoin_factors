#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import pandas as pd

class Analyzer:
    def __init__(self):
        data_fn = '/Users/gjacobu/Documents/school/Bitcoin-Blockchain/final_project/external_factors/data.csv'
        self.df = pd.read_csv(data_fn, parse_dates=[0])
    
        spikes = self.find_top_spikes_valleys(50, spikes=False)
        self.analyze_list(spikes)

    def find_top_spikes_valleys(self, num_spikes, spikes=True):
        prev_row = None
        all_diffs = []
        for row in self.df.iterrows():
            row = row[1]
            if prev_row is None:
                prev_row = row
                continue

            # Calculate based on pure increase
            value = row.Volume - prev_row.Volume

            # Calculate based on percentage increage
            value = (row.Volume - prev_row.Volume) / prev_row.Volume
            
            diff = {
                'value': value,
                'start_time': prev_row.DateTime,
                'end_time': row.DateTime
            }
            if spikes and diff['value'] > 0:
                all_diffs.append(diff)
            elif not spikes and diff['value'] < 0:
                all_diffs.append(diff)
            prev_row = row

        # Only reverse sort if we're looking for spikes, not valleys
        all_diffs.sort(reverse=spikes, key=lambda diff: diff['value'])
        
        return all_diffs[:num_spikes]

    def analyze_list(self, data):
        f_hand = open('/tmp/events', 'w')
        events = []
        for diff in data:
            start_time = diff['start_time']
            date_str = f"{start_time.month_name()} {start_time.day}, {start_time.year}"
            print(f'getting articles from {date_str}')
            articles = self.get_events_on_day(start_time)
            f_hand.write(f'================Articles from {date_str}=========================\n')
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
        

if __name__ == '__main__':
    a = Analyzer()