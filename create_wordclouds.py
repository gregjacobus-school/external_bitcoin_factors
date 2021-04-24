#!/usr/bin/env python3

from wordcloud import WordCloud

def create_wordclouds():
    spikes_fn = '/tmp/spikes'
    troughs_fn = '/tmp/troughs'
    spikes_output_fn = '/tmp/wordcloud_spikes.png'
    troughs_output_fn = '/tmp/wordcloud_troughs.png'
    base_stopwords_fn = '/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/wordcloud/stopwords'
    words_to_ignore = [
            'BBC', # a highly linked news outlet
            'reuters', # a highly linked news outlet
            'New', #Too often a part of a linked news outlet name
            'News', #Too often a part of a linked news outlet name
            'people', #news outlet, too often referenced with little insight
            'CNN', #news outlet, highly linked
    ]

    with open(base_stopwords_fn) as f:
        stopwords = [word.strip() for word in f.readlines()]
    stopwords.extend(words_to_ignore)
    stopwords = set(stopwords)

    wordcloud = WordCloud(width=640, height=400, stopwords=stopwords, max_words=50)

    with open(spikes_fn) as f:
        spike_text = f.read()
    with open(troughs_fn) as f:
        trough_text = f.read()

    spike_wc  = wordcloud.generate(spike_text)
    spike_wc.to_file(spikes_output_fn)

    trough_wc  = wordcloud.generate(trough_text)
    trough_wc.to_file(troughs_output_fn)

if __name__ == '__main__':
    create_wordclouds()