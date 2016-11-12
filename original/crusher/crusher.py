#!/usr/bin/env python3

""" Crusher, (C) 2016 Steven P. Crain, steven.crain@plattsburgh.edu
    Licensed with a creative commons non-commercial attribution license.

    Crusher is an in-memory database with configurable failure rates.
    Crusher is intended to simulate data failures for reliable
    systems homework assignments and projects.

    Ver 0.92, 11/11/2016: Added version and configuration history to
                          text persistence file. Added doc strings.
"""

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
    """Noisy Cache: a cache that is suceptible to failures."""
    def __init__(self, s=(16,0.0001,0.0001,0.0001,0.0001)):
        """Initialize with list of cache settings,
           s[0] is the size of the cache: the size of the key converted with
                hash().
           s[1] is the failure rate for False Hits.
           s[2] is the failure rate for Random Hits.
           s[3] is the failure rate for Key Half-Writes.
           s[4] is the failure rate for Value Half-Writes.
        """
        self.settings=s
        self.cache={}
    def config(self, s):
        """Update cache settings with a list of cache settings,
           s[0] is the size of the cache: the size of the key converted with
                hash().
           s[1] is the failure rate for False Hits.
           s[2] is the failure rate for Random Hits.
           s[3] is the failure rate for Key Half-Writes.
           s[4] is the failure rate for Value Half-Writes.
        """
        self.settings=s
    def hash(self,key):
        """Compute the location of a key in cache. The key is pickled, and some
           number of trailing bytes is returned based on the cache size
           setting.
        """
        h=pickle.dumps(key)
        return h[-self.settings[0]:]
    def store(self,key,val):
        """Store the key-value pair in the cache."""
        hk=self.hash(key)
        if(hk in self.cache.keys()):
            if(failure(self.settings[3],key)):
                """Key Half-Write Failure"""
                key=self.cache[self.hash(key)][0]
            if(failure(self.settings[4],val)):
                """Value Half-Write Failure"""
                val=self.cache[self.hash(key)][1]
        self.cache[self.hash(key)]=(key,val)
    def fetch(self,key):
        """Retrieve a cached value, if found. Raises a KeyError if not found
           in cache.
        """
        n=len(self.cache)
        if(n==0):
             """Early exit if the cache is empty."""
             raise KeyError(key)
        hk=self.hash(key)
        if(failure(self.settings[2],key)):
            """Random Hit Failure"""
            return list(self.cache.values())[random.randrange(n)]
        if(hk in self.cache):
            e=self.cache[hk]
            if(e[0]==key or failure(self.settings[1],key)):
                """True Hit or False Hit Failure"""
                return e[1]
        """If not found in cache, raise KeyError."""
        raise KeyError(key)
    def remove(self,key):
        """Remove a key from cache, if present."""
        hk=self.hash(key)
        if hk in self.cache.keys():
            del cache[hk]

class DataBase:
    """In-memory database with persistence on open/close."""
    def __init__(self, filename="demo.txt"):
        """Create a database persisted to filename."""
        self.filename=filename
        self.load()
    def store(self,key,val):
        """Store a key-value pair in the database."""
        self.cache[key]=val
    def fetch(self,key):
        """Fetch the value associate with a key in the database."""
        return self.cache[key]
    def remove(self,key):
        """Remove the key and its value from the database.
           Returns the value that was in the database.
           Raises a KeyError if the key is not in the database.
        """
        if key in cache:
            ret=cache[key]
            del cache[key]
            return ret
        else:
            raise KeyError(key)
    def save(self,history,filename=None):
        """Save the contents of the database into a file."""
        if(filename==None):
            filename=self.filename
        filename=os.path.splitext(filename)[0]
        of=open(filename+"-db.dat", 'wb')
        pickle.dump(self.cache, of)
        of.close()
        of=open(filename+"-db.txt", 'w')
        of.write("Crusher ver 0.92\n")
        for (op,s) in history:
             of.write("CONF\t{}\t{}\n".format(s,op))
        for (k,v) in self.cache.items():
             of.write("{}\t{}\n".format(str(k),str(v)))
        of.close()
    def load(self,filename=()):
        """Load the contents of the database into a file."""
        if(len(filename)==0):
            filename=self.filename
        filename=os.path.splitext(filename)[0]
        try:
            self.cache=pickle.load(open(filename+"-db.dat", 'rb'))
        except FileNotFoundError:
            self.cache={}

