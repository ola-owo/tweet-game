#!/usr/bin/python
# vim: set fileencoding=latin-1
import cPickle, random, sys, tweepy, types, web
from subprocess import PIPE, Popen, STDOUT
from threading import Lock

#Connect with OAuth
consumer_key = 'zCKf6pW0yjhthedkNmQg'
consumer_secret = 'MQn2mopByxe33F8vbW8CG75Wa1LCxVUHlf9Z07zo'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
access_key = '712694562-YxZ8DHMXJw0TGz5ZxqQFV0oO3G0tIFeJNMTyzEOX'
access_secret = 'bmKnPpCud19bp4ePKjnEG24E8eTb41KSFtWT6Oino'
api = auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

CELEBS = cPickle.load(open('celebs', 'rb'))

#Set Lock?
lock = Lock()

def user_timeline(username, write=True):
    try:
        timeline = api.user_timeline(username, count=200)
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
    web.debug('Twitter.py Line 51; Username: '+user_name)
    user = api.get_user(user_name)
    choices = [user]
    while len(choices) < 4:
        choice = celebList[random.randint(0,len(celebList)-1)]
        if choice in [person.screen_name for person in choices]:
            continue
        choices.append(api.get_user(choice))
    random.shuffle(choices)
    tl = user_timeline(user_name, write=False)
    if len(tl) == 0:
        getNounPhrases(tagger, category)
    random.shuffle(tl)
    for tweet in tl:
        if len(tweet) == 0:
            continue
        lock.acquire() # will block if lock is already held
        try:
            tagger.stdin.write(tweet.replace('[\\s]+', ' ')+'.\n')
            taggedTweet = tagger.stdout.readline().strip('\t\n').replace('\t', '\xe2\x80\xa6') #\xe2\x80\xa6 "…"
        finally:
            lock.release()
        if len(taggedTweet.split('\xe2\x80\xa6')) >= 3:
            break
    else:
        getNounPhrases(tagger, category)
    web.debug('Twitter.py line 73; Tweet: '+taggedTweet)
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
