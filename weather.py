#!/usr/bin/python
#Implements WeatherBug API
from urllib2 import urlopen, HTTPError
from simplejson import loads
import twitter

API_KEY = 'c53b5418bcd4a631'
BASE_URL = 'http://api.wunderground.com/api/%s/' % API_KEY

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
        data = loads(resp.read())
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
        with open('static/icons/radar.gif', 'wb+') as f:
            f.write(animation.read())
        animation.close()
