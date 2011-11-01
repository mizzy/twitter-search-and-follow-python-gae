# -*- coding: utf-8 -*-
import os
import md5
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from basehandler import BaseHandler, h
import simplejson
import appengine_utilities.sessions
from appengine_twitter import AppEngineTwitter
import urllib
import re

if re.match('Development', os.environ['SERVER_SOFTWARE']):
    OAUTH_KEY    = 'XXXXXXXXXXXXXXXXXXXXX'
    OAUTH_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
else:
    OAUTH_KEY    = 'XXXXXXXXXXXXXXXXXXXXX'
    OAUTH_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

class IndexHandler(BaseHandler):
    def get(self):
        twitter = AppEngineTwitter()
        session = appengine_utilities.sessions.Session(writer='cookie')

        if 'access_secret' in session:
            twitter.set_oauth(OAUTH_KEY,
                              OAUTH_SECRET,
                              session['access_token'],
                              session['access_secret'],
                              )
            twitter.verify()
            template_values = {
                'my': simplejson.loads(twitter.last_response.content)
              }
            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, template_values))
        else:
            twitter.set_oauth(OAUTH_KEY, OAUTH_SECRET)
            req_info = twitter.prepare_oauth_login()
            session['request_token']  = req_info['oauth_token']
            session['request_secret'] = req_info['oauth_token_secret']
            self.redirect(req_info['url'])

class SearchHandler(BaseHandler):
    def get(self):
        twitter = AppEngineTwitter()
        session = appengine_utilities.sessions.Session(writer='cookie')

        if not session.has_key('access_token'):
            twitter.set_oauth(OAUTH_KEY, OAUTH_SECRET)
            req_info = twitter.prepare_oauth_login()
            session['request_token']  = req_info['oauth_token']
            session['request_secret'] = req_info['oauth_token_secret']
            return self.redirect(req_info['url'])
            
        twitter.set_oauth(OAUTH_KEY,
                          OAUTH_SECRET,
                          session['access_token'],
                          session['access_secret'],
                          )

        twitter.friends_ids()
        friends = simplejson.loads(twitter.last_response.content)

        query = self.request.get('query')
        page  = self.request.get('page') or 1
        
        results = twitter.search(
            query.encode('utf8'),
            {'rpp': 50,
             'page': page,
             }
            )

        for result in results:
            if result['from_user_id'] in friends:
                result['is_following'] = 1
            result['unique_id'] = md5.new(result['from_user'] + result['created_at']).hexdigest()

        twitter.verify()
        my = simplejson.loads(twitter.last_response.content)

        template_values = {
            'query':   query,
            'encoded_query': urllib.quote(query.encode('utf8')),
            'results': results,
            'my':      my,
            'page':    page,
            'users':   results,
            }

        path = os.path.join(os.path.dirname(__file__), 'search.html')
        self.response.out.write(template.render(path, template_values))

class FollowHandler(BaseHandler):
    def get(self):
        twitter = AppEngineTwitter()
        session = appengine_utilities.sessions.Session(writer='cookie')
        twitter.set_oauth(OAUTH_KEY,
                          OAUTH_SECRET,
                          session['access_token'],
                          session['access_secret'],
                          )

        screen_name = self.request.get('screen_name')
        res = twitter.follow(screen_name)
        self.response.out.write(simplejson.dumps({
            'name': screen_name,
            'code': res,
            'id'  : self.request.get('id'),
            }))

class OAuthHandler(BaseHandler):
    def get(self):
        twitter = AppEngineTwitter()
        twitter.set_oauth(OAUTH_KEY, OAUTH_SECRET)

        # TwitterからHTTP GETでrequest_tokenが渡される
        req_token = self.request.get('oauth_token')
 

        # request_tokenとaccess_tokenを交換する
        session = appengine_utilities.sessions.Session(writer='cookie')
        acc_token = twitter.exchange_oauth_tokens(req_token, session['request_secret'])

        session['access_token']  = acc_token['oauth_token']
        session['access_secret'] = acc_token['oauth_token_secret']

        self.redirect('/')

class LogoutHandler(BaseHandler):
    def get(self):
        session = appengine_utilities.sessions.Session(writer='cookie')
        session.delete_item('access_token')
        session.delete_item('access_secret')
        self.redirect('/')

        
routing = [
    ('/oauth_callback', OAuthHandler),
    ('/search', SearchHandler),
    ('/follow', FollowHandler),
    ('/logout', LogoutHandler),
    ('/', IndexHandler),
    ]
    
application = webapp.WSGIApplication(
                                     routing,
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
