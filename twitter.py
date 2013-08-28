#!/usr/bin/python
# vim: set fileencoding=latin-1
import cPickle, os, random, sys, time, tweepy, types, web
from subprocess import PIPE, Popen, STDOUT
from threading import Lock
import pytz
now = pytz.datetime.datetime.now

#Secret Variables
TWITTER_ACCESS_KEY = os.environ['TWITTER_ACCESS_KEY']
TWITTER_ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']
TWITTER_CONS_KEY = os.environ['TWITTER_CONS_KEY']
TWITTER_CONS_SECRET = os.environ['TWITTER_CONS_SECRET']

#Connect with OAuth
consumer_key = TWITTER_CONS_KEY
consumer_secret = TWITTER_CONS_SECRET
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
access_key = TWITTER_ACCESS_KEY
access_secret = TWITTER_ACCESS_SECRET
api = auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

CELEBS = cPickle.load(open('celebs', 'rb'))

#Set Lock?
lock = Lock()

def user_timeline(username, write=True, rts=True):
    try:
        web.debug(str(now())+' getting api.usertimeline()...')
        timeline = api.user_timeline(username, count=200, include_rts=rts)
        web.debug(str(now())+' timeline received from server.')
        tweets = []
        for tweet in timeline:
            text = tweet.__getstate__()['text'].encode('utf-8')
            tweets.append(text)
        if write:
            tweetData = '\n'.join(tweets)
            with open('tweets.txt','w+') as f:
                f.write(tweetData)
        return tweets
    except tweepy.TweepError, e:
        return e

def oembed(query, location):
    results = api.search(query, geocode=location)
    if len(results) == 0:
        return None
    _id = str(results[0].__getstate__()['id'])
    oembed_resp = api.get_oembed(_id)
    oembed_code = oembed_resp['html']
    return oembed_code

def getNounPhrases(tagger, category):
    try:
        celebList = CELEBS[category]
    except KeyError:
        celebList = CELEBS['popular']
    random.shuffle(celebList)
    user_name = celebList[0]
    web.debug('Twitter.py Line 52; Username: '+user_name)
    user = api.get_user(user_name)
    choices = [user]
    for i in celebList[1:4]:
        choices.append(api.get_user(i))
    random.shuffle(choices)
    
    tl = user_timeline(user_name, write=False, rts=False)
    if len(tl) == 0:
        getNounPhrases(tagger, category)
    random.shuffle(tl)
    for tweet in tl:
        if len(tweet) == 0:
            continue
        lock.acquire() # will block if lock is already held
        try:
            web.debug(str(now())+' writing to tagger...')
            tagger.stdin.write(tweet.replace('[\\s]+', ' ')+'.\n')
            taggedTweet = tagger.stdout.readline().strip('\t\n').replace('\t', '\xe2\x80\xa6') #\xe2\x80\xa6 = "…"
            web.debug(str(now())+' tags received.')
        finally:
            lock.release()
        if len(taggedTweet.split('\xe2\x80\xa6')) >= 3:
            break
    else:
        getNounPhrases(tagger, category)
    web.debug('Twitter.py line 75; Tweet: '+taggedTweet)
    cPickle.dump((user_name,taggedTweet), open('answer', 'wb+'))
    return {'username':user_name, 'phrases':taggedTweet, 'otherChoices':choices}

if __name__ == '__main__':
#    while True:
#        print 'Type EXIT to quit this program.'
#        user = raw_input('Input Twitter Username: ')
    if sys.argv[1] == 'timeline':
        user = sys.argv[2]
#    if user == 'EXIT':
#        sys.exit()
        tl = user_timeline(user, write=False)
        if len(tl) == 0:
            print 'That user does not exist (or has not tweeted).'
        else:
            for tweet in tl:
                print tweet, '\n'
                time.sleep(0.25)
