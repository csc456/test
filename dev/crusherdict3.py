#!/usr/bin/env python3
import sys
from vprint import vprint
#debug=2
#def vprint(str,level=0):
# '''0=Always show
#    1=Sometimes show
#    2=Rarely show
#    3=Rarely Rarely show
# '''
# #print(' debug is:',debug)
# if level<=debug:
#  print(str)
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
  vprint(2,'safeFetch::')
  vprint(2,'  safeFetch::key:',str(key))
  #if isinstance(key, tuple): # Convert lists to tuples... See doc above...
  # newt=()
  # for v in key:
  #  newval=v
  #  if isinstance(v, list): # Is list
  #   newval=tuple(v)
  #   newt=newt+(newval)
  #  else:
  #   newt=newt+(newval,)#append
  # key=newt
  # vprint(2,'  safeFetch::new key=',key)

  # vars
  rslt_ke=0#keyerror
  rslt_ck=0#checksum
  rslt_er=0
  rslt_gd=0
  rslt_good={}
  rslt_good_num={}
  rslt_num=0
  rslt_best=None
  r=2000  # Num entries
  readMultiplier=1               
  readAmount=r*readMultiplier     # Eg twenty time the number of reads as writes. Bc writes corrupt db but reads probably do not.
  successRateInt=0.2*readAmount	# Num entries which must match in order to assume it is not a KeyError.
				# If a KeyError occurs 500 out of 2000 and s=5% then a key must be fetched
				# correctly at least 0.05*2000 or 20 times. 
  successRateNotInt=0.05*readAmount
  found=False
  forceNum=False
  if '__N__CountName' in key or 'IndexName' in str(key): #Marked
   forceNum=True
  for i in range(readAmount): #0-...
   try:
    #dbkey=str(key)+'__'+str(str(i//readMultiplier)*4)+'__'
    k=self.db.fetch(key)
    if isinstance(k, tuple):
     # Loop tuple
     n=list(k)
     for k,v in enumerate(n):
      if isinstance(v, str):
       # good or bad str?
       n[k]=v[:-4] #add
       if v[-4:] != fletcher32(v[:-4]):
        raise AttributeError # BAD
      elif isinstance(v, tuple):
       n2=list(v)
       for k2,v2 in enumerate(n2):
        if isinstance(v2, str):
         # good or bad str?
         n2[k2]=v2[:-4] #modify
         if v2[-4:] != fletcher32(v2[:-4]):
          raise AttributeError # BAD
       v=tuple(n2)
       n[k]=v
     k=tuple(n)

    #k=self.db.fetch(str(key)+'__'+str(str(i)*10)+'__')
    #if isinstance(k, tuple):
    # newtup=()
    # for j in k:
    #  if 'dbstoremarker' not in k:
    #   newtup=newtup+(k,)
    # k=newtup
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
   except: #Other
    rslt_er+=1
    if rslt_er>rslt_num:
     rslt_best='er'
     rslt_num=rslt_er
    continue
   if forceNum and not isinstance(k, int):
    continue
   if forceNum is False and isinstance(k, int):
    continue
   if isinstance(k, str) or isinstance(k, int):
    ix=k
    successRate=successRateInt
   else:
    ix=str(k)
    successRate=successRateNotInt
   # Is key=1 value=1 or key=0 value=0?
   try: #Success
    rslt_gd+=1
    rslt_good_num[ix]+=1
   except:
    rslt_good_num[ix]=1
    rslt_good[ix]=k # For later ...
   if rslt_good_num[ix] > successRate:
    found=True
  # Print the results here in v2...
  vprint(2,'  safeFetch::key  error :',rslt_ke)
  vprint(2,'  safeFetch::chksm error:',rslt_ck)
  vprint(2,'  safeFetch::anon  error:',rslt_er)
  vprint(2,'  safeFetch::good  key  :',rslt_gd)
  # Was it found (goes above threshold) ... ?
  if found is True:
   #Loop. Could also sort dict by value desc.
   best=0
   for key, value in rslt_good_num.items():
    dbval=rslt_good[key]
    if value>best:
     best=value
     rslt_best=dbval #rslt_good[key] # Set to element
     vprint(2,'  safeFetch:: new best value is ', rslt_best, "({}:{}%)".format(value,value/readAmount))
  # nn=98
  # if isinstance(rslt_best, int):
    #if rslt_best%nn==0:
  #  rslt_best=rslt_best//nn
   vprint(2,'  safeFetch:: final value is ', rslt_best)
   return rslt_best   
  # So, what are results of fetch voting?
  if rslt_best=='ke':
   raise KeyError
  elif rslt_best=='er' or rslt_best is None:
   raise KeyError # Assume it is roughly equivalent...
 def safeStore(self, dbkey, key, val=None):
  '''Next:...
     Store each dbkey as eg dbkey + __[1-20]__

     Note that pickle: It is changing data structures!
      (['Lt. Governor', 'Microsoft'], None)
      to
      (('Lt. Governor', 'Microsoft'), None) 
  '''
  vprint(2,'safeStore::')
  vprint(2,'  safeStore::dbkey='+str(dbkey))
  vprint(2,'  safeStore::key='+str(key))
  vprint(2,'  safeStore::val='+str(val))
  # Put keys and values in with a marker
  # when they are beneath a threshold length.
  # And an int, eg 0-9.
  #key=str(key) # cast to str bc hey why not ? ...
