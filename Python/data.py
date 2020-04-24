#### initialize libraries ####
import numpy as np
import pandas as pd
import os
import sys
import time
import re

#### data functions ####

#function that creates a data frame containing the game-level results of each tournament since 1985, including the seed and bracket region of each participant
#inputs:
#   seeds: a data frame pulled directly from MNCAATourneySeeds.csv
#   results: a data frame pulled directly from MNCAATourneyCompactResults.csv
#output:
#   seedResults: the created data frame with all information merged and cleaned
def createSeedResultsDF(seeds, results):
    seedsFn = seeds[:] #create copy to avoid modifying original
    resultsFn = results[:]

    seedsFn['TeamID'] = pd.Categorical(seedsFn.TeamID) #switch TeamID from int -> categorical type
    seedsFn['section'] = seedsFn.Seed.str.extract(r'(.)') #use regex to extract bracket region as new column
    seedsFn['numSeed'] = seedsFn.Seed.str.extract(r'([0-9][0-9])') #extract raw seed number as new column
    seedsFn['playInRank'] = seedsFn.Seed.str.extract(r'[0-9][0-9](.?)') #if applicable, extract play-in game seeding as new column

    seedsFn['playInRank'].replace(to_replace = ['a', 'b', ''], value = [1, 2, 0], inplace = True) #replace chars with ints in play-in ranks
    seedsFn['playInRank'] = seedsFn.playInRank.astype(float) #convert strings to floats for play-in ranks

    seedsFn['numSeed'] = seedsFn.numSeed.astype(float) #also convert numSeeds from strings to floats

    seedsFn['numSeed'] = seedsFn.numSeed + (seedsFn.playInRank / 10) #incorporate play-in rank as decimal with regular rank

    seedsFn.drop(['Seed', 'playInRank'], axis = 1, inplace = True) #don't need play-in rank or old seed columns anymore

    #### prepare TourneyResults data frame ####
    resultsFn['WTeamID'] = pd.Categorical(resultsFn.WTeamID) #convert team id's to categorical to match TourneySeeds data frame
    resultsFn['LTeamID'] = pd.Categorical(resultsFn.LTeamID)

    #### merging data frames ####
    seedsFn.rename(columns = {'TeamID': 'WTeamID'}, inplace = True) #rename column to match resultsFn data frame
    seedResults = pd.merge(resultsFn, seedsFn, on = ['WTeamID', 'Season']) #merge for winning teams
    seedResults.rename(columns = {'section': 'WSection', 'numSeed': 'WNumSeed'}, inplace = True) #rename newly merged columns to reflect winning team only

    seedsFn.rename(columns = {'WTeamID': 'LTeamID'}, inplace = True) #rename column to match up for losing team merge
    seedResults = pd.merge(seedResults, seedsFn, on = ['LTeamID', 'Season']) #merge for losing teams
    seedResults.rename(columns = {'section': 'LSection', 'numSeed': 'LNumSeed'}, inplace = True) #rename newly merged columns to reflect losing team only

    return seedResults

