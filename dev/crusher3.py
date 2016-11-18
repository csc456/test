#!/usr/bin/env python3

from crusher import Cache as TestingCache
import vprint

class Cache(TestingCache):
    """TODO: implement half-writes."""
    def __init__(self, s=(16,0.0001,0.0001,0.0001,0.0001)):
        return TestingCache.__init__(self, s) #NothingChanges
    def config(self, s):
        return TestingCache.config(self, s)   #NothingChanges
    def hash(self,key):
        return TestingCache.hash(self, key)   #NothingChanges
    def store(self,key,val):
        h=self.hash(key)
        self.cache[h]=(key,val)
        print(' self.cache store:key',key)
        print(' self.cache store:val',val)
        print(' self.cache store:h',h)
        print(' self.cache=',self.cache)
        #return TestingCache.__init__(self, s) #NothingChanges
    def fetch(self,key):
        return TestingCache.fetch(self, key) #NothingChanges
    def remove(self,key):
        return TestingCache.remove(self, key) #NothingChanges
