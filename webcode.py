#!/usr/bin/python
# vim: set fileencoding=latin-1
#First attempt at a Web.py website
import web, cgi, cPickle, json, pytz, sqlite3
from datetime import datetime, timedelta
from dateutil.parser import parse as dateparser
from subprocess import PIPE, Popen, STDOUT
import reddit, weather, twitter

urls = (
    '/', 'index',
    '/add', 'add',
    '/remove/(\d+)', 'remove',
    '/bg_add', 'bg_add',
    '/special/?', 'birthday',
    '/reddit/?', 'reddit_frontpage',
    '/weather/?', 'weather_api',
    '/weather2', 'weather_api2',
    '/get_weather','get_weather',
    '/change_location', 'change_location',
    '/twitter/?', 'who_said',
    '/twitter2/?', 'who_said2',
    '/guess_tweet', 'guess_tweet',
    '/test', 'test',
    '/(.*)/?', 'NotFound',
    )

web.config.debug = False
app = web.application(urls, globals())
render = web.template.render('templates/')
db = web.database(dbn='sqlite', db='testdb')
#Trying to see if tagger loads faster in the main program file
tagger = Popen(['java', '-cp', 'ark-tweet-nlp-0.3.jar', 'cmu.arktweetnlp.Tagger'], stdin=PIPE, stdout=PIPE)

#Set up DiskStore session
###if web.config.get('_session') is None:
###    session = web.session.Session(
###        app,
###        web.session.DiskStore('session'),
###        initializer = {
###            'redditSort': 'hot',
###            'prevLocation': '15239',
###            'prevWeather': weather.Weather('15239').getWeather(),
###            'twitterAnswer': ['defaultuser','defaultans'],
###        }
###    )
###    web.config._session = session
###else:
###    session = web.config._session

session = web.session.Session(
    app,
    web.session.DiskStore('sessions'),
    initializer = {
        'redditSort': 'hot',
        'prevLocation': '15239',
        'prevWeather': weather.Weather('15239').getWeather(),
        'twitterName': 'username',
        'twitterPhrase': 'tweet',
        'twitterCategory': 'popular',
    }
)

class NotFound:
    def GET(self, arg):
        return render.birthday()

class index:
    def GET(self):
        i = web.input(file_too_big=False)
        todos = db.select('todo')

        #Reddit FrontPage App
        if 'redditSort' not in session:
            session.redditSort = 'hot'
        fp = reddit.FrontPage(session.redditSort)
        posts = fp.getPosts()

        return render.index(todos, i.file_too_big, posts)

class birthday:
    def GET(self):
        return render.birthday()

class add:
    def POST(self):
        i = web.input()
        n = db.insert('todo', title=i.title)
        raise web.seeother('/')

class remove:
    def POST(self, ID):
        ID = int(ID)
        db.delete('todo', where='id = $ID', vars=locals())
        raise web.seeother('/')

class bg_add:
    def POST(self):
        cgi.maxlen=1024*1024*5
        try:
            file_ = web.webapi.rawinput().get('bgimg')
            filename = 'static/user/bg.jpg'
            web.debug("ALERT: File '%s' was uploaded." % file_.filename)
            if file_.filename.lower().endswith(".mid"):
                filename = 'static/user/bg.mid'
            with open(filename, 'wb') as f:
                f.write(file_.value)
        except ValueError:
            raise web.seeother('/?file_too_big=True')
        raise web.seeother('/')

class reddit_frontpage:
    def GET(self):
        if 'redditSort' not in session:
            session.redditSort = 'hot'
        fp = reddit.FrontPage(sort=session.redditSort)
        posts = fp.getPosts()
        return render.reddit(posts)
    def POST(self):
        sort = web.input(category='default').category
        web.debug('Sort: '+sort)
        if sort != 'default':
            if sort in ['hot', 'new', 'top', 'controversial']:
                session.redditSort = sort
            else:
                web.webapi.badrequest()

