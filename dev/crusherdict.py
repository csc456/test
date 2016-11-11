#!/usr/bin/env python3
import sys
debug=0

def indexName(dict, key):
 global debug
 if debug:
  print('crusherdict.py indexName(): ' + str((dict,"X",key)))
 return (dict,"X",key)

def countName(dict):
 global debug
 if debug:
  print('crusherdict.py countName(): '+str((dict,"N")))
 return (dict,"N")

def entryName(dict, n):
 global debug
 if debug:
  print('crusherdict.py entryName(): '+str((dict,"E",n)))
 return (dict, "E", n)

def statusName(dict):
 global debug
 if debug:
  print('crusherdict.py statusName(): '+str((dict, "S")))
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
 def try_getKey(self, key, val=None):
  '''It looks like self.db.fetch(idx) fails with KeyError approximately
     1/100 or 1/200 or so... Do voting here to ensure successful
     fetch. Assumption: It will be 99 correct keys versus 1 bad key.
  '''
  success_key={}
  best=None
  chk=0
  i=0
  while i<=40:
   try:
    idx=indexName(self.name,key)
    fetch=self.db.fetch(idx)
   except KeyError:
    # The following is returned from 
    # crusher.py: return self.valDBIn.mangle(self.db.fetch(self.keyDB.mangle(key)))
    i+=1
    continue # skip
   except:
    print('Fetch fails,key=' + str(key)) 
    print('Fetch fails,idx=' + str(idx)) 
    print('Unexpected error:', sys.exc_info()[0])
    raise Exception('DK1!')
   try:
    dbkey=entryName(self.name,fetch)
    try:
     success_key[dbkey] += 1
    except:
     success_key[dbkey] = 1 # initialize
    if success_key[dbkey] > chk: # set best
     best=dbkey
   except:
    print('Searching for:' + str(key)) 
    print('Unexpected error:', sys.exc_info()[0])
    raise Exception('DK2!')
   i+=1
   # Todo: Consider looping through failed keys are removing them
  return best
 def test_db_store(self, dbkey, key, val):
  '''This has not failed after many trials so far...
  '''
  global debug
  if debug:
   print('Trying to store...')
  success=0
  while success<100: 
   try:
    self.db.store(dbkey, (key,val))
    success+=1
   except:
    raise Exception('Store error')
  #raise Exception('test exception here') # Works
 def getKey(self, key, val=None):
  """Get the db key for key from the set.
     If the key is not in the set, it is added to the set.
     The value associated with key is updated unless val is None.
     The key that is used to identify the key in the db
     is returned.
  """
  #print('crusherdict.py CrusherDict.getKey()')
  # Try storing N copies here
  # where N is probably 7.
  dbkey=self.try_getKey(key,val) # Tests 40x...
  if dbkey != None:
   if(val!=None):
    self.test_db_store(dbkey, key, val)
   return dbkey
  else:
   try:
    cn = countName(self.name)
    print('New entry: Fetch:' + str(cn))
    n=self.db.fetch(cn)
   except KeyError:
    n=0
   dbkey=entryName(self.name,n)
   print('Store en:'+str(dbkey))
   self.db.store(dbkey, (key,val))
   self.db.store(indexName(self.name,key), n)
   self.db.store(countName(self.name),n+1)
   return dbkey

   
  #try:
   #dbkey=entryName(self.name,self.db.fetch(indexName(self.name,key)))
    #self.db.store(dbkey, (key,val))
  # return dbkey
  #except KeyError:
  # try:
  #  n=self.db.fetch(countName(self.name))
  # except KeyError:
  #  n=0
  # dbkey=entryName(self.name,n)
  # self.db.store(dbkey, (key,val))
  # self.db.store(indexName(self.name,key), n)
  # self.db.store(countName(self.name),n+1)
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
# import crusher
# import wrapper
# crusher.Broker = wrapper.Broker

 import crusher
# try:
 db=crusher.Broker("test_crusherdict")
 test=CrusherDict(db, "test3")
 
 for i in range(0,100):
  #try:
   #test.getKey("Hiddleston","name")
  test.getKey("H","n")
  #except:
  # pass
 #print(test.inc("Gov-Muller","voter-809809"))
 #print(test.inc("Gov-Muller","voter-8098091"))
 #print(test.inc("Gov-Muller","voter-8098092"))
 #print(test.inc("Gov-Muller","voter-8098093"))
 #print(test.inc("Gov-Muller","voter-8098094"))
 try:
  for tup in test:
   try:
    print(tup)
   except:
    pass
   #print('  tuple > '+str(tup))
 except:
  pass
 db.exit()
# except:
#  print('err')
#  pass
