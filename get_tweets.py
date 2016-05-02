#!/usr/bin/env python
import cPickle, tweepy, re
import porter
from gensim import models
from random import randint
from time import sleep
# import sklearn stuff

WEATHER_SEARCH_PHRASE = 'weather OR sunny OR rain OR wind OR hail OR snow OR heat OR cold OR outside -news -channel'

# # Here's how I got the tweets
# # (replace Twitter keys with their actual values)
# auth = tweepy.OAuthHandler(TWITTER_CONS_KEY, TWITTER_CONS_SECRET)
# api = tweepy.API(auth)
# ids = [randint(20,9999999999) for _ in range(2000)]
# tweets_raw = []
# for i in range(20):
#     subids = ids[i*100:i*100+99]
#     statuses = api.statuses_lookup(subids)
#     tweets_raw += statuses
#     sleep(0.5) # precaution so the twitter api doesn't get mad

# # Replace hashtags, handles, URLs, and numbers  with <HASHTAG>, <HANDLE>,
# # <URL>, and <NUMBER> respectively;
# # Also remove all symbols
# re.UNICODE # enable unicode character set
# bracketMatch = re.compile(r'[^\w <>]')
# urlMatch = re.compile(r'\w+:\/\/(?:\w+\.)?\w+\.\w{2,}(?:\/\S+)?')
# hashMatch = re.compile(r'#\w+')
# handleMatch = re.compile(r'@\w+')
# symbolMatch = re.compile(r'\W+(?=[A-Za-z])')
# numberMatch = re.compile(r'(?<=\s)\d+(?=\s)')
# def formatTweet(text):
#     text = re.sub(bracketMatch, '', text)
#     text = re.sub(urlMatch, '<URL>', text)
#     text = re.sub(hashMatch, '<HASHTAG>', text)
#     text = re.sub(handleMatch, '<HANDLE>', text)
#     text = re.sub(symbolMatch, '', text)
#     text = re.sub(numberMatch, '<NUMBER>', text)
#     return text
# tweets = map(formatTweet, tweets_raw)

if __name__ == '__main__':
    # Tweets are already stored locally
    tweets_parsed = cPickle.load(open('tweets_parsed','rb'))
    p = porter.PorterStemmer()
    def stem(phrase):
        stemmed_words = []
        for word in phrase.split():
            if word.isalpha():
                stemmed_words.append(p.stem(word, 0, len(word)-1))
            else:
                stemmed_words.append(word)
        return ' '.join(stemmed_words)
    tweets_stemmed = map(stem, tweets_parsed)
    cPickle.dump(tweets_stemmed, open('tweets_stemmed','wb'))
    print 'Done.'

