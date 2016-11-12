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

def voter(db, context, log, fields):
 """Perform VOTER command."""
 context.clear()
 try:
  #i=0
  while True:
   #i+=1
   #voterid="V"+str(i)
   #db.fetch(crusherdict.countName(voterid))
   amount=60
   #amount=6
   voterid="VOTER|"+"".join(random.sample("0000000000000000000000000123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",amount))
   c=crusherdict.countName(voterid)
   print('fetch:'+str(c))
   db.fetch(c)
   db.fetch(c)
   db.fetch(c)
   db.fetch(c)
   db.fetch(c)
   db.fetch(c)
   db.fetch(c)
   db.fetch(c)
 # while True:
    #voterid="V"+"".join(random.sample("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",6))
    #db.fetch(crusherdict.countName(voterid))
 except KeyError:
  """Good: we don't have this voter yet."""
 except:
  raise Exception('...')
 context["id"]=voterid
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
 t=crusherdict.CrusherDict(db,"T_____________________________________")
 """Currently the voter does not exist in the database at all."""
 d.status("UNCAST")
 """The voter just barely exists, having a status of UNCAST only."""
 for vote in context["votes"]:
  print('d.Vote for:'+str(vote[1:3]))
  d.getKey(vote[1:3])

 """The votes have been added to the voter, but not the tallies."""
 for vote in context["votes"]:
  print('t.Increment:'+str(vote[1:3]))
  t.inc(vote[1:3],context["id"])
 """The votes have been tentatively tallied."""
 t.inc("voters",context["id"])
 """Number of voters has been tentatively incremented."""
 d.status("CAST")
 #raise Exception('x')
 return
 
 # len...
# if len(context['votes']) != d.__len__():
#  print('Casted votes mismatch!')
#  return inq(db, context, log, ("INQ",context["id"]))
  ##cast(db, context, log, fields)
  ##return
# try:
#  for tup in crusherdict.CrusherDict(db,context['id']):
#   print('Trying to log tup:' + str(tup))
#   log.write("VOTE\t{}\t{}\n".format(tup[0][0],tup[0][1]))
# except:
  # Failed to write vote properly for some reason!
  # Try again.
#  cast(db, context, log, fields)
#  print('Caught VOTER error:fields:'+str(fields))
  #print('Caught inq VOTER error:fields[1]:'+str(voter_id))
#  return
 """The votes have been tallied."""
 return inq(db, context, log, ("INQ",context["id"]))
 #except:
 # print('demo.py: Trying cast again!')
 # raise Exception()
  #cast(db, context, log, fields)
commands["CAST"]=cast

def inq(db, context, log, fields):
 """Perform INQ command."""
# print('INQ:...')
# return
 context.clear()
 log.write("VOTER\n")
 voter_id = fields[1]
 try:
  for tup in crusherdict.CrusherDict(db,voter_id):
   log.write("VOTE\t{}\t{}\n".format(tup[0][0],tup[0][1]))
 except:
  #for tup in crusherdict.CrusherDict(db,voter_id):
  # try:
  #  print(tup)
  # except:
  #  print('tup print err....')
  #print('Caught inq VOTER error:tup:'+str(tup))
  #print('Caught inq VOTER error:fields:'+str(fields))
  #print('Caught inq VOTER error:fields[1]:'+str(voter_id))
  #raise Exception('inq')
  pass
 log.write("CAST\t{}\n".format(voter_id))
 return db.doExit
commands["INQ"]=inq

def report(db, log):
 """Perform final report."""
 print('Report:'+str(voters))
 return
 t=crusherdict.CrusherDict(db,"T")
 voters=db.fetch(t.getKey("voters"))[1]
 log.write("VOTERS\t{}\n".format(voters))
 for tup in t:
  #print(tup)
  #print(t)
  try:
   if tup[0]!="voters":
    log.write("TALLY\t{}\t{}\t{}\n".format(tup[0][0],tup[0][1],tup[1]))
  except:
   print('demo.py: Report-Exception:--')

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
 #try:
 if commands[line[0]](db,context,log,line):
  break
 #except:
 # print('demo.py: except --')

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