#  nn=98
  #if isinstance(dbkey, tuple): # Convert lists to tuples... See doc above...
  # newt=()
  # for v in dbkey:
  #  newval=v
  #  if isinstance(v, list): # Is list
  #   newval=tuple(v)
  #   newt=newt+(newval)
  #  else:
  #   newt=newt+(newval,)#append
  # dbkey=newt
  # vprint(2,'  safeStore::new dbkey=',dbkey)
  #if isinstance(key, tuple): # Convert lists to tuples... See doc above...
  # newt=()
  # for v in key:
  #  newval=v
  #  if isinstance(v, list): # Is list
  #   newval=tuple(v)
  #   newt=newt+(newval)
  #  else:
  #   newt=newt+(newval,)#append
  # key=newt
  # vprint(2,'  safeStore::new dbkey=',key)
  r=2000
  if val is not None:
 #  if isinstance(key, int):# and key<10:
 #   key=key*nn
 #  if isinstance(val, int):# and val<10:
 #   val=val*nn
   dbval=(key,val)
 # elif isinstance(key, int):# and key<10:
 #   key=key*nn
  else:
   dbval=key
  tmp_dbval=dbval
  if isinstance(dbval, tuple):
   # Loop tuple
   n=list(dbval)
   for k,v in enumerate(n):
    if isinstance(v, str):
     n[k]=v+fletcher32(v) #add
    elif isinstance(v, tuple):
     n2=list(v)
     for k2,v2 in enumerate(n2):
      if isinstance(v2, str):
       n2[k2]=v2+fletcher32(v2) #add
     v=tuple(n2)
     n[k]=v
   # Update dbval     
   dbval=tuple(n)
  # Loop store
  for i in range(r): #0-9 Store each field as xyz__[0-39] (40 different entries). Then for each of these entries save to the database 3 times.
   try:
     #k=str(dbkey)+'__'+str(str(i)*10)+'__'
     #k=str(dbkey)+'__'+str(str(i)*4)+'__'
     #self.db.store(dbkey, dbval+('dbstoreval:'+str(i),))
     self.db.store(dbkey, dbval)
     #n=dbval
     #if isinstance(dbval, tuple):
     # n=dbval+('dbstoremarker'+str(i),)
     #print('storing n ',n)
     #self.db.store(dbkey, n)
   except:
    pass
  # Now it is in there or else try again...
  try:
   n=self.safeFetch(dbkey)
   #n.pop() # remove marker
   #if isinstance(n, tuple):
   # newtup=()
   # for i in n:
   #  if 'dbstoremarker' not in i:
   #   newtup=newtup+(i,)
   # n=newtup
   # Does it match?
   if n != tmp_dbval:
    print('recurse1...')
    print('looking for ',tmp_dbval,' and seeing ',n)
    self.safeStore(dbkey, key, val)
  except: #KeyError
    print('recurse2...') 
    self.safeStore(dbkey, key, val)
  # ...
 def getKey(self, key, val=None):
  """Get the db key for key from the set.
     If the key is not in the set, it is added to the set.
     The value associated with key is updated unless val is None.
     The key that is used to identify the key in the db
     is returned.
  """
  #vprint('crusherdict.py CrusherDict.getKey()')
  key=tuple(key)
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
    #n=100
   dbkey=entryName(self.name,n)
   self.safeStore(dbkey, (key,val))
   self.safeStore(indexName(self.name,key), n)
   self.safeStore(countName(self.name),n+1) #1 now 100
   return dbkey
 def inc(self, key, val):
  """Increment the value for key from the set.
     If the key is not in the set, it is added to the set with value 1.
     The value is stored in the entry as an annotation.
     The key that is used to identify the key in the db
     is returned.
  """
  key=tuple(key)
  try:
   f = self.safeFetch(indexName(self.name,key))
   dbkey=entryName(self.name,f)
   v=self.safeFetch(dbkey)
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
   self.safeStore(dbkey, (key,v[1]+1,val)) #1 now 100
   return dbkey
  except KeyError:
   try:
    n=self.safeFetch(countName(self.name))
    if not isinstance(n, int):
     return self.inc(key, val) # Recursive
   except KeyError:
    n=0 #works on easy
    #n=100 #works with tiny?
   dbkey=entryName(self.name,n)
   self.safeStore(dbkey,(key,1,val)) # 1
   self.safeStore(indexName(self.name,key), n)
   self.safeStore(countName(self.name),n+1) #1 now 100
   return dbkey
 def __iter__(self):
  for i in range(self.__len__()):
   yield self.safeFetch(entryName(self.name,i))

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
#   try:
#  test2.getKey("H","5555000")
#  test3.getKey("H","6666000")
#  test4.getKey("H","7777000")
#   except:
#    pass
  ##vprint(test.inc("Gov-Muller","voter-809809"))
  ##vprint(test.inc("Gov-Muller","voter-8098091"))
  ##vprint(test.inc("Gov-Muller","voter-8098092"))
  ##vprint(test.inc("Gov-Muller","voter-8098093"))
  ##vprint(test.inc("Gov-Muller","voter-8098094"))
 try:
  for tup in test2:
#    try:
   vprint(0,tup)
#    except:
#     pass
 except:
  pass
 db.exit()