class Channel:
    """Noisy Channel implementation."""
    def __init__(self, s=(0.0001, 0.0001, 0.0001)):
        """Create a noisy channel with the specified settings."""
        self.hasPrev=False
        self.settings=s
    def config(self, s):
        """Change the settings of the noisy channel."""
        self.settings=s
    def mangle(self, data):
        """Return the data, with some bits possibly changed."""
        if(self.hasPrev and failure(self.settings[1],data)):
            """Clone failure"""
            return self.prev
        self.prev=data
        self.hasPrev=True
        if(failure(self.settings[2],data)):
            """Scramble failure"""
            return self.scramble(data)
        """Bit flip faliure"""
        return self.bitflip(data)
    def scramble(self, data):
        """Return the data with the bits scrambled.
           TODO: Scramble is not impleented.
        """
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
    """Broker implements a noisy hash database, with configurable failure
       rates.
    """
    def __init__(self, filename="demo.txt"):
        """Create a broker with default settings that persist to filename."""
        random.seed()
        self.history=[(0,"defaults")]
        self.ops=0
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
        self.history.append((self.ops,s))
        s=ast.literal_eval(s)
        try:
            for c in s[0]:
                self.configurables[c].config(s[1:])
        except TypeError:
            self.configurables[s[0]].config(s[1:])
    def interrupt(self, signal, frame):
        """Flag that an interrupt was received and we should exit ASAP."""
        self.doExit=True
    def store(self,key,val):
        """Store a key-value pair in the database."""
        self.ops+=1
        key=self.keyIn.mangle(key)
        val=self.valIn.mangle(val)
        self.cache.store(self.keyCache.mangle(key),self.valCacheOut.mangle(val))
        self.db.store(self.keyDB.mangle(key),self.valDBOut.mangle(val))
    def fetch(self,key):
        """Fetch the value of a key from the database.
           Return the value of the key.
           Raise a KeyError if the key is not in the database.
        """
        self.ops+=1
        key=self.keyIn.mangle(key)
        try:
            """Return the value from cache if the key is in the cache."""
            return self.valCacheIn.mangle(self.cache.fetch(self.keyCache.mangle(key)))
        except KeyError:
            """Return the value from the database if the key is in the DB."""
            return self.valDBIn.mangle(self.db.fetch(self.keyDB.mangle(key)))
    def remove(self,key):
        """Remove the key from cache and database. Return the old value from
           the database.
           Raises KeyError if the key was not in the database.
        """
        self.ops+=1
        self.cache.remove(self.keyCache.mangle(key))
        return self.valDBIn.mangle(self.db.remove(self.keyDB.mangle(key)))
    def exit(self):
        """Persist the database in preparation to exit."""
        self.db.save(self.history)
        print("Goodbye!")

if __name__ == "__main__":
    key=("hello","world")
    val=("by","jove")
    keystr="{}".format(key)
    
    """Create a Crusher."""
    cache=Broker("test_crusher")
    
    """Store a simple key-value pair."""
    cache.store("h","v")
    
    """Store a more complex key-value pair."""
    cache.store(key,val)
    
    """Store using a key that contains a wide variety of data types."""
    cache.store(("test","m",12,-76,7.234,-8.763,10004.3422,(123,"h")),"test")
    
    try:
        """Try retrieving using the complex key."""
        print(cache.fetch(key))
    except KeyError as error:
        """It should work, but could give an error if the complex key was
           corrupted.
        """
        print("Not found")
    
    """Try to knock the complex key out of the cache with a similar key."""
    cache.store(("goodbye","world"),13)
    
    try:
        """Try retrieving using the complex key."""
        print(cache.fetch(key))
    except KeyError as error:
        print("Not found")
    
    try:
        """Try fetching a key that has not been added."""
        print(cache.fetch(1))
    except KeyError as error:
        print("Not found")
    
    """Test the ctrl-C handling logic."""
    print("Please press Ctrl-C")
    while not cache.doExit:
        """Ctrl-C has not been detected yet, so wait until something happens.
        """
        signal.pause()
    
    """Since we got here, Ctrl-C has been pressed."""
    cache.exit()

