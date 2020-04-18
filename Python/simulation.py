import numpy as np
import pandas as pd
from data import *
from models import *

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
    def __init__(self, evalFn, refDF, priorGameA = None, priorGameB = None, teamA = None, teamB = None):
        self.evalFn = evalFn
        self.priorGameA = priorGameA
        self.priorGameB = priorGameB
        self.teamA = teamA
        self.teamB = teamB
        self.refDF = refDF

    def findWinner(self):
        if self.teamA == None:
            self.teamA = self.priorGameA.findWinner()
        if self.teamB == None:
            self.teamB = self.priorGameB.findWinner()
        
        self.winner = self.evalFn(self.teamA, self.teamB, self.refDF)

        return self.winner

class tourneyNet:
    def __init__(self, evalFn, refDF):
        self.net = []
        for _ in range(32):
            self.net.append(tourneyGame(evalFn, refDF))
        count = 0
        for i in [16, 8, 4, 2, 1]:
            for _ in range(i):
                self.net.append(tourneyGame(evalFn, refDF, priorGameA = self.net[count], priorGameB = self.net[count + 1]))
                count += 2
    
    def simulate(self):
        self.net[62].findWinner()
        return [x.winner for x in self.net]

def tourneySim(year, evalFn, detailed = False):
    #note that this implementation relies on matchups and the ref dataframe being global (i.e. accesible by the function without being explicitly passed)
    #should add in ability to manually enter team id's for a given season (what if scenarios)?
    if detailed == True:
        masterTemp = master2003[:]
    elif detailed == False:
        masterTemp = master1985[:]

    masterTemp = masterTemp[masterTemp['Season'] == year]
    #masterTemp.reset_index(inplace = True)
    
    tourney = tourneyNet(evalFn, masterTemp)

    playInGames = masterTemp[(masterTemp['WNumSeed'] != round(masterTemp['WNumSeed'])) & (masterTemp['LNumSeed'] != round(masterTemp['LNumSeed']))]
    playInGames.sort_values(by = ['WSection', 'WNumSeed'], inplace = True)
    playInGames.reset_index(inplace = True)

    nonPlayInGames = masterTemp[(masterTemp['WNumSeed'] == round(masterTemp['WNumSeed'])) | (masterTemp['LNumSeed'] == round(masterTemp['LNumSeed']))]
    nonPlayInGames.reset_index(inplace = True)

    for i in range(playInGames.shape[0]):
        if playInGames.loc[i, 'WSection'] == 'W':
            count = 0
        elif playInGames.loc[i, 'WSection'] == 'X':
            count = 8
        elif playInGames.loc[i, 'WSection'] == 'Y':
            count = 16
        elif playInGames.loc[i, 'WSection'] == 'Y':
            count = 24
        tourney.net.append(tourneyGame(evalFn, masterTemp, teamA = playInGames.loc[i, 'WTeamID'], teamB = playInGames.loc[i, 'LTeamID']))
        
        for j in range(len(matchups[0])):
            if int(playInGames.loc[i, 'WNumSeed']) == matchups[0][j][0]:
                tourney.net[count].priorGameA = tourney.net[-1]
                break
            if int(playInGames.loc[i, 'WNumSeed']) == matchups[0][j][1]:
                tourney.net[count].priorGameB = tourney.net[-1]
                break
            count += 1

    for i in range(nonPlayInGames.shape[0]):
        if nonPlayInGames.loc[i, 'WSection'] == 'W':
            count = 0
        elif nonPlayInGames.loc[i, 'WSection'] == 'X':
            count = 8
        elif nonPlayInGames.loc[i, 'WSection'] == 'Y':
            count = 16
        elif nonPlayInGames.loc[i, 'WSection'] == 'Z':
            count = 24
        firstRoundTestVar = [int(nonPlayInGames.loc[i, 'WNumSeed']), int(nonPlayInGames.loc[i, 'LNumSeed'])]

        for j in range(len(matchups[0])):
            if matchups[0][j] == firstRoundTestVar or list(reversed(matchups[0][j])) == firstRoundTestVar:
                winnerBetterSeedBool = nonPlayInGames.loc[i, 'WNumSeed'] < nonPlayInGames.loc[i, 'LNumSeed']
                if winnerBetterSeedBool:
                    if tourney.net[count].priorGameA is None:
                        tourney.net[count].teamA = nonPlayInGames.loc[i, 'WTeamID']
                    if tourney.net[count].priorGameB is None:
                        tourney.net[count].teamB = nonPlayInGames.loc[i, 'LTeamID']
                    break
                else:
                    if tourney.net[count].priorGameA is None:
                        tourney.net[count].teamA = nonPlayInGames.loc[i, 'LTeamID']
                    if tourney.net[count].priorGameB is None:
                        tourney.net[count].teamB = nonPlayInGames.loc[i, 'WTeamID']
                    break
            count += 1

    outList = tourney.simulate()
    return outList

#### debugging test cases (delete for final) ####
global master1985, matchups
seedResultsCompact = createSeedResults1985DF(seeds, tourneyCompactResults)
master1985 = createSeedResultRegTotals1985DF(seedResultsCompact, regSeasCompactTotals)
matchups = [generateMatchups(1), generateMatchups(2), generateMatchups(3), generateMatchups(4)]

tourneySim(2019, highSeedWins)