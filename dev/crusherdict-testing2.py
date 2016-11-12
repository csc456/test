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
  #print('crusherdict.py CrusherDict.__init__()')
  self.db=db
  self.name=name
 def __len__(self):
  #f = self.safeFetch(countName(self.name))
  #print(f)
  #raise Exception('len:'+str(f))
  try:
   #f = self.safeFetch(countName(self.name))   
   #print(f)
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
  name=statusName(self.name)
  try:
   old=self.db.fetch(name)
  except KeyError:
   old=None
  if stat!=None:
   self.db.store(name,stat)
  return old
 def safeFetch(self, key, val=None):
  '''Only to be used in place of getKey(self, key, val)
     Do not replace self.db.fetch(...)
     Retrieve dbkey. If no dbkey then return False.
     If error then try to retrieve again.
     If val!=None then safeStore(val).
  '''
  try:
   f=self.db.fetch(indexName(self.name,key))
   dbkey=entryName(self.name,f)
   if val!=None:
    self.safeStore(dbkey,key,val)
   return dbkey
  except KeyError: # Actually does not exist.
   return False # TODO: Loop 5-10 times here to ensure KeyError.
   # TODO: Store? #self.safeStore()
  except: # Try again. (Probably corrupt request in cache)
   return self.safeFetch(key,val)
 def safeStore(self, dbkey, key, val=None):
  '''Next:...
  '''
  try:
   if val is None: #?
    self.db.store(dbkey, key)
   else: # tuple
    self.db.store(dbkey, (key,val))
   done=self.safeFetch(dbkey) # Write to db until exists
   if done is False: # Try again.
    return self.safeStore(dbkey,key,val)
  except: # ....
   self.safeStore(dbkey, key, val)
 def getKey(self, key, val=None):
  """Get the db key for key from the set.
     If the key is not in the set, it is added to the set.
     The value associated with key is updated unless val is None.
     The key that is used to identify the key in the db
     is returned.
  """
  print('crusherdict.py CrusherDict.getKey()')
  print('  key:'+str(key))
  print('  value:'+str(val))
  dbkey=self.safeFetch(key, val)
  if dbkey:
   print('  dbkey='+str(dbkey)) 
   return dbkey
  print('  dbkey=False [!]') 
  n=self.safeFetch(countName(self.name))  # Does not exist. Create it.
  if n is False:
   n=0
  if not isinstance(n, int):
   n=0 # Hm fix this?
  print('  n='+str(n))
  dbkey=entryName(self.name,n)
  self.safeStore(dbkey,key,val)
  self.safeStore(indexName(self.name,key), n)
  self.safeStore(countName(self.name),n+1)
  return dbkey
 def inc(self, key, val):
  """Increment the value for key from the set.
     If the key is not in the set, it is added to the set with value 1.
     The value is stored in the entry as an annotation.
     The key that is used to identify the key in the db
     is returned.
  """
  print('crusherdict.py CrusherDict.inc()')
  print('  key:'+str(key))
  print('  value:'+str(val))
  try: # TODO: What happens if the dbkey does not exist here?
   dbkey=self.safeFetch(indexName(self.name,key))
   if dbkey is False:
    raise Exception('...1')
   dbkey=entryName(self.name,dbkey)
   #if dbkey is False:
   # raise Exception('...2')
   v=self.safeFetch(dbkey)
   if v is False:
    raise Exception('...3')
   self.safeStore(dbkey, (key,v[1]+1,val))
   print('  dbkey is True!')
   print('  dbkey is:'+str(dbkey))
   return dbkey
  except:
#  except KeyError:
   n=self.safeFetch(countName(self.name))
   if n is False:
    n=0
   if not isinstance(n, int):
    n=0 # Hm fix this?
   print('  dbkey is False!')
   print('  n is:'+str(n))
   # n either 1) int eg "1",
   #          2) tuple, eg ('T_____________________________________', 'E', (1, None))
   # In the case of 2 this is coming from eg
   #          t.inc("voters",context["id"])
   # ...
   dbkey=entryName(self.name,n)
   print('  dbkey is:'+str(dbkey))
   print('  Try store:')
   print('   key:'+str(dbkey))
   print('   value:'+str((key,1,val)))
   self.safeStore(dbkey,(key,1,val))
   print('  Try store:')
   print('   key:'+str(indexName(self.name,key)))
   print('   value:'+str(n))
   self.safeStore(indexName(self.name,key),n)
   print('  Try store:')
   print('   key:'+str(countName(self.name)))
   print('   value:'+str(n+1))
   self.safeStore(countName(self.name),n+1)
   #self.db.store(dbkey,(key,1,val))
   #self.db.store(indexName(self.name,key), n)
   #self.db.store(countName(self.name),n+1)
   return dbkey
 def __iter__(self):
  print('crusherdict.py CrusherDict.__iter__()')
  for i in range(self.__len__()):
   yield self.safeFetch(entryName(self.name,i))
     #yield self.db.fetch(entryName(self.name,i))

if __name__=="__main__":
 import crusher
 try:
  db=crusher.Broker("test_crusherdict")
  test2=CrusherDict(db, "dict_nameA")
  test3=CrusherDict(db, "dict_nameB")
  test4=CrusherDict(db, "dict_nameC")
  
  for i in range(0,10000):
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

