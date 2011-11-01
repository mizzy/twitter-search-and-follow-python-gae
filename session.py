#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from google.appengine.ext import db
from google.appengine.api import memcache
import time
import hashlib

#このクラスを派生させてセッションのデータを作る
class StoreData(db.Model):
 createstime = db.DateTimeProperty(auto_now_add=True)
 sessionid = db.StringProperty()

#セッションの初期化、登録
def make(request, response, store, otherdata=""):
 #セッションIDの生成
 hashdata = hashlib.sha1()
 hashdata.update(str(request.remote_addr) + str(time.time()) + otherdata)
 sessionid = hashdata.hexdigest()
 
 #データストア
 storedata = store
 storedata.createtime = time.time()
 storedata.sessionid = sessionid
 storedata.put()
 
 #Memcache
 memcache.add(sessionid, storedata)
 
 #Cookie
 response.headers.add_header(
  "Set-Cookie", 
  "sessionid=%s;expires=Fri, 31-Dec-2020 23:59:59 GMT" % sessionid)

#セッションの削除
def delete(sessionid, Model=StoreData, response=None):
 storedata = db.Query(Model).filter("sessionid = ", sessionid).get()
 if storedata is not None:
  db.delete(storedata)
 else:
  #エラー処理
  pass
 if not memcache.delete(sessionid):
  #エラー処理
  pass
 #必要とあらばCookieも削除してあげるよ
 if response is not None:
  response.headers.add_header("Set-Cookie", "sessionid=0;expires=Fri, 01-Jan-1950 00:00:00 GMT")

#有効なセッションかどうか調べる
def isvalidsession(sessionid, Model=StoreData):
 results = memcache.get(sessionid)
 if results is not None:
  return True

 results = db.Query(Model).filter("sessionid = ", sessionid).get()
 if results is not None:
  return True
 else:
  return False

#セッションIDを元に情報を得る
def getinfo_id(sessionid, Model=StoreData):
 result = memcache.get(sessionid)
 if result is not None:
  return result

 result = db.Query(Model).filter("sessionid = ", sessionid).get()
 if result is not None:
  return result
 else:
  return None
#Cookieを元に情報を得る（実際はgetinfo_id任せ）
def getinfo_cookie(cookies, Model=StoreData):
 if not cookies.has_key("sessionid"):
  return None
 return getinfo_id(cookies["sessionid"], Model)
