#!/usr/bin/env python3

import ast
import pickle
import math
import os.path
import random
import signal
import sys

def failure(rate, data):
    """Return whether any failures happened processing data with
       the given rate.
    """
    return (random.random() >= math.exp(-failureTime(rate,data)))

def failures(rate, n):
    """Return the number of failures that happened processing data with
       the given failure rate.
    """
    t=rate*n
    r=random.random()
    prob=math.exp(-t)
    n=0
    while(r>=prob and prob>0):
        r=r-prob
        n=n+1
        prob=prob*t/n
    return n

def failureTime(rate, data):
    """Return the amount of time based on the rate and number
       of bits in data.
    """
    return rate*len(str(data))*8

class Cache:
    """TODO: implement half-writes."""
    def __init__(self, s=(16,0.0001,0.0001,0.0001,0.0001)):
        self.settings=s
        self.cache={}
    def config(self, s):
        """Update Configuration"""
        self.settings=s
    def hash(self,key):
        h=pickle.dumps(key)
        return h[-self.settings[0]:]
    def store(self,key,val):
        self.cache[self.hash(key)]=(key,val)
    def fetch(self,key):
        n=len(self.cache)
        if(n==0):
             raise KeyError(key)
        hk=self.hash(key)
        if(failure(self.settings[3],key)):
            return list(self.cache.values())[random.randrange(n)]
        if(hk in self.cache):
            e=self.cache[hk]
            if(e[0]==key or failure(self.settings[1],key)):
                return e[1]
        raise KeyError(key)
    def remove(self,key):
        if key in cache:
            del cache[key]

class DataBase:
    def __init__(self, filename="demo.txt"):
        self.filename=filename
        self.load()
    def store(self,key,val):
        self.cache[key]=val
    def fetch(self,key):
        return self.cache[key]
    def remove(self,key):
        if key in cache:
            ret=cache[key]
            del cache[key]
            return ret
        else:
            raise KeyError(key)
    def save(self,filename=()):
        """Save the contents of the database into a file."""
        if(len(filename)==0):
            filename=self.filename
        filename=os.path.splitext(filename)[0]
        of=open(filename+"_db.dat", 'wb')
        pickle.dump(self.cache, of)
        of.close()
        of=open(filename+"_db.txt", 'w')
        for (k,v) in self.cache.items():
             of.write("{}\t{}\n".format(str(k),str(v)))
        of.close()
    def load(self,filename=()):
        """Load the contents of the database into a file."""
        if(len(filename)==0):
            filename=self.filename
        filename=os.path.splitext(filename)[0]
        try:
            self.cache=pickle.load(open(filename+"_db.dat", 'rb'))
        except FileNotFoundError:
            self.cache={}

class Channel:
    """TODO: Implement scramble."""
    def __init__(self, s=(0.0001, 0.0001, 0.0001)):
        self.hasPrev=False
        self.settings=s
    def config(self, s):
        self.settings=s
    def mangle(self, data):
        if(self.hasPrev and failure(self.settings[1],data)):
            return self.prev
        self.prev=data
        self.hasPrev=True
        if(failure(self.settings[2],data)):
            return self.scramble(data)
        return self.bitflip(data)
    def scramble(self, data):
        return data
    def bitflip(self, data):
        """Possibly flip bits in data based on the failure rate."""
        try:
            """Try processing as a character."""
            c=ord(data)
            n=math.ceil(math.log2(c+1))+1 
            for i in range(failures(self.settings[0],n)):
                c=c^(2**random.randrange(n))
            return chr(c)
        except TypeError:
            """Do nothing"""
        try:
            """Try processing as a string."""
            return "".join(chr(self.bitflip(ord(c))) for c in data)
        except TypeError:
            """Do nothing"""
        try:
            """Try processing as a number."""
            if data<0:
                """If data is negative, return the positive version if
                   the sign bit is flipped.
                """
                data=self.bitflip(-data)
                if(failure(self.settings[0],1)):
                    return data
                else:
                    return -data
            n=math.ceil(math.log2(data+1))+1 
            try:
                """If the number is like an integer, possibly flip bits
                   starting with the leading 0.
                """
                for i in range(failures(self.settings[0],n)):
                    data=data^(2**random.randrange(n))
            except KeyError:
                """If the number is like a float, flip any of the first 24
                   bits.
                """
                for i in range(failures(self.settings[0],24)):
                    bit=2**(n-random.randrange(n))
                    val=math.floor(data/bit)
                    if val==math.floor(0.5*val)*2:
                        """Bit is not set."""
                        data=data+bit
                    else:
                        data=data-bit
            return data
        except TypeError:
            """Do nothing."""
        try:
            """If data is iterable, return a tuple of bitflipped items."""
            return tuple(self.bitflip(x) for x in data)
        except TypeError:
            """If we cannot figure out how to mangle, just return it as-is."""
            return data

class Broker:
    def __init__(self, filename="demo.txt"):
        random.seed()
        self.cache=Cache()
        self.db=DataBase(filename)
        self.keyIn=Channel()
        self.valIn=Channel()
        self.keyCache=Channel()
        self.valCacheOut=Channel()
        self.valCacheIn=Channel()
        self.keyDB=Channel()
        self.valDBOut=Channel()
        self.valDBIn=Channel()
        self.configurables=(self.cache, self.keyIn, self.valIn, self.keyCache, self.valCacheIn, self.valCacheOut, self.keyDB, self.valDBIn, self.valDBOut)
        self.doExit=False
        signal.signal(signal.SIGINT, self.interrupt)
    def configure(self,s):
        """Process configuration message s."""
        s=ast.literal_eval(s)
        try:
            for c in s[0]:
                self.configurables[c].config(s[1:])
        except TypeError:
            self.configurables[s[0]].config(s[1:])
    def interrupt(self, signal, frame):
        self.doExit=True
    def store(self,key,val):
        key=self.keyIn.mangle(key)
        val=self.valIn.mangle(val)
        self.cache.store(self.keyCache.mangle(key),self.valCacheOut.mangle(val))
        self.db.store(self.keyDB.mangle(key),self.valDBOut.mangle(val))
    def fetch(self,key):
        key=self.keyIn.mangle(key)
        try:
            return self.valCacheIn.mangle(self.cache.fetch(self.keyCache.mangle(key)))
        except KeyError:
            return self.valDBIn.mangle(self.db.fetch(self.keyDB.mangle(key)))
    def remove(self,key):
        self.cache.remove(self.keyCache.mangle(key))
        return self.valDBIn.mangle(self.db.remove(self.keyDB.mangle(key)))
    def exit(self):
        self.db.save()
        print("Goodbye!")

if __name__ == "__main__":
    key=("hello","world")
    val=("by","jove")
    keystr="{}".format(key)
    
    cache=Broker("test_crusher")
    cache.store("h","v")
    cache.store(key,val)
    
    cache.store(("test","m",12,-76,7.234,-8.763,10004.3422,(123,"h")),"test")
    try:
        print(cache.fetch(key))
    except KeyError as error:
        print("Not found")
    
    cache.store(("goodbye","world"),13)
    
    try:
        print(cache.fetch(key))
    except KeyError as error:
        print("Not found")
    
    try:
        print(cache.fetch(1))
    except KeyError as error:
        print("Not found")
    
    print("Please press Ctrl-C")
    while not cache.doExit:
        signal.pause()
    
    cache.exit()

