#!/usr/bin/env python3
'''...
   Note: sys.exc_info()[0]
'''

import crusher
import crusher3
crusher.Cache=crusher3.Cache # Add function
crusher.DataBase=crusher3.DataBase # Add function
import crusherdict3
import os.path
import random
import re
import sys
import threading
import vprint
from vprint import vprint
import ast

commands={}
random.seed()

def conf(dbs, context, log, fields):
 """Perform CONF command."""
 plog.f.write('conf::')
 # vote on doExit
 for i in dbs:
  i.configure(fields[1])
 return dbsdoexit(dbs)
commands["CONF"]=conf

#from crusherdict.py
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

def dbsdoexit(dbs):
 plog.f.write('dbsdoexit::')
 de={}
 decmd=None
 best=0
 for i in dbs:
  x=i.doExit
  try:
   de[x]+=1
  except:
   de[x]=1
  if de[x]>best:
   best=de[x]
   decmd=x
 return decmd

def newVoterId(dbs):
 plog.f.write('newVoterId::')
 try:
  while True:
   amount=8 #6
   voterid="VOTER|"+"".join(random.sample("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyv~!@$%^&*()_+",amount))
   c=crusherdict3.countName(voterid)
   for i in dbs: # Fetch in N databases
    i.fetch(c)
 except KeyError:
  """Good: we don't have this voter yet."""
 except:
  raise Exception('...')
 return voterid

def voter(dbs, context, log, fields):
 """Perform VOTER command."""
 plog.f.write('voter::')
 context.clear()
 context["id"]=newVoterId(dbs)
 context["votes"]=[]
 return False
commands["VOTER"]=voter

def vote(dbs, context, log, fields):
 """Perform VOTE command."""
 plog.f.write('vote::')
 context["votes"].append(fields)
 return False
commands["VOTE"]=vote

#threadFailed=False
def threadVote(i,context,fields,stop_event,numberRecursions=0):
 '''Debug: numberRecursions
 '''
 plog.f.write('threadVote::'+str(context['id']))
 #context['id']=newVoterId(dbs) # Force new voter id ... interesting but useful ...? 
 d=crusherdict3.CrusherDict(i,context["id"])
 t=crusherdict3.CrusherDict(i,"___T___")
 d.status("UNCAST")
 checkvl=[] # array to match against
 # i
# for vote in context["votes"]:
 for j in range(len(context["votes"])):
  vote=context["votes"][j]
  key=vote[1:3] # Office,Cand
  d.safeStore(entryName(context["id"], j),   (key, None))
  d.safeStore(indexName(context["id"], key), j)
  d.safeStore(countName(context["id"]),      j+1)
  #d.getKey(vote[1:3])
  checkvl.append("VOTE\t{}\t{}\n".format(vote[1],vote[2])) # office, cand
 # Save to file debug....
  #i.db.save()
 if matchesVoteLog(i,checkvl,context['id']) is False:
  numberRecursions+=1
  d.status("UNCAST")
  return threadVote(i,context,fields,stop_event,numberRecursions) # Recursive...
  """The votes have been added to the voter, but not the tallies."""
 for vote in context["votes"]:
  t.inc(vote[1:3],context["id"])
 """The votes have been tentatively tallied."""
 t.inc("voters",context["id"])
 """Number of voters has been tentatively incremented."""
 d.status("CAST")
 """The votes have been tallied."""
 return

def cast(dbs, context, log, fields):
 """Perform CAST command."""
 plog.f.write('cast::')
 if len(context['votes']) == 0:
  return
 t_stop=threading.Event()
 threads=[]
 for i in dbs:
  n = threading.Thread(target=threadVote, args=(i,context,fields,t_stop,))
  n.start()
  threads.append(n)
 # Join all...
 for n in threads:
  n.join()
 #Made it
 return inq(dbs, context, log, ("INQ",context["id"]))
commands["CAST"]=cast

def matchesVoteLog(db,checkvl,vid):
 # Check that successful write before continuing in... 
 # Needs to match eg:
 #  VOTE	President	Donald Trump
 #  VOTE	Governor	Mickey Mouse
 #  VOTE	Lt. Governor	Melinda Gates
 c = crusherdict3.CrusherDict(db,vid) #open db-X with vid-Y
 x = pre_check_inq(c)
 if x is False:# or x != checkvl:
  print('  mvl:Fails checka')
  print('  Looking for:')
  print(''.join(str(x) for x in checkvl))
  print('  Seeing:')
  print(x)
  # Let's try changing to a new voter id
  # since this one has not been casted yet.
  #context['id']=newVoterId()
  return False
 else:
  for i in checkvl:
   if i not in x: 
      print('  mvl:Fails checkb')
      print('  Looking for:')
      print(''.join(str(x) for x in checkvl))
      print('  Seeing:')
      print(x)
      return False
 # Success
 return True

