#!/usr/bin/env python3

""" Example code, showing how to build a voting system that meets the
    non-reliability requirements using the CrusherDict data structure.

    Author: Steven P. Crain

    This code is licensed under a Creative Commons attribution license.

    Ver 0.92, 11/11/2016: Added doc strings. Added roll-back logic (untested).
"""

import crusher
import crusherdict
import wrapper
crusher.Broker = wrapper.Broker
import os.path
import random
import re
import sys

"""The commands dictionary is a convenient way to map from a command string
   to a command function. Yes, this is technically keeping data between
   voters, but it could be trivially reconstructed, so it is not violating
   the spirit of the requirements.
"""
commands={}
"""Initialize the random number generator. Crusher does this also, but it
   is not wise to rely on library side-effects.
"""
random.seed()

def conf(db, context, log, fields):
    """Perform CONF command.
       This is supposed to adjust the configuration of the Crusher database.
    """
    """Configure the database."""
    db.configure(fields[1])
    """Copy the configuration command to the log."""
    log.write("{}\t{}\n".format(fields[0], fields[1]))
    """This is an OK time to exit, so we check if CTRL-C has been pressed."""
    return db.doExit
"""Register this function to run when the CONF command is received."""
commands["CONF"]=conf

def voter(db, context, log, fields):
    """Perform VOTER command.
       This starts a new voter, so we first discard any data we have locally
       from before.
    """
    context.clear()
    try:
        """Loop until we get a KeyError, which will indicate that we found a
           new voterid that hasn't been used before.
        """
        while True:
             """Generate a random voterid. There are 36^6 or about 2 billion
                distinct voterids, so it is very unlikely we will get
                conflicts very often, since we only have to support 70,000
                voters.
             """
             voterid="V"+"".join(random.sample("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",6))
             """Try to retrieve the number of votes for this voterid."""
             db.fetch(crusherdict.countName(voterid))
             """No KeyError? Guess this voterid is already used, so loop to
                try another one.
             """
    except KeyError:
        """Good!!! We don't have this voter yet."""
    """Store the voterid in the context."""
    context["id"]=voterid
    """Make an empty list to store the votes in the context."""
    context["votes"]=[]
    """We are in the middle of a voter, so it is a bad time to exit."""
    return False
"""Register this function to run when the VOTER command is received."""
commands["VOTER"]=voter

def vote(db, context, log, fields):
    """Perform VOTE command.
       This just records the vote in the context, to be put in the database
       if the votes are cast.
    """
    context["votes"].append(fields)
    """We are in the middle of a voter, so it is a bad time to exit."""
    return False
"""Register this function to run when the VOTE command is received."""
commands["VOTE"]=vote

def cast(db, context, log, fields):
    """Perform CAST command.
       This records the votes in the database, increments the tallies
       and issues a receipt.
    """
    """Get a CrusherDict for this voterid."""
    d=crusherdict.CrusherDict(db,context["id"])
    """Get the CrusherDict for the tallies."""
    t=crusherdict.CrusherDict(db,"T")
    """Currently the voter does not exist in the database at all."""
    d.status("UNCAST")
    """The voter just barely exists, having a status of UNCAST only."""
    for vote in context["votes"]:
        """Add an item with key (office, candidate) and no value to the
           voter dictlist.
        """
        d.getKey(vote[1:3])
    """The votes have been added to the voter, but not the tallies."""
    for vote in context["votes"]:
        """Find the item in the tallies with key (office, candidate) and
           increment it, passing the voterid as "when" the tally was last
           updated.
        """ 
        t.inc(vote[1:3],context["id"])
    """The votes have been tentatively tallied."""
    """Tentatively increment the number of voters, again using the voterid
       as "when" it was updated.
    """
    t.inc("voters",context["id"])
    """Number of voters has been tentatively incremented."""
    """Change the voter's status to cast."""
    d.status("CAST")
    """The votes have been tallied."""
    return inq(db, context, log, ("INQ",context["id"]))
"""Register this function to run when the VOTE command is received."""
commands["CAST"]=cast

def inq(db, context, log, fields):
    """Perform INQ command."""
    context.clear()
    log.write("VOTER\n")
    for tup in crusherdict.CrusherDict(db,fields[1]):
        tup = tuple([tup])
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

def clean(db):
    """Check the database for any votes that are not properly cast.
    """
    t=crusherdict.CrusherDict(db,"T")
    try:
        x = t.getKey("voters")
        print("t.getKey")
        voters = db.fetch(x)
        print("voters = x")
        voters=db.fetch(t.getKey("voters"))
        """Get the CrusherDict for the last voter."""
        v=crusherdict.CrusherDict(db,voters[2]) 
        """Check if the vote was cast."""
        if(v.status()!="CAST"):
            """Last vote was not cast, so roll-back."""
            for tup in v:
                tally=db.fetch(t.getKey(tup[0]))
                try:
                    if(tally[2]==voters[2]):
                        t.getKey(tup[0],tally[1]-1)
                except IndexError:
                    """The tally was previously rolled back, and so
                       does not need to be rolled back this time.
                    """
            t.getKey(tup[0],tally[1]-1)
    except IndexError:
        """The tally was previously rolled back, and so
           does not need to be rolled back this time.
        """
    except KeyError:
        """c'mon python"""
try:
    filename=sys.argv[1]
except:
    filename="easy.txt"

basename=os.path.splitext(os.path.basename(filename))[0]

db=crusher.Broker(basename)
#clean(db)
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
