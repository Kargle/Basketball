import numpy as np
import pandas as pd

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

#class that represents an individual game in a tournament
#attributes:
#   evalFn: the function to be used to determine the winner of the game (see models.py)
#   refDF: the data frame that contains stats for all the teams (to be used by the evalFn)
#   priorGameA: the prior game that leads into this game and determined teamA for this game (another tourneyGame object)
#   priorGameB: priot game that determines teamB (tourneyGame object)
#   teamA: the teamID of team A for this game
#   teamB: the teamID of team B for this game
#   winner (defined after initialization): the winner of the game
class tourneyGame:
    def __init__(self, evalFn, refDF, priorGameA = None, priorGameB = None, teamA = None, teamB = None):
        self.evalFn = evalFn
        self.priorGameA = priorGameA
        self.priorGameB = priorGameB
        self.teamA = teamA
        self.teamB = teamB
        self.refDF = refDF

    #function to determine the winner of this game
    def findWinner(self):
        if self.teamA == None: 
            self.teamA = self.priorGameA.findWinner() #if team A not given, call findWinner() on priorGameA tourneyGame object to obtain team A
        if self.teamB == None: 
            self.teamB = self.priorGameB.findWinner() #same for team B
        
        self.winner = self.evalFn(self.teamA, self.teamB, self.refDF) #new attribute 'winner' is the teamID of the winning team as determined by evalFn

        return self.winner

#class that represents an entire tournament
#attributes:
#   evalFn: the function to be used to determine the winner of the games (see models.py)
#   refDF: the data frame that contains stats for all the teams (to be used by the evalFn)
#   net: a list containing all tourneyGame objects that make up the tournament, linked together appropriately
class tourneyNet:
    def __init__(self, evalFn, refDF):
        self.net = [] #initialize net attribute as empty list
        for _ in range(32): 
            self.net.append(tourneyGame(evalFn, refDF)) #first round of games go in order into the net
        count = 0
        #loops to drop in remaining rounds with links to prior round games as priors
        for i in [16, 8, 4, 2, 1]:
            for _ in range(i):
                self.net.append(tourneyGame(evalFn, refDF, priorGameA = self.net[count], priorGameB = self.net[count + 1]))
                count += 2
    
    #function that calls the 63rd (championship) game's findWinner() function and recursively determines winners of all games
    def simulate(self):
        self.net[62].findWinner()
        return [x.winner for x in self.net]

#function that simulates a full tournament based on the actual teams that played in the tournament as well as a particular evalFn for picking winners
#inputs:
#   year: the year to be simulated
#   evalFn: the function to be used to determine the winner of the games (see models.py)
#   refDF: the data frame that contains stats for all the teams
#output:
#   outList: a list containing the teamID of each victorious team in the tournament; will be the length of the number of games in the tournament
def tourneySim(year, evalFn, refDF):
    masterTemp = refDF[:]

    matchups = [generateMatchups(1), generateMatchups(2), generateMatchups(3), generateMatchups(4)] #combinations of seeds that can play in each of the first four rounds

    masterTemp = masterTemp[masterTemp['Season'] == year] #subset by year
    
    tourney = tourneyNet(evalFn, masterTemp)

    playInGames = masterTemp[(masterTemp['WNumSeed'] != round(masterTemp['WNumSeed'])) & (masterTemp['LNumSeed'] != round(masterTemp['LNumSeed']))] #the games that are not part of the 63 "regular" tourney games
    playInGames.sort_values(by = ['WSection', 'WNumSeed'], inplace = True) #sort for easy comparison later
    playInGames.reset_index(inplace = True)

    nonPlayInGames = masterTemp[(masterTemp['WNumSeed'] == round(masterTemp['WNumSeed'])) | (masterTemp['LNumSeed'] == round(masterTemp['LNumSeed']))] #all other games are "regular" 63 games
    nonPlayInGames.reset_index(inplace = True)

    sectionDict = {'W': 0, 'X': 8, 'Y': 16, 'Z': 24} #dictionary that contains index of each section's games (e.g. section X games start at position 8 in the tourney net)

    #loop to add the play in games to the end of the tourney net
    for i in range(playInGames.shape[0]):
        count = sectionDict[playInGames.loc[i, 'WSection']]
        tourney.net.append(tourneyGame(evalFn, masterTemp, teamA = playInGames.loc[i, 'WTeamID'], teamB = playInGames.loc[i, 'LTeamID']))
        
        #loop to connect the appropriate first round games to the play in game object just created
        for j in range(len(matchups[0])):
            if int(playInGames.loc[i, 'WNumSeed']) == matchups[0][j][0]:
                tourney.net[count].priorGameA = tourney.net[-1]
                break
            if int(playInGames.loc[i, 'WNumSeed']) == matchups[0][j][1]:
                tourney.net[count].priorGameB = tourney.net[-1]
                break
            count += 1

    #loop to fill in the first round non play in games based on section and seed (other rounds already connected)
    for i in range(nonPlayInGames.shape[0]):
        count = sectionDict[nonPlayInGames.loc[i, 'WSection']] #look up the index for the section
        firstRoundTestVar = [int(nonPlayInGames.loc[i, 'WNumSeed']), int(nonPlayInGames.loc[i, 'LNumSeed'])] #the test var is the seeds of the teams

        for j in range(len(matchups[0])):
            if matchups[0][j] == firstRoundTestVar or list(reversed(matchups[0][j])) == firstRoundTestVar: #if the test var matches a member of the first round matchups it is a first round game
                winnerBetterSeedBool = nonPlayInGames.loc[i, 'WNumSeed'] < nonPlayInGames.loc[i, 'LNumSeed'] #T/F whether the winner of the game had a higher seed (for indexing)
                if winnerBetterSeedBool:
                    if tourney.net[count].priorGameA is None: #as long as there was no play in game for team A spot
                        tourney.net[count].teamA = nonPlayInGames.loc[i, 'WTeamID'] #slot in the winning team for team A (team A is higher seed)
                    if tourney.net[count].priorGameB is None: 
                        tourney.net[count].teamB = nonPlayInGames.loc[i, 'LTeamID'] #same for team B
                    break
                else: #if the winner had the lower seed, switch it around
                    if tourney.net[count].priorGameA is None:
                        tourney.net[count].teamA = nonPlayInGames.loc[i, 'LTeamID']
                    if tourney.net[count].priorGameB is None:
                        tourney.net[count].teamB = nonPlayInGames.loc[i, 'WTeamID']
                    break
            count += 1

    outList = tourney.simulate() #trigger the recursive evaluation of the network
    return outList

