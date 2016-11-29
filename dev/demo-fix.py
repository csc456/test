#!/usr/bin/env python3

""" 
    Group Members: Brandon Dutko, David Shumway, Quinn Jones,
                   Michele Parmelee, and Aaron Wilkins.

    This code is licensed under a Creative Commons attribution license.
"""

import crusher
import wrapper
crusher.Broker = wrapper.Broker
import os.path
import sys

DEBUG = True
PRINTDB = False
#Turns on/off debugging print statements

"""The commands dictionary is a convenient way to map from a command string
   to a command function. Yes, this is technically keeping data between
   voters, but it could be trivially reconstructed, so it is not violating
   the spirit of the requirements.
"""
commands={}

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
    if(DEBUG):
        print("VOTER::")
    """Perform VOTER command.
       This starts a new voter, so we first discard any data we have locally
       from before.
    """
    context.clear()
    try:
        """Get the last voter id and generate the next voterid based on that.
           Try to fetch that voterid if it's succesful we have a problem and
           need to iterate through the voterids from the current point until
           we get a key error.  If the last voter id generates a key error
           iterate from the beginning.
        """
        try:
            LVID = db.fetch("LVID")
        except KeyError:
            LVID = "0"
        try:
            VID = str(int(LVID)+1)
            db.fetch(VID)
            #VID in system already, we need to find one that isn't
            while True:
                VID = str(int(VID)+1)
                db.fetch(VID)
        except:
            #We got a VID that reportedly isn't in the system
            #Store id in context and make a list in context to store
            #the votes and 2 dicts in context to store id-name
            #relationships for offices and candidates
            context["id"]=VID
            context["votes"]=[]
            context["offices"]={}
            context["candidates"]={}
            return False
    except:
        """Do nothing"""
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
    if(DEBUG):
        print("CAST::")
    """Perform CAST command.
       This records the votes in the database, increments the tallies
       and issues a receipt.
    """
    VID = context["id"]
    if(len(context["votes"]) == 0):
        if(DEBUG):
            print("VOTED FOR NO ONE")
    for vote in context["votes"]:
        """Get the office id for current vote's office, do this the
           same way we got voterid earlier if it isn't already
           in the db except it's internal so it can be illegible 
           for compactness.
           voter dictlist. vote[1] = officename, vote[2] = candidatename
        """
        if(DEBUG):
            print("VOTED FOR", context["votes"])
        OID = ""
        CID = ""
        try:
            #Does it already exist?
            OID = db.fetch("ON"+str(vote[1]))
        except (KeyError, wrapper.InvalidChecksum):
            #It doesn't exist or it's broken, make one
            try:
                #Get the last office id and increment it
                LOID = db.fetch("LOID")

            except KeyError:
                #Last office id does not exist
                LOID = "0"

            except wrapper.InvalidChecksum:
                #There is a last office id but it's invalid
                LOID = "0"

            try:
                while True:
                    #Try to make sure we don't overwrite any existing 
                    #office id's
                    try:
                        db.fetch("O"+LOID)
                    except wrapper.InvalidChecksum:
                        """
                        We found a broken one :( too bad
                        There's nothing we can do to fix it so just keep
                        looking.
                        """
                    #We got one, increment it and try again
                    LOID = str(int(LOID)+1)
                    #TODO increment character wise (0-255 per char)
                    #Rather than with integers
            except KeyError:
                #We found an OID theoretically not in use, store its mapping
                #And store it as the LOID
                OID = "O"+LOID
                db.store("ON"+str(vote[1]), OID)
                db.store(OID, str(vote[1]))
                db.store("LOID", LOID)

            #Now do the same except with the candidate (which is paired with
            #the office.
        try:
            #Does it already exist?
            CID = "C"+str(db.fetch(str(OID)+"-CN-"+str(vote[2])))
        except:
            #It doesn't exist or it's invalid, make a new one
            try:
                #Get the last candidate id and increment it
                LCID = db.fetch("LCID")

            except KeyError:
                #Last candidate id does not exist
                LCID = "0"

            except wrapper.InvalidChecksum:
                #There is a last candidate id but it's invalid
                LCID = "0"

            try:
                while True:
                    #Try to make sure we don't overwrite any existing 
                    #candidate id's
                    try:
                        db.fetch(str(OID)+"C"+LCID)
                    except wrapper.InvalidChecksum:
                        """
                        We found a broken one :( too bad
                        There's nothing we can do to fix it so just keep
                        looking.
                        """
                    #We got one, increment it and try again
                    LCID = str(int(LCID)+1)
                    #TODO increment character wise (0-255 per char)
                    #Rather than with integers
            except KeyError:
                #We found a CID theoretically not in use, store its mapping
                TempCID = "-1"
                try:
                    TempCID = db.fetch("LCID")
                except:
                    """Do nothing"""
                if(int(TempCID) < int(LCID)):
                    db.store("LCID",LCID)
                CID = "C"+LCID
                db.store(str(OID)+"-CN-"+str(vote[2]),LCID)
                db.store(str(OID)+CID, str(vote[2])+"-"+str(0))

        context["offices"][str(vote[1])] = OID
        context["candidates"][str(vote[2])] = CID

    """We have the id-name mappings and voter id now, store the votes
    and update the tallies.  Also generate a string that lists the office
    ids the voter voted for.
    """
    officeIDs = ""
    for vote in context["votes"]:
        OID = str(context["offices"][str(vote[1])])
        officeIDs = officeIDs + OID + "-"
        CID = str(context["candidates"][str(vote[2])])
        try:
            #See if this is the first vote for this office-candidate pair
            CIDINF = str(db.fetch(OID+CID))
            #It's not
            #Split the tally from the name
            try:
                [CName, CTally] = str(CIDINF).rsplit("-",1)
            except ValueError:
                CName = str(CIDINF)
                CTally = str(0)
        except (KeyError, wrapper.InvalidChecksum):
            #It is the first vote or it's corrupted so start from 0
            CName = str(vote[2])
            CTally = 0
        #Store it with incremented tally
        #TODO increment tally by bit instead of as integers
        #(0-255) except for ord('-')
        CTally = str(int(CTally)+1)
        #The vote
        db.store(VID+OID, CID)
        #The tally
        db.store(OID+CID, CName+"-"+CTally)

    """
    Now store the voter id info for reciept requests
    """
    #[:-1] to strip the last "-"
    if(officeIDs != ""):
        db.store(VID, officeIDs[:-1])
    else:
        db.store(VID, "%")
    #Also store the LVID as this VID
    db.store("LVID", VID)
    if(DEBUG):
        print("ENDCAST::")
    
    return inq(db, context, log, ("INQ",context["id"]))
