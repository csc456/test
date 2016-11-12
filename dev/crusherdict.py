#!/usr/bin/env python3
debug=0
import sys

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
# def
 def safeFetch(self, key):
  '''Try a number of fetches. Voting on which is best.
     Probably bitwise.
  '''
  print('safeFetch::')
  print('  key:'+str(key))
  c={'__key_error__':0,'__none__':0}
  best=None
  num=0
  i=0
  print('  try200')
  while i<200:
   i+=1
   try:
    n=self.db.fetch(key)
   except KeyError:
    c['__key_error__']+=1
    if c['__key_error__'] > num:
     best='__key_error__'
     num=c['__key_error__']
    continue
   except: #others
    c['__none__']+=1
    if c['__none__'] > num:
     best='__none__'
     num=c['__none__']
    continue
   try:
    c[str(n)]+=1 # fetch success
   except:
    c[str(n)]=1 # instantiate
   if c[str(n)] > num:
    best=n
    num=c[str(n)]
  # Raise KeyError in both cases
  print('  best='+str(best))
  if best == '__key_error__' or best == '__none__':
   print('  raise KeyError.....')
   raise KeyError('--')
  else:
   return n
 def safeStore(self, dbkey, key, val=None):
  '''Next:...
  '''
  print('safeStore::')
  print('  dbkey='+str(dbkey))
  print('  key='+str(key))
  print('  val='+str(val))
  try:
   if val is None:
    print('  store:')
    print('  store-dbkey:'+str(dbkey))
    print('  store-key:'+str(key))
    self.db.store(dbkey, key)
   else: # tuple
    self.db.store(dbkey, (key,val))
   # Now try fetching by dbkey
   try:
    done=self.safeFetch(dbkey)
   except: # Raised error so store again
    #self.safeStore(dbkey, key, val)
    print('Unexpected error1:', sys.exc_info()[0])  
    raise Exception('.1')
   # Success
   # optional: return done
  except: # ....
   #self.safeStore(dbkey, key, val)
   print('Unexpected error2:', sys.exc_info()[0])
   raise Exception('.2')
 def getKey(self, key, val=None):
  """Get the db key for key from the set.
     If the key is not in the set, it is added to the set.
     The value associated with key is updated unless val is None.
     The key that is used to identify the key in the db
     is returned.
  """
  #print('crusherdict.py CrusherDict.getKey()')
  try:
   f=self.safeFetch(indexName(self.name,key))
   dbkey=entryName(self.name,f)
   if(val!=None):
    self.safeStore(dbkey, (key,val))
    #self.db.store(dbkey, (key,val))
   return dbkey
  except KeyError:
   try:
    n=self.safeFetch(countName(self.name))
    #n=self.db.fetch(countName(self.name))
   except KeyError:
    n=0
   print('count name='+str(n))
   dbkey=entryName(self.name,n)
   print('s1')
   self.safeStore(dbkey, (key,val))
   print('s2')
   self.safeStore(indexName(self.name,key), n)
   print('s3')
   self.safeStore(countName(self.name),n+1)
   #self.db.store(dbkey, (key,val))
   #self.db.store(indexName(self.name,key), n)
   #self.db.store(countName(self.name),n+1)
   return dbkey
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

