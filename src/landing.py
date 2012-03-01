#!/usr/bin/env python

import sys
from brubeck.request_handling import Brubeck, WebMessageHandler
from brubeck.templating import Jinja2Rendering,load_jinja2_env
import json
import pymongo
import redis
import urllib
from bson.objectid import ObjectId
from gevent.monkey import *
patch_all()
class DocHandler(Jinja2Rendering):
    def get(self,id):
        conn = pymongo.Connection()
        doc = conn.lr.envelope.find_one({'_id':ObjectId(id)})
        return self.render_template('doc.html',doc=doc)

class DocsHandler(Jinja2Rendering):
    def get(self):    
        try:
            start = int(self.get_argument('pos'))
        except:
            start = 0      
        ids = self.db_conn.lrange('ids',start,start+100)        
        args = {'ids':ids}
        if len(ids) > 100:
          args['nextUrl'] ="/docs?pos="+str(start+100)
        return self.render_template('docs.html',**args)


class IndexHandler(Jinja2Rendering):
    def get(self):
        return self.render_template('index.html')


class KeysHandler(Jinja2Rendering):
  def get(self):
      try:
          start = int(self.get_argument('pos'))
      except:
          start = 0
      keys = self.db_conn.lrange('keys',start,start+100)
      args = {'keys':keys}
      if len(keys) > 100:
        args['pos']=str(start+100)
      return self.render_template('keys.html',**args)

class KeyHandler(Jinja2Rendering):
    def get(self,keyword):
        keyword = urllib.unquote(keyword)
        try:
            start = int(self.get_argument('pos'))
        except:
            start = 0      
        ids = self.db_conn.lrange(keyword,start,start+100)        
        args = {'ids':ids}
        if len(ids) > 100:
          args['nextUrl'] = nextUrl="/keys/%s?pos=%d" % (keyword,start+100)
        return self.render_template('docs.html',**args)
class SitemapHandler(Jinja2Rendering):
    def get(self):
        ids = self.db_conn.lrange('ids',0,-1) 
        self.headers["Conent-Type"] = 'text/xml'
        return self.render_template('sitemap.xml',ids=ids)      
urls = [(r'^/sitemap.xml',SitemapHandler),
        (r'^/keys/(.+)$',KeyHandler), 
        (r'^/keys',KeysHandler),
        (r'^/docs/(.+)$', DocHandler),        
        (r'^/docs', DocsHandler),
        (r'^/', IndexHandler)]
                
mongrel2_pair = ('tcp://127.0.0.1:9997', 'tcp://127.0.0.1:9996')

app = Brubeck(mongrel2_pair=mongrel2_pair,
              handler_tuples=urls,
              db_conn = redis.Redis(),
              template_loader=load_jinja2_env('./templates'))
app.run()
