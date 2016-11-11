#!/usr/bin/env python3
'''Todo: Pre- and Post-database call integrity check.
'''
import sys
debug=0

def indexName(dict, key):
 global debug
 if debug:
  print('crusherdict.py indexName(): ' + str((dict,"X",key)))
 return (dict,"XXXXXXXXXXX",key)

def countName(dict):
 global debug
 if debug:
  print('crusherdict.py countName(): '+str((dict,"N")))
 return (dict,"NNNNNNNNNNN")

def entryName(dict, n):
 global debug
 if debug:
  print('crusherdict.py entryName(): '+str((dict,"E",n)))
 return (dict, "EEEEEEEEEEE", n)

def statusName(dict):
 global debug
 if debug:
  print('crusherdict.py statusName(): '+str((dict, "S")))
  print('  dict:'+dict)
 return (dict, "SSSSSSSSSSS")

class CrusherDict:
 def __init__(self, db, name):
  """Create a set named key in the database."""
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
  """Get and optionally set the status of the set.
     
     Return: key
  """
  #print('crusherdict.py CrusherDict.status()')
  name=statusName(self.name)
  try:
   old=self.db.fetch(name)
  except: # needs this... hm
   old=None
  print('status name:key:' + str(key) + ':stat:' + str(stat)+':old:'+str(old)+':self.name:'+str(self.name))
#  except KeyError:
#   old=None
  if stat!=None:
   i=0
   while i<=100:
    print('store status name:'+str(stat))
    self.db.store(name,stat)
    i+=1
  return old
 def try_getKey(self, key, val=None):
  '''It looks like self.db.fetch(idx) fails with KeyError approximately
     1/100 or 1/200 or so...
  '''
  success_key={}
  best=None
  chk=0
  i=0
  while i<=10:
   try:
    idx=indexName(self.name,key)
    fetch=self.db.fetch(idx)
   except TypeError: # ?? Not sure why there is a type error but it happens occasionally...
    i+=1
    continue
   except KeyError:
    # The following is returned from 
    # crusher.py: return self.valDBIn.mangle(self.db.fetch(self.keyDB.mangle(key)))
    i+=1
    continue # skip
   except:
    raise Exception('DK1!Key')
   try:
    dbkey=entryName(self.name,fetch)
   except:
    raise Exception('DK3!')
   try:
    success_key[dbkey] += 1
   except:
    try:
     success_key[dbkey] = 1 # initialize
    except:
     pass
   try:
    if success_key[dbkey] > chk: # set best
     best=dbkey
   except: # Unexpected error
    pass
    #raise Exception('DK1!')    
   i+=1
   # Todo: Consider looping through failed keys are removing them
   #for key in success_key:
   # if key == best:
   #  print('key is'+str(key))
   # elif key != best:
   #  i=100
   #  try:
   #   print('try to remove key'+str(key))
   #   self.db.remove(key)
   #  except:
   #   pass
     #while i>0:
     # try:
     #  self.db.remove(key)
     # except:
     #  pass
     # i -= 1
  return best
 def test_db_store(self, dbkey, key, val):
  '''Fails occasionally with "Store error"
     ...need integrity check
  '''
  global debug
  if debug:
   print('Trying to store...')
  success=0
  while success<2000:
   try:
    self.db.store(dbkey, (key,val))
    success+=1
   except:
    #raise Exception('Store error')
    pass
  #raise Exception('test exception here') # Works
# def store_replicate(idx, n):
#  i=0
#  while i<20:
#   try:
#    self.db.store(idx, n)
#   except:
#    pass ##
 def newKey(self, key, val=None):
  print('Store new key:self.newKey:key=' + str(key)+',val='+str(val))
  try:
   cn = countName(self.name)
   print('New entry: Fetch:' + str(cn))
   n=self.db.fetch(cn)
  except KeyError:
   n=0
  except: # Other errors may be raised
   print('Unexpected error:', sys.exc_info()[0])
   self.newKey(key,val) # try again
   return
  dbkey=entryName(self.name,n)
  idx=indexName(self.name,key)
  cn=countName(self.name)
  for i in range(0,100):
   try:
    self.db.store(dbkey, (key,val))
   except:
    pass
  for i in range(0,100):
   try:
    self.db.store(idx, n)
   except:
    pass
  if isinstance(n, int): # Hm...?
   for i in range(0,100):
    try:
     self.db.store(cn, n+1)
    except:
     pass
  #raise Exception('x')
  return dbkey
 def getKey(self, key, val=None):
  """Get the db key for key from the set.
     If the key is not in the set, it is added to the set.
     The value associated with key is updated unless val is None.
     The key that is used to identify the key in the db
     is returned.
  """
  # Try storing N copies here
  # where N is probably 7.
  dbkey=self.try_getKey(key,val) # Tests 40x...
  if dbkey != None:
   if(val!=None):
    self.test_db_store(dbkey, key, val)
   return dbkey
  else:
   return self.newKey(key,val)
 def inc(self, key, val):
  """Increment the value for key from the set.
     If the key is not in the set, it is added to the set with value 1.
     The value is stored in the entry as an annotation.
     The key that is used to identify the key in the db
     is returned.
  """
  print('crusherdict.py CrusherDict.inc()')
  # Hm getKey?
  dbkey=self.getKey(key,val)
  #if dbkey != None:
  print(dbkey)
  if isinstance(dbkey[1], int): # increment if int...otherwise... er...
   newValue=dbkey[1]+1
   self.db.store(dbkey, (key,newValue,val))
  elif isinstance(dbkey[2], int):
   newValue=dbkey[2]+1
   self.db.store(dbkey, (key,newValue,val))
  return dbkey
 def __iter__(self):
  print('crusherdict.py CrusherDict.__iter__()')
  #try:
  for i in range(self.__len__()):
   yield self.db.fetch(entryName(self.name,i))
  #except:
  # print('skip except....')

if __name__=="__main__":
# import crusher
# import wrapper
# crusher.Broker = wrapper.Broker

 import crusher
 db=crusher.Broker("test_crusherdict")
 test=CrusherDict(db, "test3")
 
 for i in range(0,100):
  #try:
   #test.getKey("Hiddleston","name")
  test.getKey("Key","Value")
# print(test.inc("Gov-Muller","voter-809809"))
# print(test.inc("Gov-Muller","voter-8098091"))
# print(test.inc("Gov-Muller","voter-8098092"))
# print(test.inc("Gov-Muller","voter-8098093"))
# print(test.inc("Gov-Muller","voter-8098094"))
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
