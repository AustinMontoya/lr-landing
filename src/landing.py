#!/usr/bin/env python

import sys
from brubeck.request_handling import Brubeck, WebMessageHandler
from brubeck.templating import Jinja2Rendering,load_jinja2_env
import json
import pymongo
import redis
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
        client = redis.Redis()    
        ids = client.lrange('ids',0,-1)        
        return self.render_template('docs.html',ids=ids)


class IndexHandler(Jinja2Rendering):
  def get(self):
        return self.render_template('index.html')


class KeysHandler(Jinja2Rendering):
  def get(self):
      client = redis.Redis()    
      keys = client.lrange('keys',0,-1)
      return self.render_template('keys.html',keys=keys)

class KeyHandler(Jinja2Rendering):
  def get(self,keyword):
      print 'got here'
      client = redis.Redis()    
      ids = client.lrange(keyword,0,-1)    
      return self.render_template('docs.html',ids=ids)

urls = [(r'^/keys/(\w+)$',KeyHandler), 
        (r'^/keys',KeysHandler),
        (r'^/docs/(\w+)$', DocHandler),        
        (r'^/docs', DocsHandler),
        (r'^/', IndexHandler)]
                
mongrel2_pair = ('tcp://127.0.0.1:9997', 'tcp://127.0.0.1:9996')

app = Brubeck(mongrel2_pair=mongrel2_pair,
              handler_tuples=urls,
              template_loader=load_jinja2_env('./templates'))
app.run()
