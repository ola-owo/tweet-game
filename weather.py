#!/usr/bin/python
#Implements WeatherBug API
from urllib2 import urlopen, HTTPError
from xml.etree import ElementTree as et
import json, re
import twitter

API_KEY = 'c53b5418bcd4a631'
BASE_URL = 'http://api.wunderground.com/api/%s/' % API_KEY

c_key = 'V2Pjr6F2YFmhlc5kfrTVo61BXOUgtuX0'
c_secret = 'QvbAR5HhwxsncV8p'
access_call = 'https://thepulseapi.earthnetworks.com/oauth20/token?grant_type=client_credentials\
&client_id=%s&client_secret=%s&' % (c_key, c_secret)
API_KEY2 = json.loads(urlopen(access_call).read().decode())['OAuth20']['access_token']['token']
CITYCODES = []
with open('citycodes.txt', 'r') as f:
    for line in f.readlines():
        if not line.startswith('#'):
            CITYCODES.append(line.split('|'))

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

def getWeather2(q, **kwargs):
    '''Search with Weatherbug 'Pulse' API'''
    if q.isdigit() and len(q)==5:
        #Search by ZIP Code
        location = 'zipCode='+q
        suggestions = None
    else:
        #Search the intl country database
        q = q.title()
        suggestions = {}
        location = ''
        for cityData in CITYCODES:
            if q == cityData[1]:
                if len(location) == 0:
                    location = 'cityCode='+cityData[0]
                else:
                    suggestions[cityData[0]] = cityData[1]
            elif q in cityData[1]:
                suggestions[cityData[0]] = cityData[1]

    conditions = {}
    baseURL = 'https://thepulseapi.earthnetworks.com/getLiveWeatherRSS.aspx?access_token=%s&OutputType=1' % API_KEY2
    params = [location]
#    for key in kwargs:
#        params.append(key + '=' + kwargs[key])
    paramString = '&'.join(params)
    URL = baseURL + '&' + paramString
#    URL = baseURL
    resp = urlopen(URL).read().decode()
    aws = '{http://www.aws.com/aws}'
    root = et.fromstring(resp).find(aws+'ob')

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

    def getRadar(self):
        URL = BASE_URL + 'animatedradar/animatedsatellite/q/%s.gif' % self.location
        animation = urlopen(URL)
        with open('static/icons/radar.gif', 'wb+') as f:
            f.write(animation.read())
        animation.close()
