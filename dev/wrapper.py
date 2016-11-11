#!/usr/bin/env python3

############
###wrapper.py
###by Brandon Dutko
###WARNING This whole thing is currently untested.  Expect all types of crashing.  Use at your own risk.
############

import crusher.Broker as Broken

############
###This may not work, I've never replaced a class from a module
###with a child class from a different module in a seperate script that imports
###both modules before
###
###in scripts that use this wrapper:
###import crusher
###import wrapper
###crusher.Broker = wrapper.Broker
############

#n represents the number of replicas that should be stored
#this can easily be hard coded if storing n is not allowed
n = 7

class Broker(Broken):
    def __init__(self, filename="demo.txt"):
        """Nothing changes for the initialization"""
        Broken.__init__(self, filename)
        
    def configure(self, s):
        """Nothing changes for the configuration"""
        Broken.configure(self, s)
        
    def interrupt(self, signal, frame):
        """Nothing changes for the interrupt"""
        Broken.interrupt(self, signal, frame)
        
    def fletcher32(self, string):
        a = map(ord, string)
        b = [sum(a[:i])%65535 for i in range(len(a)+1)]
        return (sum(b) << 16) | max(b)
        
    def store(self, key, val):
        """Make replicas of the key-val pair, add a checksum to val and store those,
        fetch/store each replica until the fetched value is the same as the stored
        value to check for validity in the cache (if it's invalid in the cache
        it's almost certainly invalid in the db)"""
        for i in range(n):
            again = True
            while(again):
                again = False
                newKey = (key + "-" + str(i))
                newVal = (val + "-" + str(self.fletcher32((key+val)))
                Broken.store(self, newKey, newVal)
                if(Broken.fetch(newKey) != newVal):
                    #Likely corrupted if we cant even get it back right from the cache
                    #Try again
                    again = True
        
    def fetch(self, key):
        """Fetch each replica and use voting to determine the propert
        value, if the checksum does not match the key value pair then
        fail safely, in the event of ties in the voting seperate the possibilies
        and check with the checksum to determine the most likely correct val.
        In the event that the checksum has a Tt in it assume the two letters 
        to possibly be \t or Tt.  In the event that there are more than 1
        candidates with their own correct checksums just pick one at random
        and then buy a lottery ticket."""
        values = []
        for i in range(0, n):
            values.append(Broken.fetch((key+"-"+str(n))))
        valLengths = []
        for value in values:
            valLengths.append(len(value))
        valLengths = self.voteInt(valLengths)
        for lengths in valLengths:
            valuesWSameLengthTemp = []
            #For each possible length (if more than one length won the vote)
            for value in values:
                if len(value) == lengths:
                    valuesWSameLengthTemp.append(value)
            possibleValues = self.voteStr(valuesWSameLengthTemp)
            #TODO
            
    def voteInt(listOfInts):
        """
        Votes on a list of ints and determines the ints with the
        most occurences.
        Returns a list of the ints that occured the most (because there
        can be ties)
        """
        intDict = {}
        for item in listOfInts:
            if item in intDict:
                intDict[item] += 1
            else:
                intDict[item] = 1
        weightDict = {}
        for key in intDict:
            if intDict[key] in weightDict:
                weightDict[intDict[key]].append(key)
            else:
                weightDict[intDict[key]] = [key]
        return weightDict[max(weightDict.keys(), key=int)]
        
        
    def voteStr(listOfStrings):
        """
        Votes bitwise on a list of strings of the same length and determines the most likely strings
        returns a list of strings that are created from the bits that occured
        the most (because there can be ties for each individual bit)
        This entire process could probably be made more efficient by replacing alot of the
        code with proper bit manipulation rather than turning the bits into a list of integers to
        work with.
        """
        finalStringsAsBits = []
        #finalStringsAsBits will be a list of lists of bits that represent
        #the voted upon string possibilities
        #ex: the string possibilites "i"/"I" would be represented as follows
        #[[0],[1],[1,0],[0],[1],[0],[0],[1]] because 01101001 is "i" and 01001001 is "I"
        
        #For each character (The strings all have the same number of characters)
        for i in range(len(listOfStrings[0])):
        
            #Get the binary representation of the characters
            binReps = []
            for item in listOfStrings:
                binReps.append(bin(ord(item)))
                
            #For each bit in the binary representations
            for j in range(len(binReps[0])):
                bitRep = []
                for binRep in binReps:
                    bitRep.append(int(binRep[j]))
                #We now have a list of bits represented either by a 0 or 1 integer
                #for the nth bit of the string to vote with
                finalStringsAsBits.append(voteInt(bitRep))
                
        #We now have a binary representation of the final string possibilities
        
        #TODO make all possible combinations of the bits and convert those combinations back
        #into strings to return in a list
            
                
        
        
    def remove(self, key):
        """Something might change here because this method scares me, but really
        there's no reason for it to even exist or ever be called"""
        #Currently this will not work unless it's called with the proper
        #key which will have a copy identifier on it that the caller
        #probably doesn't know
        return Broken.remove(self, key)
        
    def exit(self):
        """Nothing changes on exit"""
        Broken.exit
        