def pre_check_inq(c):
 tmp_log=''
 try:
  for tup in c:
   try:
    tup=ast.literal_eval(tup)
    tmp_log += "VOTE\t{}\t{}\n".format(tup[0][0],tup[0][1])
   except:
    vprint(2,'  pre_check_inq exception::tmp_log=',str(tmp_log))
    return False
 except:
  return False
 return tmp_log

def check_inq(c):
 plog.f.write('check_inq::')
 tmp=''
 for tup in c:
  try:
   tup=ast.literal_eval(tup)
   tmp+="VOTE\t{}\t{}\n".format(tup[0][0],tup[0][1])
  except:
   vprint(2,'  check_inq::Exception:',sys.exc_info()[0])
   return check_inq(c)
 return tmp

def inq(dbs, context, log, fields):
 """Perform INQ command."""
 plog.f.write('inq::'+str(fields[1]))
 voter_id = fields[1]
 context.clear()
 log.write("VOTER\n")
 #vote on db logs
 logs={}
 best=None
 curr=0
 for i in dbs:
  c = crusherdict3.CrusherDict(i,voter_id)
  try:
   tmp=check_inq(c)
  except:
   raise Exception('  inq::tmp_log fails')
  try:
   logs[tmp]+=1
  except:
   logs[tmp]=0
  if logs[tmp]>curr:
   curr=logs[tmp]
   best=tmp
 # Write best
 log.write(tmp)   
 log.write("CAST\t{}\n".format(voter_id))
 return dbsdoexit(dbs)
commands["INQ"]=inq

def report(dbs, log):
 """Perform final report."""
 plog.f.write('report::')
 print('demo.py report()')
 # Get total voters
 voters={}
 best=None
 curr=0
 for i in dbs:
  t=crusherdict3.CrusherDict(i,"___T___")
  try:
   n=t.getKey("voters")
   x=t.safeFetch(n)
   # eval here
   x=ast.literal_eval(x)
   x=x[1]
  except:
   continue
  try:
   voters[x]+=1
  except:
   voters[x]=1
  if voters[x]>curr:
   curr=voters[x]
   best=x
 # Best
 head="VOTERS\t{}\n".format(best)
 log.write(head) 

 # Get tallies  
 try:
  voters={}
  best=None
  curr=0
  for i in dbs:
   t=crusherdict3.CrusherDict(i,"___T___")
   tmp=''
   try:
    for tup in t:
     tup=ast.literal_eval(tup)
     if tup[0]!="voters":
      tmp+="TALLY\t{}\t{}\t{}\n".format(tup[0][0],tup[0][1],tup[1])
   except:
    vprint(2,'  check_inq::Exception:',sys.exc_info()[0])
    print('  report::vote-log2 ...')
    continue # Skip db entirely ...
   # Add this result ...
   try:
    voters[tmp]+=1
   except:
    voters[tmp]=1
   if voters[tmp]>curr:
    curr=voters[tmp]
    best=tmp
  log.write(best)
 except:
  print('  report::vote-log3 ...')

try:
 filename=sys.argv[1]
except:
 filename="easy.txt"

basename=os.path.splitext(os.path.basename(filename))[0]

dbs=[]
for i in range(1):
 dbs.append(crusher.Broker(basename+'__db'+str(i)+'__'))

#db=crusher.Broker(basename)
log=open(basename+"-votelog.txt","w")
cmd=open(filename,"r")
context={}

# create a profiling log
# use a class to globalize it
class PlogClass:
 pass
plog=PlogClass()
plog.f=open(basename+"-plog.txt","w")

for line in cmd:
 if line[-1]=="\n":
  line=line[:-1]
 line=line.split("\t")
 print('demo.py: Try cmd:' + line[0])
 if commands[line[0]](dbs,context,log,line):
  break

cmd.close()
log.close()
results=open(basename+"-results.txt","w")
report(dbs,results)
plog.f.close()

results.close()
for i in dbs:
 i.exit()
