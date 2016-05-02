#!/usr/bin/python
from bs4 import BeautifulSoup as bs
import cPickle as cp
from urllib2 import Request, urlopen

URL = 'http://twittercounter.com/pages/100' 

print 'Getting top 100 Twitter accounts from URL "http://twittercounter.com/pages/100"' 
from urllib2 import Request, urlopen
req = Request(URL)
resp = urlopen(req).read().decode('utf-8')

# parse with BeautifulSoup etc
print 'Parsing HTTP response...'
soup = bs(resp, 'html.parser')
lst = soup.find_all('span', itemprop='alternateName')
lst = [i.text[1:] for i in lst]

#save list into celebs file
print 'Pickling new celebrity list'
with open('celebs','r') as f:
    celebs = cp.load(f)
celebs['popular'] = lst
with open('celebs','w') as f:
    cp.dump(celebs, f)