"""Register this function to run when the VOTE command is received."""
commands["CAST"]=cast

def inq(db, context, log, fields):
    if(DEBUG):
        print("INQ::")
    """Perform INQ command."""
    context.clear()
    log.write("VOTER\n")
    #Get voted upon offices
    VID = str(fields[1])
    try:
        OIDS = db.fetch(VID)
    except (KeyError, wrapper.InvalidChecksum):
        log.write("FAILED RETRIEVAL FOR" + VID)
        return db.doExit
    if(OIDS == "%"):
        #They cast but didn't vote
        log.write("CAST\n")
        return db.doExit
    OIDSList = OIDS.split("-")
    Votes = []
    for OID in OIDSList:
        votedFor = "FAILED"
        votedOffice = "FAILED"
        try:
            votedOffice = str(db.fetch(OID))
            CID = db.fetch(VID+OID)
            #Have to split off the tally
            votedFor = str(db.fetch(OID+CID)).rsplit("-")[0]
        except:
            """Do nothing"""
        log.write("VOTE\t{}\t{}\n".format(votedOffice, votedFor))
    log.write("CAST\n")
    return db.doExit
commands["INQ"]=inq

def report(db, log):
    if(DEBUG):
        print("REPORT::")
    """Perform final report."""
    #Last office id and last candidate id are critical if either fail
    #to be retrieved then we can only hope to hit all the tallies by
    #padding misses

    failed = False
    #Get last office id
    try:
        LOID = db.fetch("LOID")
    except:
        failed = True

    #Get last candidate id
    try:
        LCID = db.fetch("LCID")
    except:
        failed = True

    #Set current candidate id and office id and voter id
    CID = str(0)
    OID = str(0)
    VID = str(0)

    padding = 30
    failuresInARow = 0
    amountOfVoters = 0

    #The last voter id should tell us how many voters there were
    try:
        LVID = int(db.fetch("LVID"))
    except:
        LVID = -1

    failedCandidates = 0
    #Iterate through all combinations of OID-CID up to LOID-LCID
    if(not failed):
        for i in range(int(LOID)+1):
            OID = "O"+str(i)
            for j in range(int(LCID)+1):
                CID = "C"+str(j)
                try:
                    if(DEBUG):
                        print("CNAME,TALLY", db.fetch(OID+CID))
                    [CNAME, TALLY] = str(db.fetch(OID+CID)).rsplit("-")
                    ONAME = str(db.fetch(OID))
                    if(DEBUG):
                        """"""
                        print("ONAME", ONAME)
                        print("CNAME", CNAME)
                        print("TALLY", TALLY)
                    log.write("TALLY\t{}\t{}\t{}\n".format(ONAME, CNAME, TALLY))
                except:
                    """Failed for one reason or another, do nothing"""
    if(LVID >= 0):
        log.write("VOTERS\t"+str(LVID)+"\n")
    else:
        log.write("VOTERS\tERROR\n")

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
if(PRINTDB):
    try:
        print("::DB STORAGE::")
        for item in db.DEBUG_stored_in_db:
            print(str(item), ":", db.DEBUG_stored_in_db[item])
    except:
        print("db not in debug mode!")
results.close()
db.exit()
