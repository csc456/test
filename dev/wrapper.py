#!/usr/bin/env python3

############
###wrapper.py
###Team Members: Brandon Dutko, David Shumway, Quinn Jones, Michele Parmalee
###and Aaron Wilkins
############

from crusher import Broker as Broken
import sys

DEBUG = True
#Turns on/off print statements for debugging

############
###in scripts that use this wrapper:
###import crusher
###import wrapper
###crusher.Broker = wrapper.Broker
############

NUMOFREPLICAS = 24

class InvalidChecksum(Exception):
    pass

class Broker(Broken):
    def __init__(self, filename="demo.txt"):
        """Nothing changes for the initialization"""
        if(DEBUG):
            self.DEBUG_stored_in_db = {}
        return Broken.__init__(self, filename)
        
    def configure(self, s):
        """Nothing changes for the configuration"""
        return Broken.configure(self, s)
        
    def interrupt(self, signal, frame):
        """Nothing changes for the interrupt"""
        return Broken.interrupt(self, signal, frame)
        
    def fletcher32(self, string):
        #print(string)
        """Create a fletcher32 checksum and return it as 4 8bit characters"""
        a = list(map(ord, string))
        b = [sum(a[:i])%65535 for i in range(len(a)+1)]
        return chr((sum(b) >> 8) & 255) + chr((sum(b)) & 255) + chr((max(b) >> 8) & 255) + chr((max(b)) & 255)
        
    def store(self, key, val):
        if(DEBUG):
            print("store::", str(key), ":", str(val))
        """Make replicas of the key-val pair, add a checksum to val and store those,
        fetch/store each replica until the fetched value is the same as the stored
        value to check for validity in the cache (if it's invalid in the cache
        it's almost certainly invalid in the db)"""
        for i in range(NUMOFREPLICAS):
            again = True
            againMax = 100 #Avoid infi loops (db is really screwed if this matters)
            while(again == True and againMax > 0):
                againMax = againMax - 1
                again = False
                newKey = str(key) + str(i)
                newVal = str(val) + self.fletcher32((str(key)+str(val)))
                try:
                    if(DEBUG):
                        print("  ::Broken.store", newKey, newVal)
                    Broken.store(self, newKey, newVal)
                    if(DEBUG):
                        self.DEBUG_stored_in_db[newKey] = newVal
                    if(Broken.fetch(self, newKey) != newVal):
                        #Likely corrupted if we cant even get it back right from the cache
                        #Try again
                        if(DEBUG):
                            print("Broken.fetch(self, newKey) != newVal")
                        again = True
                
                except KeyError:
                    """Do nothing"""
                    #print(newKey + ": error 69")
                    again = True
        
    def fetch(self, key):
        if(DEBUG):
            print("Fetch::", str(key), end=" ")
        """Fetch each replica and use voting to determine the propert
        value, if the checksum does not match the key value pair then
        fail safely, in the event of ties in the voting seperate the possibilies
        and check with the checksum to determine the most likely correct val.
        In the event that there are more than 1
        candidates with their own correct checksums just pick one at random
        and then buy a lottery ticket."""
        values = []
        errors = 0
        key = str(key)
        for i in range(NUMOFREPLICAS):
            try:
                value = str((Broken.fetch(self, (str(key)+str(i)))))
                values.append(value)
            
            except KeyError:
                errors += 1
                if errors >= NUMOFREPLICAS:
                    if(DEBUG):
                        print("KeyError")
                    raise KeyError

        valLengths = []
        for value in values:
            valLengths.append(len(value))
        try:
            valLengths = self.voteInt(valLengths)
        except ValueError as e:
            valLengths = []
            #print("Empty list of values!")
        for lengths in valLengths:
            valuesWSameLengthTemp = []
            #For each possible length (if more than one length won the vote)
            for value in values:
                if len(value) == lengths:
                    valuesWSameLengthTemp.append(value)

            """
            If we have 9 or more acceptable values to vote on
            vote on 3 at a time then vote on the 3 winners of
            those votes.  Otherwise if we have 3 or more just
            vote on 3 of them.  If we only have 1 or 2 values
            just see if the checksum is valid.
            """
            possibleValues = []
            #9 or more
            if(len(valuesWSameLengthTemp) >= 11):
                if(len(valuesWSameLengthTemp) % 2 == 0):
                    possibleValues = self.voteStr(valuesWSameLengthTemp[:-1])
                else:
                    possibleValues = self.voteStr(valuesWSameLengthTemp)
            if(11 > len(valuesWSameLengthTemp) >= 9):
                possibleValues = self.voteStr(valuesWSameLengthTemp[:3])
                for item in self.voteStr(valuesWSameLengthTemp[3:6]):
                    possibleValues.append(item)
                for item in self.voteStr(valuesWSameLengthTemp[6:9]):
                    possibleValues.append(item)
                possibleValues = self.voteStr(possibleValues[:3])

            #3 - 8
            if(9 > len(valuesWSameLengthTemp) >= 3):
                possibleValues = self.voteStr(valuesWSameLengthTemp[:3])

            #1-2
            if(0 < len(valuesWSameLengthTemp) <= 2):
                for value in valuesWSameLengthTemp:
                    possibleValues.append(value)

            #0
            if(len(valuesWSameLengthTemp) <= 0):
                if(DEBUG):
                    print("NO VALUES WITH SAME LENGTH RETURNED")
                raise Exception("No values with same length returned")

            for value in possibleValues:
                if value[-4:] == self.fletcher32((str(key)+str(value[:-4]))):
                    if(DEBUG):
                        print(value[:-4])
                    return value[:-4]

            errorMessage = "No matching value-checksum pair for " + str(possibleValues)
            if(DEBUG):
                print("InvalidChecksum")
            raise InvalidChecksum(errorMessage)
            
        """
        try:
            raise InvalidChecksum("No matching value-checksum pair")
        except:
            print("No matching value-checksum pair for", values)
        """
            
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
        """Calls Broken.remove for each key copy and returns the 
        voted upon value.
        """
        valList = []
        for i in range(n):
            try:
                valList.append(str(Broken.remove(self, (str(key)+str(i)))))
            except:
                pass
        return self.voteStr(valList)
        
    def exit(self):
        """Nothing changes on exit"""
        return Broken.exit
        
