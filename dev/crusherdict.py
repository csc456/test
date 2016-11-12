#!/usr/bin/env python3
debug=0

def indexName(dict, key):
 global debug
 if debug:
  print('crusherdict.py indexName()')
  print('  dict:'+dict)
  print('  key:'+str(key))
 return (dict,"X",key)

def countName(dict):
 global debug
 if debug:
  print('crusherdict.py countName()')
  print('  dict:'+dict)
 return (dict,"N")

def entryName(dict, n):
 global debug
 if debug:
  print('crusherdict.py entryName()')
  print('  dict:'+dict)
  print('  n:'+str(n))
 return (dict, "E", n)

def statusName(dict):
 global debug
 if debug:
  print('crusherdict.py statusName()')
  print('  dict:'+dict)
 return (dict, "S")

class CrusherDict:
 def __init__(self, db, name):
  """Create a set named key in the database."""
  print('crusherdict.py CrusherDict.__init__()')
  self.db=db
  self.name=name
 def __len__(self):
  try:
   return self.db.fetch(countName(self.name))
  except KeyError:
   return 0
 def __contains__(self,key):
  try:
   self.db.fetch(indexName(self.name,key))
   return True
  except KeyError:
   return False
 def status(self, key, stat=None):
  """Get and optionally set the status of the set."""
  #print('crusherdict.py CrusherDict.status()')
  name=statusName(self.name)
  try:
   old=self.db.fetch(name)
  except KeyError:
   old=None
  if stat!=None:
   self.db.store(name,stat)
  return old
 def dbgFetch(self, key):
  print('Fetch--key:'+str(key))
 def dbgStore(self, key, val):
  print('Store--key:'+str(key)+';val:'+str(val))
 def safeFetch(self, key, val=None):
  try:
   dbkey=entryName(self.name,self.db.fetch(indexName(self.name,key)))
   if(val!=None):
    self.safeStore(dbkey,key,val)
    #self.db.store(dbkey, (key,val))
   return dbkey
  except KeyError: # Actually does not exist.
   return False # TODO: Loop 5-10 times here to ensure KeyError.
  except: # Try again. (Probably corrupt request in cache)
   return self.safeFetch(key,val)
 def safeStore(self, dbkey, key, val=None):
  '''Next: Implement integrity check
  '''
  try:
   self.db.store(dbkey, (key,val))
   done=self.safeFetch(dbkey)
   if done is False: # Try again. Did not save.
    return self.safeStore(dbkey,key,val)
   #print('Want to save:'+str((key,val)))
   #print('Save in db is:'+str(done))
   #raise KeyException('test')
  except: # ....
   self.safeStore(dbkey, key, val)
   #raise Exception('test')
 def getKey(self, key, val=None):
  """Get the db key for key from the set.
     If the key is not in the set, it is added to the set.
     The value associated with key is updated unless val is None.
     The key that is used to identify the key in the db
     is returned.
  """
  #print('crusherdict.py CrusherDict.getKey()')
  dbkey=self.safeFetch(key, val)
  if dbkey:
   return dbkey
  # Does not exist. Create it.
  n=self.safeFetch(countName(self.name))
  if n is False:
   n=0
  if not isinstance(n, int):
   n=0 # Hm fix this?
  print('count name = '+str(n))
  dbkey=entryName(self.name,n)
  print('calling store1')
  #self.dbgStore(dbkey, (key,val))
#  self.db.store(dbkey, (key,val))
  self.safeStore(dbkey,key,val)
  print('calling store2')
  #self.dbgStore(indexName(self.name,key), n)
#  self.db.store(indexName(self.name,key), n)
  self.safeStore(indexName(self.name,key), n)
  print('calling store3')
  #self.dbgStore(countName(self.name),n+1)
  #self.db.store(countName(self.name),n+1)
  self.safeStore(countName(self.name),n+1)
  return dbkey
  #try:
   #self.dbgFetch(indexName(self.name,key))
   #dbkey=entryName(self.name,self.db.fetch(indexName(self.name,key)))
   #if(val!=None):
   # self.db.store(dbkey, (key,val))
   #return dbkey
  #except KeyError:
 def inc(self, key, val):
  """Increment the value for key from the set.
     If the key is not in the set, it is added to the set with value 1.
     The value is stored in the entry as an annotation.
     The key that is used to identify the key in the db
     is returned.
  """
  print('crusherdict.py CrusherDict.inc()')
  try:
   dbkey=entryName(self.name,self.db.fetch(indexName(self.name,key)))
   v=self.db.fetch(dbkey)
   self.db.store(dbkey, (key,v[1]+1,val))
   return dbkey
  except KeyError:
   try:
    n=self.db.fetch(countName(self.name))
   except KeyError:
    n=0
   dbkey=entryName(self.name,n)
   self.db.store(dbkey,(key,1,val))
   self.db.store(indexName(self.name,key), n)
   self.db.store(countName(self.name),n+1)
   return dbkey
 def __iter__(self):
  print('crusherdict.py CrusherDict.__iter__()')
  for i in range(self.__len__()):
   yield self.db.fetch(entryName(self.name,i))

if __name__=="__main__":
 import crusher
 try:
  db=crusher.Broker("test_crusherdict")
  test2=CrusherDict(db, "dict_nameA")
  test3=CrusherDict(db, "dict_nameB")
  test4=CrusherDict(db, "dict_nameC")
  
  for i in range(0,1000):
   try:
    #test.getKey("Hiddleston","name")
    test2.getKey("H","5555000")
    test3.getKey("H","6666000")
    test4.getKey("H","7777000")
   except:
    pass
  #print(test.inc("Gov-Muller","voter-809809"))
  #print(test.inc("Gov-Muller","voter-8098091"))
  #print(test.inc("Gov-Muller","voter-8098092"))
  #print(test.inc("Gov-Muller","voter-8098093"))
  #print(test.inc("Gov-Muller","voter-8098094"))
  try:
   for tup in test2:
    try:
     print(tup)
    except:
     pass
    #print('  tuple > '+str(tup))
  except:
   pass
  db.exit()
 except:
  print('err')
  pass

