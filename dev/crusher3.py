#!/usr/bin/env python3

from crusher import Cache as TestingCache
from crusher import DataBase as TestingDb

class Cache(TestingCache):
 """TODO: implement half-writes."""
 def __init__(self, s=(16,0.0001,0.0001,0.0001,0.0001)):
  return TestingCache.__init__(self, s) #NothingChanges
 def config(self, s):
  return TestingCache.config(self, s)   #NothingChanges
 def hash(self,key):
  return TestingCache.hash(self, key)   #NothingChanges
 def store(self,key,val):
  return TestingCache.store(self, key, val) #NothingChanges
 def fetch(self,key):
  return TestingCache.fetch(self, key)  #NothingChanges
 def remove(self,key):
  return TestingCache.remove(self, key) #NothingChanges

class DataBase(TestingDb):
 def __init__(self, filename="demo.txt"):
  self.filename='data/'+filename # Prepend a folder name here
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

#if __name__=="__main__":
# pass
