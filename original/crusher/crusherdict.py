#!/usr/bin/env python3

""" Example code, showing how to build a useful data structure for vote
    processing on top of a dictionary-like data structure.
    The data structures supports indexed access like a list and key-based
    access like a dictionary. It also has a status field that can be set.

    Author: Steven P. Crain

    This code is licensed under a Creative Commons attribution license.

    Ver 0.93, 11/11/2016: Allow counters with value None act as 0.
    Ver 0.92, 11/11/2016: Added doc strings.
"""

def indexName(dictname, key):
    """Return the underlying key used for key-based access to an item 
       identified by key in the dictlist named dictname.
    """
    return (dictname,"X",key)

def countName(dictname):
    """Return the underlying key used for access to the number of items
       in the dictlist named dictname.
    """
    return (dictname,"N")

def entryName(dictname, n):
    """Return the underlying key used for index-based access to item n
       in the dictlist named dictname.
    """
    return (dictname, "E", n)

def statusName(dictname):
    """Return the underlying key used for access to the status of the
       dictlist named dictname.
    """
    return (dictname, "S")

class CrusherDict:
    """A CrusherDict is a dictlist built on top of a dictionary.
       The dictlist is identified by a name. It has a status and
       contains items. Each item has an index, a key and a value.
       The items can be iterated in order by index and accessed
       by index and by key.

       Internally, the data is mapped onto dictionary keys and values
       according to the following scheme:

       Key: (dictname, "S")
       Value: The status of the CrusherDict.

       Key: (dictname, "N")
       Value: The number of items in the CrusherDict.

       Key: (dictname, "E", n)
       Value: Item number n from the list, stored as (key, value, when)
              When is only used when the value is a counter.

       Key: (dictname, "X", key)
       Value: The index of the item with the specified key.
    """
    def __init__(self, db, dictname):
        """Create a dictlist named dictname in the underlying database db."""
        self.db=db
        self.name=dictname
    def __len__(self):
        """Return the number of items in this CrusherDict."""
        try:
            return self.db.fetch(countName(self.name))
        except KeyError:
            return 0
    def __contains__(self,key):
        """Returns whether the key is the key of an item in the CrusherDict."""
        try:
            """Look up the key in the index."""
            self.db.fetch(indexName(self.name,key))
            """Found it in the index, so return True."""
            return True
        except KeyError:
            """Not found, so return false."""
            return False
    def status(self, stat=None):
        """Get and optionally set to stat the status of the CrusherDict.
           Returns None if the status has not been set.
        """
        name=statusName(self.name)
        try:
            """Get the stored status."""
            old=self.db.fetch(name)
        except KeyError:
            """There is no stored status."""
            old=None
        if stat!=None:
            """Store the new status."""
            self.db.store(name,stat)
        """Return the previously stored status."""
        return old
    def getKey(self, key, val=None):
        """Get the underlying key for direct access to the the item identified
           by key.
           If the key is not in the set, it is added to the set.
           The value associated with key is updated unless val is None.
           The key that is used to identify the item in the db
           is returned.
        """
        try:
            """Look up the index of the item with this key.
               Then, get the underlying key for this item.
            """
            dbkey=entryName(self.name,self.db.fetch(indexName(self.name,key)))
            if(val!=None):
                """Change the value stored for this item.
                   What we actually store is a tuple, containing the
                   key and the value.
                """
                self.db.store(dbkey, (key,val))
            """Return the underlying key."""
            return dbkey
        except KeyError:
            """There is no item with this key yet."""
            try:
                """Get the index for this new item."""
                n=self.db.fetch(countName(self.name))
            except KeyError:
                """There are no items in the list yet, so the index is 0."""
                n=0
            """get the underlying key for this item."""
            dbkey=entryName(self.name,n)
            """Create the item.
               What we actually store is a tuple, containing the
               key and the value.
            """
            self.db.store(dbkey, (key,val))
            """Create the index for the item to find it by key."""
            self.db.store(indexName(self.name,key), n)
            """Update the number of items in the list, which makes the item
               officially in the list.
            """
            self.db.store(countName(self.name),n+1)
            """Return the underlying key of the new item."""
            return dbkey
    def inc(self, key, when=None):
        """Increment the value for key from the set.
           If the key is not in the set, it is added to the set with value 1.
           when is also stored in the item, as a marker of when
           this value was last changed.
           The key that is used to identify the key in the db
           is returned.
        """
        try:
            """Look up the index of the item with this key.
               Then, get the underlying key for this item.
            """
            dbkey=entryName(self.name,self.db.fetch(indexName(self.name,key)))
            """Get the stored value."""
            v=self.db.fetch(dbkey)
            """Store the item with its new value.
               The format is (key, count, when).
            """
            if(v[1]==None):
                self.db.store(dbkey, (key,1,when))
            else:
                self.db.store(dbkey, (key,v[1]+1,when))
            """Return the undrlying key."""
            return dbkey
        except KeyError:
            """The item is not created yet."""
            try:
                """Get the index for this new item."""
                n=self.db.fetch(countName(self.name))
            except KeyError:
                """There are no items in the list yet, so the index is 0."""
                n=0
            """get the underlying key for this item."""
            dbkey=entryName(self.name,n)
            """Store the item with its new value.
               The format is (key, count, when).
            """
            self.db.store(dbkey,(key,1,when))
            """Create the index for the item to find it by key."""
            self.db.store(indexName(self.name,key), n)
            """Update the number of items in the list, which makes the item
               officially in the list.
            """
            self.db.store(countName(self.name),n+1)
            """Return the underlying key of the new item."""
            return dbkey
    def __iter__(self):
        """Iterate over the items in the CrusherDict, in index order.
           Items are represented as tuples, either (key, value) or
           (key, counter, when) tuples.
        """
        """Find out how many items there are, and loop over the indexes."""
        for i in range(self.__len__()):
            """Yield each item in term. """
            yield self.db.fetch(entryName(self.name,i))

if __name__=="__main__":
    """Make a Crusher database."""
    import crusher
    db=crusher.Broker("test_crusherdict")
    
    """Make a CrusherDict dictlist to play with."""
    test=CrusherDict(db, "test")
    """Add an item with key "Hiddleston" and value "name"."""
    print(test.getKey("Hiddleston","name"))
    """Increment the counter with key "Gov-Muller" and when "voter-809809"."""
    print(test.inc("Gov-Muller","voter-809809"))
    """Iterate over the items in the dictlist."""
    for tup in test:
        """Print each item."""
        print(tup)
    """Close the Crusher database."""
    db.exit()