class weather_api:
    def GET(self):
        try:
            observationTime = session.prevWeather['current_observation']['observation_time_rfc822']
        except TypeError, e:
            web.debug(e)
            session.prevWeather = weather.Weather('15239').getWeather()
            observationTime = session.prevWeather['current_observation']['observation_time_rfc822']
        #Check if last request was less than 10 secs ago
        lastUpdated = dateparser(observationTime)
        if (datetime.now(pytz.utc) - lastUpdated) > timedelta(seconds=10): #Make new request
            conditions = weather.Weather(session.prevLocation)
            web.debug("Requesting Radar GIF for " + conditions.location)
            try:
                conditions.getRadar()
            except weather.HTTPError:
                pass
            now = conditions.getWeather()
            return render.weather(now)
        else: #Give old data instead
            if session.prevWeather == None:
                session.prevWeather = weather.Weather(session.prevLocation)
            try:
                now = session.prevWeather 
            except AttributeError:
                session.prevWeather = weather.Weather(session.prevLocation)
                now = session.prevWeather

            return render.weather(now, too_fast=True)

class change_location:
    def POST(self):
        location = str(web.input('zipcode')['zipcode'])
        location = location.strip(' ').replace(' ', '_')

        #Check if location is same as before
        if 'prevLocation' not in session:
            web.debug("Requesting Radar GIF for " + conditions.location)
            session.prevLocation = '15239'
        if location != session.prevLocation:
            session.prevLocation = location
        raise web.seeother('/weather')

class who_said:
    def GET(self):
        category = session.twitterCategory
        puzzle = twitter.getNounPhrases(tagger, category)
        choices = puzzle['otherChoices']
        web.debug('Username: %s\nPhrase: %s' % (puzzle['username'], puzzle['phrases']))
        categories = list(twitter.CELEBS.keys())
        session.twitterName = puzzle['username']
        session.twitterPhrase = puzzle['phrases']
        active = session.twitterCategory
        return render.twitter(puzzle['phrases'], choices, categories, active)

class who_said2:
    def GET(self):
        category = session.twitterCategory
        puzzle = twitter.getNounPhrases(tagger, category)
        choices = puzzle['otherChoices']
        web.debug('Username: %s\nPhrase: %s' % (puzzle['username'], puzzle['phrases']))
        categories = list(twitter.CELEBS.keys())
        session.twitterName = puzzle['username']
        session.twitterPhrase = puzzle['phrases']
        active = session.twitterCategory
        return render.twitter2(puzzle['phrases'], choices, categories, active)

class guess_tweet:
    def GET(self):
        phrase = web.input('tweet')
        name = web.input('name')
        answer = session.twitterName
        return answer
    def POST(self):
        try:
            category = web.input('category')['category']
            web.debug(category)
            session.twitterCategory = category
            web.debug('Successful Category Change')
        except AttributeError:
            session.twitterCategory = 'popular'
            web.debug("Webcode.py Line 192: AttributeError... defaulting to 'popular'")

class get_weather:
    def GET(self):
        lat = web.input(latitude=None)
        long_ = web.input(longitude=None)
        loc = web.input(location='15239')
        city = web.input(cityCode=None)
        resp = weather.getWeather2(q=loc.location, cityCode=city.cityCode, latitude=lat.latitude, longitude=long_.longitude)
        return json.dumps(
            {'conditions':resp[0], 'suggestions':resp[1]},
            sort_keys=True,
            indent=2,
            separators=(',',': ')
        )

class weather_api2:
    def GET(self):
        return render.weather2(session.prevLocation)

class test:
    def GET(self):
        def get_ip_number(ip_address):
            if ip_address == 0:
                return ''
            ipList = ip_address.split('.')
            for i in range(len(ipList)):
                ipList[i] = int(ipList[i])
            ipNum = (256 * 256 * 256 * ipList[0])+(256 * 256 * ipList[1])+(256 * ipList[2])+(ipList[3])
            return str(ipNum)
            
        IP_Address = web.ctx.ip
        IP_Number = get_ip_number(ip_address)
        
        print "Your IP Address: "+IP_Address
        print "Your IP Number: "+IP_Number
        print "Your Location: "+location

if __name__ == '__main__':
    app.run()