#function that creates a data frame containing the wins, losses, points scored and points allowed of every NCAA div 1 team since 1985
#input:
#   regSeasonResults: a data frame pulled directly from MRegularSeasonCompactResults.csv or MRegularSeasonDetailedResults.csv
#   columns: a list with the names of the columns to be included (generally one of two configurations based on compact/detailed)
#output:
#   masterSeasonTotals: a data frame containing team id, season, G, W, L, PF, PA (and extra items if detailed) for every team
def createRegSeasonStatsDF(regSeasonResults, columns):
    years = regSeasonResults.Season.unique() #every unique year in the data set
    masterSeasonTotals = pd.DataFrame(columns = columns) #make an empty data frame to hold the new season data
    ncol = len(columns) #size of output data frame will depend on columns given

    #loop that iterates through each year in the data set and finds the W, L, PF and PA, and any additional columns, for each team in each year
    for year in years:
        print(year)
        actSeason = regSeasonResults[regSeasonResults.Season == year] #the currently active year (a subset of original data set)
        actSeason.reset_index(inplace = True) #reset the index of the subset (for cleaner indexing in next loop)
        teams = actSeason.WTeamID.append(actSeason.LTeamID).unique() #get list of unique teams for active year
        nrow = len(teams) #number of rows to be added to data frame
        actSeasonTotals = pd.DataFrame(data = np.zeros((nrow, ncol)), columns = columns) #create data frame with correct number of rows and columns for data fill

        actSeasonTotals['Season'] = pd.Series(data = [year] * nrow) #fill in this data frame with the current season
        actSeasonTotals['TeamID'] = pd.Series(data = teams) #also fill in with every team that played that season

        #loop that iterates through each game in the season and aggregates the info into the new data frame
        for game in range(actSeason.shape[0]):
            WInd = actSeasonTotals.index[actSeasonTotals['TeamID'] == actSeason.loc[game, 'WTeamID']].tolist()[0] #find the row index of the winning team in the active game
            LInd = actSeasonTotals.index[actSeasonTotals['TeamID'] == actSeason.loc[game, 'LTeamID']].tolist()[0] #row index of losing team in active game
            actSeasonTotals.loc[WInd, 'Wins'] += 1 #increment winning team's win total by 1
            actSeasonTotals.loc[LInd, 'Losses'] += 1 #increment losing team's loss total by 1
            actSeasonTotals.loc[WInd, 'Pts'] += actSeason.loc[game, 'WScore'] #add the winning team's points scored to their season PF total
            actSeasonTotals.loc[WInd, 'PA'] += actSeason.loc[game, 'LScore'] #add the losing team's points scored to the winning team's PA total
            actSeasonTotals.loc[LInd, 'Pts'] += actSeason.loc[game, 'LScore'] #do the same for the losing team
            actSeasonTotals.loc[LInd, 'PA'] += actSeason.loc[game, 'WScore']

            if ncol > 7: #test to see if this is the detailed run (otherwise this code won't run)
                for j in columns[7:]: #iterate through remaining data items
                    actSeasonTotals.loc[WInd, j] += actSeason.loc[game, ('W' + j)] #follow the procedure from above for winner and loser
                    actSeasonTotals.loc[LInd, j] += actSeason.loc[game, ('L' + j)]

        masterSeasonTotals = pd.concat([masterSeasonTotals, actSeasonTotals], axis = 0) #collect all the active seasons together in the master data frame created above

    masterSeasonTotals['G'] = masterSeasonTotals['Wins'] + masterSeasonTotals['Losses'] #fill in games played column with sum of win and loss columns

    masterSeasonTotals['Record'] = masterSeasonTotals['Wins'] / masterSeasonTotals['G']
    masterSeasonTotals['PtsPG'] = masterSeasonTotals['Pts'] / masterSeasonTotals['G']

    if ncol > 7:
        masterSeasonTotals['FGPerc'] = masterSeasonTotals['FGM'] / masterSeasonTotals['FGA']
        masterSeasonTotals['FG3Perc'] = masterSeasonTotals['FGM3'] / masterSeasonTotals['FGA3']
        masterSeasonTotals['FTPerc'] = masterSeasonTotals['FTM'] / masterSeasonTotals['FTA']
        masterSeasonTotals['TR'] = masterSeasonTotals['OR'] + masterSeasonTotals['DR']
        masterSeasonTotals['RebPG'] = masterSeasonTotals['TR'] / masterSeasonTotals['G']
        masterSeasonTotals['AstPG'] = masterSeasonTotals['Ast'] / masterSeasonTotals['G']
        masterSeasonTotals['TOPG'] = masterSeasonTotals['TO'] / masterSeasonTotals['G']
        masterSeasonTotals['StlPG'] = masterSeasonTotals['Stl'] / masterSeasonTotals['G']
        masterSeasonTotals['BlkPG'] = masterSeasonTotals['Blk'] / masterSeasonTotals['G']
        masterSeasonTotals['PFPG'] = masterSeasonTotals['PF'] / masterSeasonTotals['G']

    return masterSeasonTotals

