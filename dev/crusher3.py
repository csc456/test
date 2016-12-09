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
from vprint import vprint #vprint

class Cache(TestingCache):
 """TODO: implement half-writes."""
 def __init__(self, s=(16,0.0001,0.0001,0.0001,0.0001)):
  return TestingCache.__init__(self, s) #Nothing
 def config(self, s):
  return TestingCache.config(self, s)   #Nothing
 def hash(self,key):
  #return TestingCache.hash(self, key)   #NothingChanges
  vprint(3,'crusher.py::TestingCache::hash')
  vprint(3,'  key:'+str(key))
  h=pickle.dumps(key)
  vprint(3,'  dumps:'+str(h))
  vprint(3,'  @self.settings:'+str(self.settings))
  vprint(3,'  @self.settings[0]:'+str(self.settings[0]))
  vprint(3,'  @return:'+str(h[-self.settings[0]:]))
  return h[-self.settings[0]:]
 def store(self,key,val):
  #try:
  # k=self.hash(key)
  # self.cache[k]=(key,val)
  #except:
  # vprint(3,sys.exc_info()[0],0)
  return TestingCache.store(self, key, val) #NothingChanges
 def fetch(self,key):
  return TestingCache.fetch(self, key)  #NothingChanges
 def remove(self,key):
  return TestingCache.remove(self, key) #NothingChanges

class DataBase(TestingDb):
 def __init__(self, filename="demo.txt"):
  #self.filename='data/'+filename # Prepend a folder name here
  self.filename=filename # Prepend a folder name here
  self.load()
 def store(self,key,val):
  return TestingDb.store(self, key, val) #NothingChanges
 def fetch(self,key):
  return TestingDb.fetch(self, key) #NothingChanges
 def remove(self,key):
  return TestingDb.remove(self, key) #NothingChanges
 def save(self,filename=()):
  return TestingDb.save(self, filename) #NothingChanges
 def load(self,filename=()):
  return TestingDb.load(self, filename) #NothingChanges

if __name__=="__main__":
 vprint(2,'test')
 pass
