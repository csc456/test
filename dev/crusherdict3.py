#!/usr/bin/env python3
import sys
from vprint import vprint
import ast
# Testing
from time import sleep

def fletcher32(string):
 """Create a fletcher32 checksum and return it as 4 8bit characters"""
 a = list(map(ord, string))
 b = [sum(a[:i])%65535 for i in range(len(a)+1)]
 return chr((sum(b) >> 8) & 255) + chr((sum(b)) & 255) + chr((max(b) >> 8) & 255) + chr((max(b)) & 255)

def indexName(dict, key):
 vprint(3,'crusherdict.py indexName()')
 vprint(3,'  dbkey=',str((dict,"__X__IndexName",key)))
 return (dict,"__X__IndexName",key)

def countName(dict):
 vprint(3,'crusherdict.py countName()')
 vprint(3,'  dbkey=',str((dict,"__N__CountName")))
 return (dict,"__N__CountName")

def entryName(dict, n):
 # Always make n an int
 n=int(n)
 vprint(3,'crusherdict.py entryName()')
 vprint(3,'  dbkey=',str((dict, "__E__EntryName", n)))
 return (dict, "__E__EntryName", n)

def statusName(dict):
 vprint(3,'crusherdict.py statusName()')
 vprint(3,'  dbkey=',str((dict, "__S__StatusName")))
 return (dict, "__S__StatusName")

