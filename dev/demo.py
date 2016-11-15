#!/usr/bin/env python3

import crusher
import crusherdict
import os.path
import random
import re
import sys

commands={}
random.seed()

def conf(db, context, log, fields):
 """Perform CONF command."""
 db.configure(fields[1])
 return db.doExit
commands["CONF"]=conf

def newVoterId():
 try:
  while True:
   amount=10
   #amount=6
   voterid="VOTER|"+"".join(random.sample("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",amount))
   c=crusherdict.countName(voterid)
   print('fetch:'+str(c))
   db.fetch(c)
   db.fetch(c)
   db.fetch(c)
 except KeyError:
  """Good: we don't have this voter yet."""
 except:
  raise Exception('...')
 return voterid

def voter(db, context, log, fields):
 """Perform VOTER command."""
 context.clear()
 #context["id"]=voterid
 context["id"]=newVoterId()
 context["votes"]=[]
 return False
commands["VOTER"]=voter

def vote(db, context, log, fields):
 """Perform VOTE command."""
 context["votes"].append(fields)
 return False
commands["VOTE"]=vote

def cast(db, context, log, fields):
 """Perform CAST command."""
 if len(context['votes']) == 0:
  print('Empty voter!')
  return
 print('Cast voter')
 print('voter id='+context['id'])
 #try:#??
 d=crusherdict.CrusherDict(db,context["id"])
 t=crusherdict.CrusherDict(db,"___T___")
 """Currently the voter does not exist in the database at all."""
 d.status("UNCAST")
 """The voter just barely exists, having a status of UNCAST only."""
 checkvl=[] # array to match against
 for vote in context["votes"]:
  print('d.Vote for:'+str(vote[1:3]))
  d.getKey(vote[1:3])
  checkvl.append("VOTE\t{}\t{}\n".format(vote[1],vote[2]))

 # Check that successful write before continuing in... 
 # Needs to match eg:
 #  VOTE	President	Donald Trump
 #  VOTE	Governor	Mickey Mouse
 #  VOTE	Lt. Governor	Melinda Gates
 c = crusherdict.CrusherDict(db,context['id'])
 x = sanity_check_inq(c)
 if x is False:# or x != checkvl:
  print('Fails sanity check1a')
  print('Looking for:')
  print('\n'.join(str(x) for x in checkvl))
  print('But seeing:')
  print(x)
  # Let's try changing to a new voter id
  # since this one has not been casted yet.
  #context['id']=newVoterId()
  return cast(db, context, log, fields)
 else:
  for i in checkvl:
   if i not in x: 
      print('Fails sanity check1b')
      print('Looking for:')
      print('\n'.join(str(x) for x in checkvl))
      print('But seeing:')
      print(x)
      return cast(db, context, log, fields)

 """The votes have been added to the voter, but not the tallies."""
 for vote in context["votes"]:
  print('t.Increment:'+str(vote[1:3]))
  t.inc(vote[1:3],context["id"])
 """The votes have been tentatively tallied."""
 t.inc("voters",context["id"])
 # Check again here?
  #c = crusherdict.CrusherDict(db,context['id'])
  #x = sanity_check_inq(c)
  #if x is False or x != checkvl:
  # print('Fails sanity check2')
  # return cast(db, context, log, fields) #...
 """Number of voters has been tentatively incremented."""
 d.status("CAST")
 """The votes have been tallied."""
 return inq(db, context, log, ("INQ",context["id"]))
commands["CAST"]=cast

def sanity_check_inq(c):
 tmp_log=''
 try:
  for tup in c:
   if isinstance(tup, int) or tup is None:
    return False
   tmp_log += "VOTE\t{}\t{}\n".format(tup[0][0],tup[0][1])
 except:
  return False
 return tmp_log
def check_inq(c):
 tmp_log=''
 try:
  for tup in c:
   if isinstance(tup, int) or tup is None:
    return check_inq(c) # Try again. Recursive.
   tmp_log += "VOTE\t{}\t{}\n".format(tup[0][0],tup[0][1])
 except:
  return check_inq(c) # Try again. Recursive.
 return tmp_log
def inq(db, context, log, fields):
 """Perform INQ command."""
 print('demo.py inq()')
 #print('  voter_id:'+str(fields[1]))
 voter_id = fields[1]
 context.clear()
 c = crusherdict.CrusherDict(db,voter_id)
 log.write("VOTER\n")
 try:
  tmp_log=check_inq(c)
  if tmp_log != False: # If success then write
   log.write(tmp_log)   
  else: # Otherwise another plan is necessary.
   pass
 except:
  raise Exception('inq')
 log.write("CAST\t{}\n".format(voter_id))
 return db.doExit
commands["INQ"]=inq

def report(db, log):
 """Perform final report."""
 print('demo.py report()')
 #return
 try:
  t=crusherdict.CrusherDict(db,"___T___")
  voters=db.fetch(t.getKey("voters"))[1]
  log.write("VOTERS\t{}\n".format(voters))
 except:
  print('  report::except...')
 for tup in t:
  try:
   if tup[0]!="voters":
    log.write("TALLY\t{}\t{}\t{}\n".format(tup[0][0],tup[0][1],tup[1]))
  except:
   print(' report::except...')

try:
 filename=sys.argv[1]
except:
 filename="easy.txt"

basename=os.path.splitext(os.path.basename(filename))[0]

db=crusher.Broker(basename)
cmd=open(filename,"r")
log=open(basename+"-votelog.txt","w")
context={}

for line in cmd:
 if line[-1]=="\n":
  line=line[:-1]
 line=line.split("\t")
 print('demo.py: Try cmd:' + line[0])
 if commands[line[0]](db,context,log,line):
  break

try:
 cmd.close()
 log.close()
 results=open(basename+"-results.txt","w")
 report(db,results)
except:
 pass
try:
 results.close()
except:
 pass
try:
 db.exit()
except:
 pass 
