#!/usr/bin/env python3

############
###wrapper.py
###by Brandon Dutko
###WARNING This whole thing is currently untested.  Expect all types of crashing.  Use at your own risk.
############

from crusher import Broker as Broken

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


class InvalidChecksum(Exception):
    pass

class Broker(Broken):
    def __init__(self, filename="demo.txt"):
        """Nothing changes for the initialization"""
        return Broken.__init__(self, filename)
        
    def configure(self, s):
        """Nothing changes for the configuration"""
        return Broken.configure(self, s)
        
    def interrupt(self, signal, frame):
        """Nothing changes for the interrupt"""
        return Broken.interrupt(self, signal, frame)
        
    def fletcher32(self, string):
        """Create a fletcher32 checksum and return it as 4 8bit characters"""
        a = list(map(ord, string))
        b = [sum(a[:i])%65535 for i in range(len(a)+1)]
        return chr((sum(b) >> 8) & 255) + chr((sum(b)) & 255) + chr((max(b) >> 8) & 255) + chr((max(b)) & 255)
        
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
                newVal = (val + "-" + self.fletcher32((key+val)))
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
            for value in possibleValues:
                if(self.fletcher32(value[0:-4]) == value[-4:]):
                    return value[0:-4]
        raise InvalidChecksum("No matching value-checksum pair")
            
    def voteInt(self, listOfInts):
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
        
        
    def voteStr(self, listOfStrings):
        """
        Does bitwise voting on a list of strings to determine the strings
        that represent the bits with the most occurences.
        All strings in the list must be the same size
        Returns a list of the strings that represent the bits that occured
        the most (because there can be many ties among the bits)
        """
        #Convert the strings into bits and store them in a list
        #as a list of bits
        finalStringsAsBits = []
        #for each string
        for i in range(len(listOfStrings)):
            binReps = []
            #for each character
            for k in range(len(listOfStrings[i])):
                binReps.append(format(ord(listOfStrings[i][k]), '08b'))
            finalStringsAsBits.append(binReps)
        #finalStringsAsBits is now a list of lists of 8bit strings
        #that represent characters
        trueStringAsBits = []
        #for each 8bit rep of a character
        for i in range(len(finalStringsAsBits[0])):
            #for each bit of the character
            for k in range(8):
                bits = []
                #for each string
                for j in range(len(finalStringsAsBits)):
                    bits.append(int(finalStringsAsBits[j][i][k]))
                trueStringAsBits.append(self.voteInt(bits))
        #trueStringAsBits is a list of lists containing a 0, 1, or both
        #that represents all possible bits
        #ex: 'f' or 'g' would be [[0],[1],[1],[0],[0],[1],[1],[0,1]]
        allBitStrings = [[]]
        #allBitStrings is a list that contains lists of bits that represent
        #possible bitstrings created by all combinations of the bits
        #who tied or it simply contains 1 list of the only possible
        #string based on the bit voting

        #for each bit
        for i in range(len(trueStringAsBits)):
            #if there's only 1 winner add that to all of the bitstrings
            if(len(trueStringAsBits[i]) == 1):
                for j in range(len(allBitStrings)):
                    allBitStrings[j].append(trueStringAsBits[i][0])
            #if 0 and 1 tied then branch by copying the current
            #possibilities, adding 0 or 1 to the original possibilities
            #add the other to the copies and add the copies (that now
            #differ in the last bit) to the possibilities
            else:
                copy = []
                for j in range(len(allBitStrings)):
                    copy.append(list(allBitStrings[j]))
                for j in range(len(allBitStrings)):
                    allBitStrings[j].append(trueStringAsBits[i][0])
                for j in range(len(copy)):
                    copy[j].append(trueStringAsBits[i][1])
                for item in copy:
                    allBitStrings.append(item)
        #allBitStrings now contains all possible winners
        allStrings = []
        #Convert allBitStrings into normal strings
        #and store it in allStrings: a list of strings that
        #represent the possiblilities based on bitwise voting
        #aka the return value

        #for all possibilities
        for i in range(len(allBitStrings)):
            possibility = ""
            #for each character (every 8 entries because each entry is a bit)
            for j in range(len(allBitStrings[i])//8):
                characterAsBin = ""
                #for 8 bits
                for k in range(8):
                    characterAsBin += str(allBitStrings[i][(j*8)+k])
                possibility += chr(int(characterAsBin, 2))
            allStrings.append(possibility)
                
        return allStrings

    def remove(self, key):
        """Something might change here because this method scares me, but really
        there's no reason for it to even exist or ever be called"""
        #Currently this will not work unless it's called with the proper
        #key which will have a copy identifier on it that the caller
        #probably doesn't know
        return Broken.remove(self, key)
        
    def exit(self):
        """Nothing changes on exit"""
        return Broken.exit
        
