#!/usr/bin/env python3

from crusher import Cache as TestingCache

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
 #def dumpCache(self:

#if __name__=="__main__":
# pass
