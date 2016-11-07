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
    log.write("{}\t{}\n".format(fields[0], fields[1]))
    return db.doExit
commands["CONF"]=conf

def voter(db, context, log, fields):
    """Perform VOTER command."""
    context.clear()
    try:
        while True:
             voterid="V"+"".join(random.sample("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",6))
             db.fetch(crusherdict.countName(voterid))
    except KeyError:
        """Good: we don't have this voter yet."""
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
    d=crusherdict.CrusherDict(db,context["id"])
    t=crusherdict.CrusherDict(db,"T")
    """Currently the voter does not exist in the database at all."""
    d.status("UNCAST")
    """The voter just barely exists, having a status of UNCAST only."""
    for vote in context["votes"]:
        d.getKey(vote[1:3])
    """The votes have been added to the voter, but not the tallies."""
    for vote in context["votes"]:
        t.inc(vote[1:3],context["id"])
    """The votes have been tentatively tallied."""
    t.inc("voters",context["id"])
    """Number of voters has been tentatively incremented."""
    d.status("CAST")
    """The votes have been tallied."""
    return inq(db, context, log, ("INQ",context["id"]))
commands["CAST"]=cast

def inq(db, context, log, fields):
    """Perform INQ command."""
    context.clear()
    log.write("VOTER\n")
    for tup in crusherdict.CrusherDict(db,fields[1]):
        log.write("VOTE\t{}\t{}\n".format(tup[0][0],tup[0][1]))
    log.write("CAST\t{}\n".format(fields[1]))
    return db.doExit
commands["INQ"]=inq

def report(db, log):
    """Perform final report."""
    t=crusherdict.CrusherDict(db,"T")
    voters=db.fetch(t.getKey("voters"))[1]
    log.write("VOTERS\t{}\n".format(voters))
    for tup in t:
        if tup[0]!="voters":
            log.write("TALLY\t{}\t{}\t{}\n".format(tup[0][0],tup[0][1],tup[1]))

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
    if commands[line[0]](db,context,log,line):
        break

cmd.close()
log.close()
results=open(basename+"-results.txt","w")
report(db,results)
results.close()
db.exit()