#function to output the actual winners of the tournament for a particular year in the same order as the tourneySim function (for comparison, to determine accuracy)
def tourneyActual(year, compactDF):
    masterTemp = compactDF[:]

    matchups = [generateMatchups(1), generateMatchups(2), generateMatchups(3), generateMatchups(4)]

    masterTemp = masterTemp[masterTemp['Season'] == year]

    playInGames = masterTemp[(masterTemp['WNumSeed'] != round(masterTemp['WNumSeed'])) & (masterTemp['LNumSeed'] != round(masterTemp['LNumSeed']))]
    playInGames.sort_values(by = ['WSection', 'WNumSeed'], inplace = True) #sort play in games by same criteria as above
    playInGames.reset_index(inplace = True)

    nonPlayInGames = masterTemp[(masterTemp['WNumSeed'] == round(masterTemp['WNumSeed'])) | (masterTemp['LNumSeed'] == round(masterTemp['LNumSeed']))]
    nonPlayInGames.reset_index(inplace = True)

    roundIndList = [0, 32, 48, 56] #index for the first game of each round
    roundSectionMultiplierList = [8, 4, 2, 1] #multiplier for each section by round
    matchupsDivisorList = [1, 4, 16, 64] #need to divide the matchups count by a number for each round later
    sectionDict = {'W': 0, 'X': 1, 'Y': 2, 'Z': 3} #key for each section within each round

    out = [0] * 63

    #loop that gets winner of each game in correct order
    for i in range(nonPlayInGames.shape[0]):
        if nonPlayInGames.loc[i, 'DayNum'] == 152 and (nonPlayInGames.loc[i, 'WSection'] == 'W' or nonPlayInGames.loc[i, 'WSection'] == 'X'): #this would be a final four game
            index = 60
        elif nonPlayInGames.loc[i, 'DayNum'] == 152 and (nonPlayInGames.loc[i, 'WSection'] == 'Y' or nonPlayInGames.loc[i, 'WSection'] == 'Z'): #final four game
            index = 61
        elif nonPlayInGames.loc[i, 'DayNum'] == 154: #championship game
            index = 62
        else: #otherwise it is a game in the first four rounds
            testVar = [int(nonPlayInGames.loc[i, 'WNumSeed']), int(nonPlayInGames.loc[i, 'LNumSeed'])] #get seeds of teams in the game

            breakFlag = False
            for j in range(len(matchups)): #iterate through the four rounds of matchup
                for k in range(len(matchups[j])): #iterate over each of the possible seeds for each round
                    if matchups[j][k] == testVar or list(reversed(matchups[j][k])) == testVar: #if our game matches the matchup
                        roundNum = j #this is the round of our game
                        gameNum = k #this is the game index of our game (how many from the first game of the round on the bracket)
                        breakFlag = True 
                        break
                if breakFlag:
                    break
            
            roundInd = roundIndList[roundNum] #get the index of the start of the correct round for this game
            roundSectionMultiplier = roundSectionMultiplierList[roundNum] #get the multiplier for the correct round and the correct section
            matchupsDivisor = matchupsDivisorList[roundNum] #will need this for game indexing
            sectionNum = sectionDict[nonPlayInGames.loc[i, 'WSection']]

            index = roundInd + (roundSectionMultiplier * sectionNum) + int(gameNum / matchupsDivisor) #index of the game in the network

        out[index] = nonPlayInGames.loc[i, 'WTeamID'] #put the winning team in the list at this point
    
    for i in range(playInGames.shape[0]):
        out.append(playInGames.loc[i, 'WTeamID']) #add the play in games to the end in order

    return out

#function to compare the results of a simulated tournament with the true results
#inputs:
#   yearsList: a list of years to compare games within
#   evalFn: the function to be used to determine the winner of the games (see models.py)
#   compactDF: the compact tourney results DF (only need compact for game winners)
#   refDF: the DF containing stats for all the teams (default value: None)
def tourneySimVsActual(yearsList, evalFn, compactDF, refDF = None):
    if refDF is None:
        refDF = compactDF #use compact if no refDF given

    simResults = []
    actualResults = []

    for i in yearsList:
        simResults = simResults + tourneySim(i, evalFn, refDF) #append the results of our simulated tournament for a particular year
        actualResults = actualResults + tourneyActual(i, compactDF) #append the actual results for that year

    simMatchEqual = [x == y for x, y in zip(simResults, actualResults)] #list with True where the predicted winner is the same as the actual winner
    accuracy = sum(simMatchEqual) / len(simMatchEqual) #accuracy is ratio of correct predictions

    return accuracy