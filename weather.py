#!/usr/bin/python
#Implements WeatherBug and Weather Underground APIs
from collections import OrderedDict
from urllib2 import urlopen, HTTPError
from xml.etree import ElementTree as et
import cPickle, difflib, json, os, re, web
import twitter

#Secret Variables
API_KEY = os.environ['WUNDERGROUND_KEY']
WXBUG_KEY = os.environ['WXBUG_KEY']
WXBUG_SECRET = os.environ['WXBUG_SECRET']

BASE_URL = 'http://api.wunderground.com/api/%s/' % API_KEY

def getToken():
    c_key = WXBUG_KEY
    c_secret = WXBUG_SECRET
    access_call = 'https://thepulseapi.earthnetworks.com/oauth20/token?grant_type=client_credentials\
&client_id=%s&client_secret=%s&' % (c_key, c_secret)
    API_KEY2 = json.loads(urlopen(access_call).read().decode())['OAuth20']['access_token']['token']
#Initial getToken()
c_key = 'V2Pjr6F2YFmhlc5kfrTVo61BXOUgtuX0'
c_secret = 'QvbAR5HhwxsncV8p'
access_call = 'https://thepulseapi.earthnetworks.com/oauth20/token?grant_type=client_credentials\
&client_id=%s&client_secret=%s&' % (c_key, c_secret)
API_KEY2 = json.loads(urlopen(access_call).read().decode())['OAuth20']['access_token']['token']

#with open('citycodes.txt', 'r') as f:
#    CITYCODES = []
#    for line in f.readlines():
#        if not line.startswith('#'):
#            CITYCODES.append(line.strip('\n').split('|'))
with open('citydict', 'rb') as f:
    #Loads City Code Dictionary, keyed by first letter
    CITYCODES = cPickle.load(f)

class Weather:
    def __init__(self, location, features=['conditions'], icon_set = '/i/'):
        self.location = location
        self.features = features
        self.icon_set = icon_set

    def getWeather(self):
        formattedFeatures = '/'.join(self.features)
        params = '/'.join([formattedFeatures, 'q', self.location+'.json'])

        URL = BASE_URL + params
        try:
            resp = urlopen(URL)
        except HTTPError:
            data = {'response':{
                'error':{
                    'description':'Invalid Location'}}}
            return data
        data = json.loads(resp.read())
        resp.close()
        if 'current_observation' in data.keys():
            iconURL = data['current_observation']['icon_url']
            data['current_observation']['icon_url'] = iconURL.replace('/k/', self.icon_set)
            oembed_lat = data['current_observation']['display_location']['latitude']
            oembed_long = data['current_observation']['display_location']['longitude']
            oembed_coord = ','.join([oembed_lat, oembed_long, '100km'])
            data['html'] = twitter.oembed('weather OR clima', oembed_coord)

        return data

    def getRadar(self):
        URL = BASE_URL + 'animatedradar/animatedsatellite/q/%s.gif' % self.location
        animation = urlopen(URL)
        with open('static/img/radar.gif', 'wb+') as f:
            f.write(animation.read())
        animation.close()

def getWeather2(q, cityCode=None, latitude=None, longitude=None, **kwargs):
    '''Search with Weatherbug 'Pulse' API'''
    if latitude and longitude:
        #Coordinates retrieved from webpage
        location='lat=%s&long=%s' % (latitude, longitude)
        suggestions = None
    elif cityCode:
        #City Code given from suggestions list
        location = 'cityCode='+cityCode
        suggestions = None
    elif q.isdigit() and len(q)==5:
        #Search by ZIP Code
        location = 'zipCode='+q
        suggestions = None
    else:
        #Search the intl country database
        # q = re.sub('[\W\d]+', '', q).title()
        q = q.strip(' ').title()
        REmatcher = re.compile(r'^([^,]+)(?:, *(\w+))?$')
        REmatch = REmatcher.match(q)
        if REmatch is None:
            return (None, None)
        else:
            REmatch = REmatch.groups()
            q = REmatch[0]
        letter = q[0].lower()
        web.debug('Weather.py Line 84; q = \'%s\'' % q) 
        suggestions = {}
        possible_cities = [city[1] for city in CITYCODES[letter]]
        unsorted_matches = difflib.get_close_matches(q, possible_cities, cutoff=0.8)
        matches = list(OrderedDict.fromkeys(unsorted_matches))
        if len(matches)==0:
            return (None, None)
        web.debug('Weather.py Line 72; matches= '+str(matches))

        def citySearch(names):
            match_found = False
            match = None
            suggs = []
            for name in names:
                for city in CITYCODES[letter]:
                    if name == city[1]:
                        if match_found:
                            suggs.append(city)
                        else:
                            match = city
                            match_found = True
            if REmatch[1] is not None:
                allmatches = [match] + suggs
                for i in allmatches:
                    if i[2] == '--':
                        #Match Countries
                        if i[4].strip('\n') == REmatch[1].title():
                            match = i
                            break
                    else:
                        #Match States
                        if i[2] == REmatch[1].upper():
                            match = i
                            break
            return (match, suggs)        
                
        match = citySearch(matches)
        web.debug('Weather.py Line 130; match chosen: ')
        web.debug(match[0])
        location = 'cityCode='+match[0][0]
        suggestions = match[1]

    conditions = {}
    baseURL = 'https://thepulseapi.earthnetworks.com/getLiveWeatherRSS.aspx?access_token=%s&OutputType=1' % API_KEY2
    params = [location]
    for key in kwargs:
        params.append(key + '=' + kwargs[key])
    paramString = '&' + '&'.join(params)
    URL = baseURL + paramString
    web.debug('URL: '+URL)
    aws = '{http://www.aws.com/aws}'

    #Catch random HTTP Errors
    try:
        resp = urlopen(URL).read().decode()
    except HTTPError as e:
        web.debug('Weather.py; HTTPError: '+str(e))
        web.debug('URL = '+ URL)
        getWeather2(q, cityCode, kwargs)

    #Catch expired token
    try:
        root = et.fromstring(resp).find(aws+'ob')
    except et.ParseError:
        if 'fault' in json.loads(resp).keys():
            getToken()
        getWeather2(q, kwargs)

    #City Name
    conditions['city'] = root.find(aws+'city-state').text 
    #Temperature
    temp = root.find(aws+'temp')
    conditions['temp'] = temp.text + temp.attrib['units']
    #OEmbed
    coordinates = ','.join([root.find(aws+'latitude').text, root.find(aws+'longitude').text, '100km'])
    conditions['html'] = twitter.oembed('weather OR clima', coordinates)
    #Low/High
    conditions['temp_high'] = root.find(aws+'temp-high').text
    conditions['temp_low'] = root.find(aws+'temp-low').text
    #Current Conditions
    icon_url = root.find(aws+'current-condition').attrib['icon']
    icon_code = re.findall('\d{3}', icon_url)[0]
    conditions['icon'] = 'http://img.weather.weatherbug.com/forecast/icons/localized\
/500x420/en/trans/cond%s.png' % icon_code
    conditions['condition'] = root.find(aws+'current-condition').text

    return (conditions, suggestions)
