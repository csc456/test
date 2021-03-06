#!/usr/bin/env python3
debug=0
import sys

def indexName(dict, key):
 global debug
 if debug:
  print('crusherdict.py indexName()')
  print('  dict:'+dict)
  print('  key:'+str(key))
 return (dict,"__X__IndexName",key)

def countName(dict):
 global debug
 if debug:
  print('crusherdict.py countName()')
  print('  dict:'+dict)
 return (dict,"__N__CountName")

def entryName(dict, n):
 global debug
 if debug:
  print('crusherdict.py entryName()')
  print('  dict:'+dict)
  print('  n:'+str(n))
 return (dict, "__E__EntryName", n)

def statusName(dict):
 global debug
 if debug:
  print('crusherdict.py statusName()')
  print('  dict:'+dict)
 return (dict, "__S__StatusName")

class CrusherDict:
 def __init__(self, db, name):
  """Create a set named key in the database."""
  print('crusherdict.py CrusherDict.__init__()')
  self.db=db
  self.name=name
 def __len__(self):
  print('crusherdict.py .__len__()')
  try:
   f=self.safeFetch(countName(self.name))
   if isinstance(f, str):
    tempn = int(f)
   if str(tempn) != str(f):
    return self.__len__()
   return int(f)
  except KeyError:
   return 0
 def __contains__(self,key):
  try:
   self.safeFetch(indexName(self.name,key))
   return True
  except KeyError:
   return False
 def status(self, key, stat=None):
  """Get and optionally set the status of the set."""
  name=statusName(self.name)
  try:
   old=self.safeFetch(name)
  except KeyError:
   old=None
  if stat!=None:
   self.safeStore(name,stat)
  return old
 def safeFetch(self, key):
  '''Try a number of fetches. Voting on which is best.
     Probably bitwise.
  '''
  print('safeFetch::')
  print('  safeFetch::key:'+str(key))
  rslt_ke=0
  rslt_er=0
  rslt_gd={}
  rslt_good={}
  rslt_num=0
  rslt_best=None
  n=None
  for i in range(1): #1
   try:
    n=self.db.fetch(str(key))
   except KeyError:
    rslt_ke+=1
    if rslt_ke>rslt_num:
     rslt_best='ke'
     rslt_num=rslt_ke
    continue
   except: #Other
    print("!!!!!!!!!!", sys.exc_info()[0])
    rslt_er+=1
    if rslt_er>rslt_num:
     rslt_best='er'
     rslt_num=rslt_er
    continue
   try: #Success
    rslt_gd[str(n)]+=1
   except:
    rslt_gd[str(n)]=1
   if rslt_gd[str(n)] > rslt_num:
    rslt_best=n ####rslt_good[str(n)] # Set to element
    rslt_num=rslt_gd[str(n)]               # Set to num
  # So, what are results of fetch voting?
  if rslt_best=='ke':
   raise KeyError
  elif rslt_best=='er' or rslt_best is None:
   print("rslt_best =", rslt_best)
   raise Exception('Another exception...')
  else:
   n=rslt_best
  #...
  return n
 def safeStore(self, dbkey, key, val=None):
  '''Next:...
     Store each dbkey as dbkey+__[1-20]
  '''
  print('safeStore::')
  print('  safeStore::dbkey='+str(dbkey))
  print('  safeStore::key='+str(key))
  print('  safeStore::val='+str(val))
  if val is None:
   key = key
  else:
   key = (key,val)
  print('  store:', end='')
  for i in range(1): #0-9 Store each field as xyz__[0-39] (40 different entries). Then for each of these entries save to the database 3 times.
   print(str(i)+',', end='')
   try:
     k=str(dbkey)
     self.db.store(k, key)
   except:
    print("COULDN'T STORE")
    pass
  print('-')
 def getKey(self, key, val=None):
  """Get the db key for key from the set.
     If the key is not in the set, it is added to the set.
     The value associated with key is updated unless val is None.
     The key that is used to identify the key in the db
     is returned.
  """
  print('crusherdict.py CrusherDict.getKey()')
  try:
   f=self.safeFetch(indexName(self.name,key))
   dbkey=entryName(self.name,f)
   if(val!=None):
    self.safeStore(dbkey, (key,val))
   return dbkey
  except KeyError:
   try:
    n=self.safeFetch(countName(self.name))
    if isinstance(n, str):
     tempn = int(n)
    if str(tempn) != str(n):
     return self.getKey(key, val)
    n = int(n)
   except KeyError:
    n=0
   dbkey=entryName(self.name,n)
   self.safeStore(dbkey, (key,val))
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
  print('  val:'+str(val))
  try:
   f = self.safeFetch(indexName(self.name,key))
   print('  indexName:'+str(f))
   dbkey=entryName(self.name,f)
   print('  dbkey:'+str(dbkey))
   v=self.safeFetch(dbkey)
   print('  fetch(dbkey):'+str(v))
   # v is one of:
   #   BROKEN:  fetch(dbkey):(('Senator', 'Harry Weasley'), None)
   #   BROKEN:  fetch(dbkey):16
   #   BROKEN:  fetch(dbkey):(('T_____________________________________', '__E__EntryName', 3), (('Secretary of the Vote', 'Charles Lindbergh'), 1, 'VOTER|0THR000U040078B00K632EVIJF0X0Z0YO0DC05P0Q00M09N00AL0W01G0S00'))
   #   WORKING: fetch(dbkey):(('Governor', 'Jack'), 1, 'VOTER|9K0Q0000DG0LZH70V000W0F0R006BP28M0500ES00XYO30C40I0JNU0A100T')
   if isinstance(v, int): # is int
    return self.inc(key,val) # Recursive...
   if len(v) != 3: # tuple len not three
    return self.inc(key,val) # Recursive...
   # If v is None
   # Try again... eg...
   if v and v[1] and v[1] is None:
    return self.inc(key,val) # Recursive...
   self.safeStore(dbkey, (key,v[1]+1,val))
   return dbkey
  except KeyError:
   try:
    n=self.safeFetch(countName(self.name))
    if isinstance(n, str):
     tempn = int(n)
    if str(tempn) != str(n):
     return self.inc(key, val)
    n = int(n)
   except KeyError:
    n=0
   dbkey=entryName(self.name,n)
   self.safeStore(dbkey,(key,1,val))
   self.safeStore(indexName(self.name,key), n)
   self.safeStore(countName(self.name),n+1)
   return dbkey
 def __iter__(self):
  print('crusherdict.py CrusherDict.__iter__()')
  for i in range(self.__len__()):
   yield self.safeFetch(entryName(self.name,i))

if __name__=="__main__":
 import crusher
 import wrapper
 crusher.Broker = wrapper.Broker
 try:
  db=crusher.Broker("test_crusherdict")
  test2=CrusherDict(db, "dict_nameA")
  #test3=CrusherDict(db, "dict_nameB")
  #test4=CrusherDict(db, "dict_nameC")
  
  for i in range(0,1):
   try:
    test2.getKey("H","5555000")
    #test3.getKey("H","6666000")
    #test4.getKey("H","7777000")
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
  except:
   pass
  db.exit()
 except:
  print('err')
  pass