#function that merges the seedResults and regSeasTotals data frames created above
#inputs:
#   seedResults: defined above
#   regSeasTotals: either of the compact or detailed regSeasTotals data frames created above
#outputs:
#   outDF: a data frame that merges these two data frames such that the columns defined above are incorporated for the winning and losing teams
def createMasterDF(seedResults, regSeasTotals):
    srFn = seedResults[:] #create copy to avoid modifying original
    rstFn = regSeasTotals[:]

    rstFn.rename(columns = {'TeamID': 'WTeamID'}, inplace = True)
    outDF = pd.merge(srFn, rstFn, on = ['WTeamID', 'Season'])

    colNames = list(outDF.columns)

    for i in range(12, len(colNames)):
        colNames[i] = re.sub(r'^', 'W', colNames[i])

    outDF.columns = colNames

    colInd = len(colNames)

    rstFn.rename(columns = {'WTeamID': 'LTeamID'}, inplace = True)
    outDF = pd.merge(outDF, rstFn, on = ['LTeamID', 'Season'])

    colNames = list(outDF.columns)

    for i in range(colInd, len(colNames)):
        colNames[i] = re.sub(r'^', 'L', colNames[i])

    outDF.columns = colNames
    
    return outDF

def dataAugment(regSeasStatsDF, detailed = True):
    tempDF = regSeasStatsDF[:]

    tempDF['PtsDif'] = tempDF['Pts'] - tempDF['PA']
    tempDF['PtsPGDif'] = tempDF['PtsDif'] / tempDF['G']
    #tempDF['4HistSeed'] = tempDF['Avg seed last 4 years']
    #tempDF['4HistRcd'] = tempDF['Wins/season last 4 years']
    #tempDF['25HistSeed'] = tempDF['Avg seed last 25 years']

    
    if detailed:   
        tempDF['ATR'] = tempDF['Ast'] / tempDF['TO']
        #tempDF['Def'] = tempDF[''] / tempDF['']
        #tempDF['OppFGPerc'] = tempDF['OppPts'] / tempDF['OppG'] <-- tried LFGPct here



    return tempDF

def createDetailedLogRegDF(detailedDF):
    tempDF = detailedDF[:]

    tempDF.rename(columns = {'WLoc': 'wLoc'}, inplace = True)

    tempDF['gameOutcome'] = pd.Series(data = np.random.randint(low = 0, high = 2, size = tempDF.shape[0]))

    loseDF = tempDF[tempDF['gameOutcome'] == 0]
    winDF = tempDF[tempDF['gameOutcome'] == 1]

    loseColumns = list(loseDF.columns)
    winColumns = list(winDF.columns)

    for i in range(len(loseColumns)):
        loseColumns[i] = re.sub(r'^W', 'Opp', loseColumns[i])
        loseColumns[i] = re.sub(r'^L', 'Self', loseColumns[i])

        winColumns[i] = re.sub(r'^L', 'Opp', winColumns[i])
        winColumns[i] = re.sub(r'^W', 'Self', winColumns[i])

    loseDF.columns = loseColumns
    winDF.columns = winColumns

    loseDF = loseDF[winColumns]

    outDF = pd.concat((winDF, loseDF))

    return outDF


#### data imports ####

#### data from provided csv's as data frames ####
seeds = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MNCAATourneySeeds.csv'))
tourneyCompactResults = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MNCAATourneyCompactResults.csv'))
regSeasCompactResults = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MRegularSeasonCompactResults.csv'))
regSeasDetailedResults = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MRegularSeasonDetailedResults.csv'))

#### other variables that will be needed ####
columnsCompact = ['Season', 'TeamID', 'G', 'Wins', 'Losses', 'Pts', 'PA']
columnsDetailed = ['Season', 'TeamID', 'G', 'Wins', 'Losses', 'Pts', 'PA', 'FGM', 'FGA', 'FGM3', 'FGA3', 'FTM', 'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl', 'Blk', 'PF']

#### generated data ####
regSeasCompactTotals = pd.read_pickle(os.path.join(sys.path[0], '../GeneratedData/regSeasCompactTotals.pkl'))
regSeasDetailedTotals = pd.read_pickle(os.path.join(sys.path[0], '../GeneratedData/regSeasDetailedTotals.pkl'))