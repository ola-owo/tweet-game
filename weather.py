#!/usr/bin/python
#Implements OpenWeatherMap and Weather Underground APIs
from collections import OrderedDict
from urllib2 import HTTPError,  urlopen
from urllib import quote
from HTMLParser import HTMLParser as h
import cPickle, difflib, json, os, re, web
import twitter

#Secret Variables
API_KEY = os.environ['WUNDERGROUND_KEY']
OWM_KEY = os.environ['OWM_KEY']
MQ_KEY = os.environ['MAPQUEST_KEY']

BASE_URL_WU = 'http://api.wunderground.com/api/%s/' % API_KEY
BASE_URL_OWM = 'http://openweathermap.org/data/2.3/weather?'
BASE_URL_MQ = 'http://open.mapquestapi.com/geocoding/v1/address?'

class Weather:
    'Weather object (using Weather Underground API)'
    def __init__(self, location, features=['conditions'], icon_set = '/i/'):
        self.location = location
        self.features = features
        self.icon_set = icon_set

    def getWeather(self):
        formattedFeatures = '/'.join(self.features)
        params = '/'.join([formattedFeatures, 'q', self.location+'.json'])

        URL = BASE_URL_WU + params
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
        URL = BASE_URL_WU + 'animatedradar/animatedsatellite/q/%s.gif' % self.location
        animation = urlopen(URL)
        with open('static/img/radar.gif', 'wb+') as f:
            f.write(animation.read())
        animation.close()

def getGeoCode(q, **kwargs):
    '''Get city coordinates with MapQuest API'''
    params = ['key='+MQ_KEY, 'location='+quote(q)]
    for key, value in kwargs.iteritems():
        params.append(key + '=' + value)
    paramString = '&'.join(params)
    URL = h().unescape(BASE_URL_MQ + paramString)

    try:
        web.debug('MapQuest URL: ' + URL)
        resp = urlopen(URL).read().decode('utf-8')
    except HTTPError as e:
        #Catch random HTTP Errors
        web.debug('Weather.py; HTTPError: '+str(e))
        getGeoCode(q, **kwargs)

    root = json.loads(resp)
    try:
        coords = root['results'][0]['locations'][0]['latLng']
    except IndexError as e: # No results given from MapQuest
        return False, False, False
    lat = str(coords['lat'])
    lng = str(coords['lng'])
    suggestions = [i for i in root['results'][0]['locations']]
    return lat, lng, suggestions
    
def getWeather2(lat, lng):
    '''getWeather2(lat,lng) -> dict
    Search with OpenWeatherMap API'''
    baseURL = 'http://api.openweathermap.org/data/2.5/weather?'
    params = ['lat='+lat, 'lon='+lng, 'APPID='+OWM_KEY, 'mode=json', 'units=imperial']
    paramString = '&'.join(params)
    URL = h().unescape(baseURL + paramString)
    web.debug('URL: '+URL)

    try:
        resp = urlopen(URL).read().decode('utf-8')
    except HTTPError as e:
        #Catch random HTTP Errors
        web.debug('Weather.py; HTTPError: '+str(e))
        getWeather2(lat, lng)

    root = json.loads(resp)
    return root
