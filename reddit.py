from urllib2 import urlopen, HTTPError
import time, json

def parse(url):
    try:
        r = urlopen(url).read().decode()
        data = json.loads(r)
        return data

    except HTTPError:
        time.sleep(1)
        parse(url)

class FrontPage(object):
    def __init__(self, sort='hot', limit=25):
        self.sort = sort
        self.limit = limit
        self.endpoint = 'http://api.reddit.com/%s.json?limit=%d' % (self.sort, self.limit)

    def getPosts(self):
        '''returns a list of posts'''
        data = parse(self.endpoint)
        while data == None:
            data = parse(self.endpoint)
        posts = [post['data'] for post in data['data']['children']]
        return posts
