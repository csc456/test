#!/usr/bin/env python3

import crusher
import crusher3
crusher.Cache=crusher3.Cache # Add function
import crusherdict3
import os.path
import random
import re
import sys
import threading

commands={}
random.seed()

def conf(dbs, context, log, fields):
 """Perform CONF command."""
 # vote on doExit
 for i in dbs:
  i.configure(fields[1])
 return dbsdoexit(dbs)
commands["CONF"]=conf

def dbsdoexit(dbs):
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
 try:
  while True:
   amount=10 #6
   voterid="VOTER|"+"".join(random.sample("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",amount))
   c=crusherdict3.countName(voterid)
   #print('fetch:'+str(c))
   for i in dbs: # Fetch in N databases
    i.fetch(c)
 except KeyError:
  """Good: we don't have this voter yet."""
 except:
  raise Exception('...')
 return voterid

def voter(dbs, context, log, fields):
 """Perform VOTER command."""
 context.clear()
 context["id"]=newVoterId(dbs)
 context["votes"]=[]
 return False
commands["VOTER"]=voter

def vote(dbs, context, log, fields):
 """Perform VOTE command."""
 context["votes"].append(fields)
 return False
commands["VOTE"]=vote

#threadFailed=False
def threadVote(i,context,fields,stop_event,numberRecursions=0):
 '''Debug: numberRecursions
 '''
 d=crusherdict3.CrusherDict(i,context["id"])
 t=crusherdict3.CrusherDict(i,"___T___")
 d.status("UNCAST")
 checkvl=[] # array to match against
 for vote in context["votes"]:
  #d.getKey('abcdefg0123457'*numberRecursions) #random noise
  d.getKey(vote[1:3])
  checkvl.append("VOTE\t{}\t{}\n".format(vote[1],vote[2]))
 if matchesVoteLog(i,checkvl,context['id']) is False:
  #threadFailed=True
  #print('  threadVote::match fails!')
  #return
  numberRecursions+=1
  return threadVote(i,context,fields,stop_event,numberRecursions) # Recursive...
  """The votes have been added to the voter, but not the tallies."""
 for vote in context["votes"]:
  #print('t.Increment:'+str(vote[1:3]))
  t.inc(vote[1:3],context["id"])
 """The votes have been tentatively tallied."""
 t.inc("voters",context["id"])
 """Number of voters has been tentatively incremented."""
 d.status("CAST")
 """The votes have been tallied."""
 return

def cast(dbs, context, log, fields):
 """Perform CAST command."""
 if len(context['votes']) == 0:
  return
 t_stop=threading.Event()
 threads=[]
 for i in dbs:
  #print('  cast::start thread')
  n = threading.Thread(target=threadVote, args=(i,context,fields,t_stop,))
  n.start()
  threads.append(n)
 # Join all...
 for n in threads:
  n.join()
 #Made it
 #return
 return inq(dbs, context, log, ("INQ",context["id"]))
commands["CAST"]=cast

def matchesVoteLog(db,checkvl,vid):
 # Check that successful write before continuing in... 
 # Needs to match eg:
 #  VOTE	President	Donald Trump
 #  VOTE	Governor	Mickey Mouse
 #  VOTE	Lt. Governor	Melinda Gates
 print('  mvl:db',db)
 print('  mvl:vid',vid)
 c = crusherdict3.CrusherDict(db,vid) #open db-X with vid-Y
 x = pre_check_inq(c)
 if x is False:# or x != checkvl:
  print('  mvl:Fails checka')
  print('  Looking for:')
  print('\n'.join(str(x) for x in checkvl))
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
      print('\n'.join(str(x) for x in checkvl))
      print('  seeing:')
      print(x)
      return False
 # Success
 return True

def pre_check_inq(c):
 tmp_log=''
 try:
  for tup in c:
   print('  pre_check_inq::',tup)
   if isinstance(tup, int) or tup is None:
    return False
   tmp_log += "VOTE\t{}\t{}\n".format(tup[0][0],tup[0][1])
 except:
  return False
 return tmp_log

def check_inq(c):
 tmp=''
 try:
  for tup in c:
   if isinstance(tup, int) or tup is None:
    return check_inq(c) # Try again. Recursive.
   tmp+="VOTE\t{}\t{}\n".format(tup[0][0],tup[0][1])
 except:
  return check_inq(c) # Try again. Recursive.
 return tmp

def inq(dbs, context, log, fields):
 """Perform INQ command."""
 #print('demo.py inq()')
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
 #return db.doExit
commands["INQ"]=inq

def report(dbs, log):
 """Perform final report."""
 print('demo.py report()')
 try:
  voters={}
  best=None
  curr=0
  for i in dbs:
   t=crusherdict3.CrusherDict(i,"___T___")
   x=i.fetch(t.getKey("voters"))[1]
   try:
    voters[x]+=1
   except:
    voters[x]=1
   if voters[x]>curr:
    curr=voters[x]
    best=x
  # Write best
  log.write("VOTERS\t{}\n".format(best))
 except:
  print('  report::except...')
 #TODO
 #for tup in t:
 # try:
 #  if tup[0]!="voters":
 #   log.write("TALLY\t{}\t{}\t{}\n".format(tup[0][0],tup[0][1],tup[1]))
 # except:
 #  print(' report::except...')

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

for line in cmd:
 if line[-1]=="\n":
  line=line[:-1]
 line=line.split("\t")
 print('demo.py: Try cmd:' + line[0])
 if commands[line[0]](dbs,context,log,line):
  break

try:
 cmd.close()
 log.close()
 results=open(basename+"-results.txt","w")
 report(dbs,results)
except:
 pass
try:
 results.close()
except:
 pass
try:
 for i in dbs:
  i.exit()
except:
 pass 
