import numpy as np
import pandas as pd

#### simulation ####

#function to generate every possible matchup for the given round of the tournament
#input:
#   round: the round for which all possible matchups will be returned
#output:
#   out: a list of lists, each of which is a pair of ranks that can play each other in a given round
def generateMatchups(round):
    seedNums = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15] #an ordered list of all the ranks

    groupSize = int((2 ** round) / 2) #a useful variable to be used for indexing later

    out = []
    
    count = 0 #another variable to be used for indexing

    #loop that generates the matchups for the given round using the seedNums list
    for _ in range(int(16 / 2 ** round)):
        pivots = seedNums[count:(count + groupSize)] #the values which will "anchor" the permutations
        leaves = seedNums[(count + groupSize):(count + groupSize + groupSize)] #the values to permute over
        for j in pivots: #run over the pivots
            for k in leaves: #for each pivot pair with each leaf
                out.append([j, k]) #add to end of out list
        count += 2 ** round
    
    return out

class tourneyGame:
    def __init__(self, evalFn, priorGameA = None, priorGameB = None, teamA = None, teamB = None):
        self.evalFn = evalFn
        self.priorGameA = priorGameA
        self.priorGameB = priorGameB
        self.teamA = teamA
        self.teamB = teamB

    def findWinner(self):
        if self.teamA == None:
            self.teamA = self.priorGameA.findWinner()
        if self.teamB == None:
            self.teamB = self.priorGameB.findWinner()
        
        self.winner = self.evalFn(self.teamA, self.teamB)

        return self.winner

#### evaluation functions ####

#function to find accuracy of picking highest seed every time
#input: 
#   seedResults: a data frame with merged seed info and results of tournament games from data file
#output:
#   accuracy: a decimal reflecting ratio of correct guesses
def highSeedWins(seedResults):
    nrow = seedResults.shape[0] #number of rows in the data frame
    seedResults['WExpected'] = seedResults.WTeamID #new column to hold winner we think will win each game; initialize to the actual winner id's

    #loop to populate the expected winner column
    for i in range(nrow):
        if seedResults.loc[i, 'WNumSeed'] >= seedResults.loc[i, 'LNumSeed']: #if the winner's seed is higher than the loser's
            seedResults.loc[i, 'WExpected'] = seedResults.loc[i, 'LTeamID'] #then replace the winner's id with the loser's id

    seedResults['correctGuess'] = seedResults.WExpected == seedResults.WTeamID #new column that is a T/F depending on whether our guess matched the actual

    accuracy = seedResults.correctGuess.sum() / nrow #accuracy is average of T/F column

    return accuracy