class CrusherDict:
 def __init__(self, db, name):
  """Create a set named key in the database."""
  self.db=db
  self.name=name
 def __len__(self):
  vprint(2,'Loading .__len__() for ',self.name,' ... ')
  try:
   f=self.safeFetch(countName(self.name))
   if str(f)!=str(int(f)): # Recurse
    vprint(2,'  .__len__()::(Recurse), Seeing: ',f)
    return self.__len__() # Try again...
   else:
    vprint(2,'  .__len__()::return',int(f))
    return int(f)
  except KeyError:
   vprint(2,'  .__len__()::return 0')
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
 def safeFetch(self, key, storing=False):
  '''Try a number of fetches with voting.
     Default is read attempt. On Store increase required successRate. On fetch decrease required?
     If coming from a read then require a lower successRate?
  '''
  vprint(2,'safeFetch::')
  vprint(2,'  safeFetch::key:',str(key))
  key=str(key)
  # Some vars
  rslt_ke=0 #keyerror
  rslt_ck=0 #checksum
  rslt_nm=0 #integer must contain key
  rslt_er=0
  rslt_gd=0
  rslt_good={}
  rslt_good_num={}
  rslt_num=0
  rslt_best=None
  r=200  # Num entries
  readMultiplier=10 # Store100; Then  Read100*RecurseRead40=Read4000; # Works well: w=60,r=200*60
  readAmount=r*readMultiplier    # Eg twenty time the number of reads as writes. Bc writes corrupt db but reads probably do not.
  successRate=0.02*readAmount	# Num entries which must match in order to assume it is not a KeyError.
				# If a KeyError occurs 500 out of 2000 and s=5% then a key must be fetched
				# correctly at least 0.05*2000 or 20 times. 
  if storing is True:
   successRate=0.02*readAmount
  found=False
  forceNum=False
  forceStr=False
  if 'CountName' in str(key) or 'IndexName' in str(key): #Marked
   forceNum=True
  else:
   forceStr=True
  fld=fletcher32(key)
  tmpkey=key+fld
  # Loop
  for i in range(readAmount):
   try:
    tmpk=tmpkey+'_'+str((i//readMultiplier)*1000)+'_'
    k=self.db.fetch(tmpk)
    if k[-4:] != fletcher32(k[:-4]):
     raise AttributeError # BAD, no cs
    # Must have key in val
    if str(fld)*4 not in k:
     raise LookupError #BAD, no indexof
    # Replace checksum ... k=k[:-8]
    k=k[:-20]
    if k.isdigit() and forceStr:
     raise LookupError
    elif not k.isdigit() and forceNum:
     raise LookupError
   except KeyError:
    rslt_ke+=1
    if rslt_ke>rslt_num:
     rslt_best='ke'
     rslt_num=rslt_ke
    continue
   except AttributeError:
    # Bad Checksum!
    rslt_ck+=1
    continue
   except LookupError:
    # Bad Integer! (Key does not match Key-Value pair.)
    rslt_nm+=1
    continue
   except: #Other
    rslt_er+=1
    if rslt_er>rslt_num:
     rslt_best='er'
     rslt_num=rslt_er
    continue
   try: #Success
    rslt_gd+=1
    rslt_good_num[k]+=1
   except:
    rslt_good_num[k]=1
   if rslt_good_num[k]>successRate:
    found=True
  # Print the results here in v3...
  vprint(3,'  safeFetch::key  error :',rslt_ke)
  vprint(3,'  safeFetch::chksm error:',rslt_ck)
  vprint(3,'  safeFetch::int   error:',rslt_nm)
  vprint(3,'  safeFetch::anon  error:',rslt_er)
  vprint(3,'  safeFetch::good  key  :',rslt_gd)
  # Was it found (goes above threshold) ... ?
  if found is True:
   #Loop. Could also sort dict by value desc.
   best=0
   rb=None
   for keyx, valx in rslt_good_num.items():
    if valx>best:
     best=valx
     rb=keyx # Element
     vprint(2,'  safeFetch:: new best value is ({}:{}%):'.format(valx,round(100*valx/readAmount,2)), rb)
   vprint(2,'  safeFetch:: final value is ', rb)
   return str(rb)
  raise KeyError
 def safeStore(self, dbkey, key):
  '''Store each dbkey as eg dbkey + __[1-20]__
  '''
  vprint(2,'safeStore::')
  vprint(2,'  safeStore::dbkey='+str(dbkey))
  vprint(2,'  safeStore::key='+str(key))
  # Put keys and values in with a marker
  # when they are beneath a threshold length.
  # And an int, eg 0-9.
  r=200
  dbkey=str(dbkey)
  key=str(key)
  fld=fletcher32(dbkey)
  tmpkey=dbkey+fld
  tmpval=key+fld+fld+fld+fld # Adding four straight...
  tmpval+=fletcher32(tmpval) # Add cs(val) to val
  # Loop store
  for i in range(r):
   self.db.store(tmpkey+'_'+str(i*1000)+'_', tmpval)
  # Now it is in there or else try again...
  try:
   n=self.safeFetch(dbkey, True)
   # Matches?
   if n != key:
    vprint(2,'  safeStore::Recurse(1)')
    vprint(1,'  safeStore::[Looking for ',key,' and seeing ',n,']')
    self.safeStore(dbkey, key)
  except: #KeyError
    vprint(2,'  safeStore::Recurse(2)')
    self.safeStore(dbkey, key)
 def getKey(self, key, val=None):
  """**NOT USED**
     Get the db key for key from the set.
     If the key is not in the set, it is added to the set.
     The value associated with key is updated unless val is None.
     The key that is used to identify the key in the db
     is returned.
  """
  vprint(2,'crusherdict.py CrusherDict.getKey()')
  try: # If db key exists... Then do not update the db...
   f=self.safeFetch(indexName(self.name,key))
   dbkey=entryName(self.name,f)
   if(val!=None):
    self.safeStore(dbkey, (key,val))
   return dbkey
  except KeyError:
   try:
    n=self.safeFetch(countName(self.name))
    if str(n)!=str(int(n)):
     # Hm try again?
     return self.getKey(key, val)
    n=int(n)
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

     Example:
     key: ['Office of Computer Science Research Grants', 'Zachary Edwards'] 
     val: VOTER|wgpJsirh 
  """
  vprint(2,'crusherdict.py .inc()')
  vprint(2,'  .inc()::key:',key)
  vprint(2,'  .inc()::val:',val)
  try:
   try:
    f=self.safeFetch(indexName(self.name,key))
    dbkey=entryName(self.name, f)
    #  v is one of:
    #   BROKEN:  fetch(dbkey):(('Senator', 'Harry Weasley'), None)
    #   BROKEN:  fetch(dbkey):16
    #   BROKEN:  fetch(dbkey):(('T_____________________________________', '__E__EntryName', 3), (('Secretary of the Vote', 'Charles Lindbergh'), 1, 'VOTER|0THR000U040078B00K632EVIJF0X0Z0YO0DC05P0Q00M09N00AL0W01G0S00'))
    #   WORKING: fetch(dbkey):(('Governor', 'Jack'), 1, 'VOTER|9K0Q000')
    v=self.safeFetch(dbkey)
    if v.isdigit(): # When a string contains only digits
     raise Exception('...')
    v=ast.literal_eval(v)
    if len(v) != 3: # tuple len not three
     raise Exception('...')
    if v and v[1] and v[1] is None:
     raise Exception('...')
    if str(v[1])!=str(int(v[1])):
     raise Exception('...')
    self.safeStore(dbkey, (key,int(v[1])+1,val))
    return {
     'entry':dbkey,
     'index':indexName(self.name,key),
     'valEntry':(key,int(v[1])+1,val),
     'valIndex':f,
    }
   except KeyError:
    raise KeyError # Send up
   except:
    return self.inc(key,val) # Recurse
  except KeyError:
   try:
    n=self.safeFetch(countName(self.name))
    if not n.isdigit(): # If not a digit
     # Hm try again? Do not set to 0.
     return self.inc(key, val)
    else:
     n=int(n)
   except KeyError:
    n=0
   dbkey=entryName(self.name,n)
   self.safeStore(dbkey,(key,1,val))
   self.safeStore(indexName(self.name,key), n)
   self.safeStore(countName(self.name),n+1)
   return {
    'entry':dbkey,
    'index':indexName(self.name,key),
    'valEntry':(key,1,val),
    'valIndex':n,
   }

 def __iter__(self):
  vprint(2,'crusherdict.py __iter__()::')
  for i in range(self.__len__()):
   vprint(2,'  []iter::i:',i)
   try:
    n=self.safeFetch(entryName(self.name,i))
   except:
    n=None
   vprint(2,'  []iter::n:',i)
   yield n

if __name__=="__main__":
 import crusher
 import crusher3
 crusher.Cache=crusher3.Cache # Add function
 crusher.DataBase=crusher3.DataBase # Add function

 db=crusher.Broker("test_crusherdict")
 test2=CrusherDict(db, "dict_nameA")
 test3=CrusherDict(db, "dict_nameB")
 test4=CrusherDict(db, "dict_nameC")
  
 for i in range(0,1000):
  test2.safeStore('x','99999')
  vprint(0,test2.safeFetch('x'))
 try:
  for tup in test2:
   vprint(0,tup)
 except:
  pass
 db.exit()
