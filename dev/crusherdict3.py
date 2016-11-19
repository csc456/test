#!/usr/bin/env python3
import sys

debug=2
def vprint(str,level=0):
 '''0=Always show
    1=Sometimes show
    2=Rarely show
    3=Rarely Rarely show
 '''
 #print(' debug is:',debug)
 if level<=debug:
  print(str)

def indexName(dict, key):
 vprint('crusherdict.py indexName()',2)
 vprint('  dbkey='+str((dict,"__X__IndexName",key)),2)
 return (dict,"__X__IndexName",key)

def countName(dict):
 vprint('crusherdict.py countName()',2)
 vprint('  dbkey='+str((dict,"__N__CountName")),2)
 return (dict,"__N__CountName")

def entryName(dict, n):
 vprint('crusherdict.py entryName()',2)
 vprint('  dbkey='+str((dict, "__E__EntryName", n)),2)
 return (dict, "__E__EntryName", n)

def statusName(dict):
 vprint('crusherdict.py statusName()',2)
 vprint('  dbkey='+str((dict, "__S__StatusName")),2)
 return (dict, "__S__StatusName")

class CrusherDict:
 def __init__(self, db, name):
  """Create a set named key in the database."""
  #vprint('crusherdict.py CrusherDict.__init__()')
  self.db=db
  self.name=name
 def __len__(self):
  #vprint('crusherdict.py .__len__()')
  try:
   f=self.safeFetch(countName(self.name))
   if not isinstance(f, int) or f is None: # Recursive...
    #vprint('  .__len__():bad f:'+str(f))
    return self.__len__() # Try again...
   else:
    return f
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
  vprint('safeFetch::',1)
  vprint('  safeFetch::key:'+str(key),1)
  rslt_ke=0
  rslt_er=0
  rslt_gd={}
  rslt_good={}
  rslt_num=0
  rslt_best=None
  n=None
  for i in range(20): #0-19
   try:
    n=self.db.fetch(str(key)+'__'+str(str(i)*10)+'__')
   except KeyError:
    rslt_ke+=1
    if rslt_ke>rslt_num:
     rslt_best='ke'
     rslt_num=rslt_ke
    continue
   except: #Other
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
   raise Exception('Another exception...')
  else:
   n=rslt_best
  vprint('  safeFetch:value is:',str(n),1)
  #...
  return n
 def safeStore(self, dbkey, key, val=None):
  '''Next:...
     Store each dbkey as dbkey+__[1-20]
 

     NOTE: Add a safeFecth lookup each time!
           Channel CONF may be using last key fetched as the key to store!
  '''
  vprint('safeStore::',1)
  vprint('  safeStore::dbkey='+str(dbkey),1)
  vprint('  safeStore::key='+str(key),1)
  vprint('  safeStore::val='+str(val),1)
  # See note above.
  # Extra CONF muddies channel!
  # So do fetch of dbkey to store next.
  #try:
  # self.safeFetch(dbkey)
  #except:
  # pass #Safely Ignore
  if val is None:
   key = key
  else:
   key = (key,val)
  for i in range(20): #0-9 Store each field as xyz__[0-39] (40 different entries). Then for each of these entries save to the database 3 times.
   try:
     k=str(dbkey)+'__'+str(str(i)*10)+'__'
     self.db.store(k, key)
   except:
    pass
 def getKey(self, key, val=None):
  """Get the db key for key from the set.
     If the key is not in the set, it is added to the set.
     The value associated with key is updated unless val is None.
     The key that is used to identify the key in the db
     is returned.
  """
  #vprint('crusherdict.py CrusherDict.getKey()')
  try:
   f=self.safeFetch(indexName(self.name,key))
   dbkey=entryName(self.name,f)
   if(val!=None):
    self.safeStore(dbkey, (key,val))
   return dbkey
  except KeyError:
   try:
    n=self.safeFetch(countName(self.name))
    if not isinstance(n, int):
     # Hm try again?
     return self.getKey(key, val)
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
  #vprint('crusherdict.py CrusherDict.inc()')
  #vprint('  key:'+str(key))
  #vprint('  val:'+str(val))
  try:
   f = self.safeFetch(indexName(self.name,key))
   #vprint('  indexName:'+str(f))
   dbkey=entryName(self.name,f)
   #vprint('  dbkey:'+str(dbkey))
   v=self.safeFetch(dbkey)
   #vprint('  fetch(dbkey):'+str(v))
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
    if not isinstance(n, int):
     ##vprint('  Looking for int but found not int!')
     #n=0
     #Hm try again?
     return self.inc(key, val)
   except KeyError:
    n=0
   dbkey=entryName(self.name,n)
   self.safeStore(dbkey,(key,1,val))
   self.safeStore(indexName(self.name,key), n)
   self.safeStore(countName(self.name),n+1)
   return dbkey
 def __iter__(self):
  #vprint('crusherdict.py CrusherDict.__iter__()')
  #vprint('  iter::name:',self.name)
  #vprint('  iter::db:',self.db)
  #vprint('  iter::range(self.__len__()):',range(self.__len__()))
  for i in range(self.__len__()):
   #vprint('  iter::i:',i)
   yield self.safeFetch(entryName(self.name,i))

if __name__=="__main__":
 import crusher
 try:
  db=crusher.Broker("test_crusherdict")
  test2=CrusherDict(db, "dict_nameA")
  test3=CrusherDict(db, "dict_nameB")
  test4=CrusherDict(db, "dict_nameC")
  
  for i in range(0,1000):
   try:
    test2.getKey("H","5555000")
    test3.getKey("H","6666000")
    test4.getKey("H","7777000")
   except:
    pass
  ##vprint(test.inc("Gov-Muller","voter-809809"))
  ##vprint(test.inc("Gov-Muller","voter-8098091"))
  ##vprint(test.inc("Gov-Muller","voter-8098092"))
  ##vprint(test.inc("Gov-Muller","voter-8098093"))
  ##vprint(test.inc("Gov-Muller","voter-8098094"))
  try:
   for tup in test2:
    try:
     vprint(tup)
    except:
     pass
  except:
   pass
  db.exit()
 except:
  #vprint('err')
  pass
