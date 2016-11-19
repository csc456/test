#!/usr/bin/env python3

from crusher import Cache as TestingCache
from crusher import DataBase as TestingDb
import ast
import pickle
import math
import os.path
import random
import signal
import sys

debug=3
def vprint(str,level=0):
 '''0=Always show
    1=Sometimes show
    2=Rarely show
    3=Rarely Rarely show
 '''
 #print(' debug is:',debug)
 if level<=debug:
  print(str)

class Cache(TestingCache):
 """TODO: implement half-writes."""
 def __init__(self, s=(16,0.0001,0.0001,0.0001,0.0001)):
  TestingCache.__init__(self, s) #Nothing
 def config(self, s):
  TestingCache.config(self, s)   #Nothing
 def hash(self,key):
  #return TestingCache.hash(self, key)   #NothingChanges
  vprint('crusher.py::TestingCache::hash',3)
  vprint('  key:'+str(key),3)
  h=pickle.dumps(key)
  vprint('  dumps:'+str(h),3)
  vprint('  @return:'+str(h[-self.settings[0]:]),3)
  return h[-self.settings[0]:]
 def store(self,key,val):
  vprint('crusher.py:TestingCache::store')
  try:
   k=self.hash(key)
   self.cache[k]=(key,val)
  except:
   vprint(sys.exc_info()[0],0)
   vprint('err',0)
  vprint('  hash:'+str(k),3)
  vprint('  key:'+str(key),3)
  vprint('  val:'+str(val),3)
  #return TestingCache.store(self, key, val) #NothingChanges
 def fetch(self,key):
  TestingCache.fetch(self, key)  #NothingChanges
 def remove(self,key):
  TestingCache.remove(self, key) #NothingChanges

class DataBase(TestingDb):
 def __init__(self, filename="demo.txt"):
  self.filename='data/'+filename # Prepend a folder name here
  self.load()
 def store(self,key,val):
  TestingDb.store(self, key, val) #NothingChanges
 def fetch(self,key):
  TestingDb.fetch(self, key) #NothingChanges
 def remove(self,key):
  TestingDb.remove(self, key) #NothingChanges
 def save(self,filename=()):
  TestingDb.save(self, filename) #NothingChanges
 def load(self,filename=()):
  TestingDb.load(self, filename) #NothingChanges

#if __name__=="__main__":
# pass
