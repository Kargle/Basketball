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

    if ncol > 7: #check to see whether this is detailed or compact stats DF (detailed if > 7)
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

#function that merges the seedResults and regSeasTotals data frames created above, and adds columns for conference appearances
#inputs:
#   seedResults: defined above
#   regSeasTotals: either of the compact or detailed regSeasTotals data frames created above
#outputs:
#   outDF: a data frame that merges these two data frames such that the columns defined above are incorporated for the winning and losing teams
def createMasterDF(seedResults, regSeasTotals):
    srFn = seedResults[:] #create copy to avoid modifying original
    rstFn = regSeasTotals[:]

    rstFn.rename(columns = {'TeamID': 'WTeamID'}, inplace = True) #match up column names to merge on
    outDF = pd.merge(srFn, rstFn, on = ['WTeamID', 'Season'])

    colNames = list(outDF.columns) 

    for i in range(12, len(colNames)): #loop to add a 'W' to the front of these column names because the values are for the winning team (first 12 columns are general game info)
        colNames[i] = re.sub(r'^', 'W', colNames[i])

    outDF.columns = colNames #use new column names

    colInd = len(colNames)

    #do the same thing as above but for the losing team
    rstFn.rename(columns = {'WTeamID': 'LTeamID'}, inplace = True)
    outDF = pd.merge(outDF, rstFn, on = ['LTeamID', 'Season'])

    colNames = list(outDF.columns)

    for i in range(colInd, len(colNames)):
        colNames[i] = re.sub(r'^', 'L', colNames[i])

    outDF.columns = colNames

    #this part adds the number of tournament game appearances for the winner's and loser's conferences (proxy for strength of schedule)
    outDF['LConfAppearances'] = pd.Series(data = np.zeros(outDF.shape[0])) #new columns to hold appearances
    outDF['WConfAppearances'] = pd.Series(data = np.zeros(outDF.shape[0]))

    LConfAppearances = outDF['LConfAbbrev'].value_counts() #get the totals for each conference for winners and losers
    WConfAppearances = outDF['WConfAbbrev'].value_counts()

    for i in LConfAppearances.index: #this loop combines the winner and loser appearances into one list with all the conferences
        if i in WConfAppearances.index:
            LConfAppearances[i] = LConfAppearances[i] + WConfAppearances[i]

    totalConfAppearances = LConfAppearances #rename for clarity

    for i in outDF.index: #loop over the DF and add the appropriate apppearances value based on the winner's and loser's conf appearances
        outDF.loc[i, 'LConfAppearances'] = totalConfAppearances[outDF.loc[i, 'LConfAbbrev']]
        outDF.loc[i, 'WConfAppearances'] = totalConfAppearances[outDF.loc[i, 'WConfAbbrev']]
    
    return outDF

#function to add extra stats / features that we want to explore in our analysis; this function is necessary to avoid running the resource intensive reg season stats DF function over and over
#inputs: 
#   regSeasStatsDF: the output of the createRegSeasonStatsDF defined above
#   detailed: boolean, default value True, communicating whether the input DF is detailed or compact
#output:
#   tempDF: the input DF with new columns added
def dataAugment(regSeasStatsDF, detailed = True):
    tempDF = regSeasStatsDF[:]

    #these will be run for both compact and detailed DFs
    tempDF['PtsDif'] = tempDF['Pts'] - tempDF['PA']
    tempDF['PtsPGDif'] = tempDF['PtsDif'] / tempDF['G']
    
    #these will only be added to detailed DF
    if detailed:   
        tempDF['ATR'] = tempDF['Ast'] / tempDF['TO']
        tempDF['TrueShtPerc'] = tempDF['Pts'] / (2 * (tempDF['FGA']) + (0.44 * tempDF['FTA']))
        tempDF['ORPG'] = tempDF['OR'] / tempDF['G']
        tempDF['DRPG'] = tempDF['DR'] / tempDF['G']
        tempDF['FTAPG'] = tempDF['FTA'] / tempDF['G']
        
        #these are all for calculating the def metric defined below
        avgStlPG = tempDF['StlPG'].mean()
        avgBlkPG = tempDF['BlkPG'].mean()
        avgPFPG = tempDF['PFPG'].mean()
        avgDRPG = tempDF['DRPG'].mean()

        tempDF['StlPGnorm'] = tempDF['StlPG'] / avgStlPG
        tempDF['BlkPGnorm'] = tempDF['BlkPG'] / avgBlkPG
        tempDF['PFPGnorm'] = tempDF['PFPG'] / avgPFPG
        tempDF['DRPGnorm'] = tempDF['DRPG'] / avgDRPG

        #this is a combination of the key defensive team stats, weighted by their ability to predict the outcome of games taken individually
        tempDF['DefMetric'] = tempDF['StlPGnorm'] * 0.3829596412556054 + tempDF['BlkPGnorm'] * 0.45112107623318387 + tempDF['PFPGnorm'] * 0.42511210762331836 + tempDF['DRPGnorm'] * 0.3874439461883408
        
    return tempDF

#function to add the conference of each team
#inputs:
#   regSeasStatsDF: output of createRegSeasonStatsDF defined above
#   conferences: raw conferences CSV from competition data
#outputs:
#   outDF: the input DF with conferences added
def addConferences(regSeasStatsDF, conferences):
    outDF = pd.merge(regSeasStatsDF, conferences, on = ['TeamID', 'Season'])
    return outDF

#function to make a DF that can be used to run logistic regression tests (primarily combines winner/loser stats into one "difference" stat)
#input:
#   detailedDF: final masterDetailed DF from running functions above
#output:
#   outDF
def createDetailedLogRegDF(detailedDF):
    tempDF = detailedDF[:]
    tempDF.reset_index(inplace = True)

    tempDF.rename(columns = {'WLoc': 'wLoc'}, inplace = True) #change to lower case to avoid issues with regex later

    tempDF['gameOutcome'] = pd.Series(data = np.random.randint(low = 0, high = 2, size = tempDF.shape[0])) #assign each game a random 0/1

    loseDF = tempDF[tempDF['gameOutcome'] == 0] #games assigned a 0 will be designated as a "loser" game (from POV of losing team)
    winDF = tempDF[tempDF['gameOutcome'] == 1] #games assigned a 1 from POV of winning team

    loseColumns = list(loseDF.columns)
    winColumns = list(winDF.columns)

    #this loop replaces the "W" and "L" for team stats with "self" and "opp", depending on POV defined above
    for i in range(len(loseColumns)):
        loseColumns[i] = re.sub(r'^W', 'opp', loseColumns[i]) #for loser, opponent is the winning team
        loseColumns[i] = re.sub(r'^L', 'self', loseColumns[i]) #self is losing team

        winColumns[i] = re.sub(r'^L', 'opp', winColumns[i]) #vice versa
        winColumns[i] = re.sub(r'^W', 'self', winColumns[i])

    loseDF.columns = loseColumns
    winDF.columns = winColumns

    loseDF = loseDF[winColumns] #reorder the loseDF columns to match the winDF columns for concatenation

    outDF = pd.concat((winDF, loseDF))

    #everything below is taking differences of self minus opp to obtain a dif score (easier for variable selection)
    outDF['SeedDif'] = outDF['selfNumSeed'] - outDF['oppNumSeed']
    outDF['RecordDif'] = outDF['selfRecord'] - outDF['oppRecord']
    outDF['PtsPGDif'] = outDF['selfPtsPG'] - outDF['oppPtsPG']
    outDF['FGPercDif'] = outDF['selfFGPerc'] - outDF['oppFGPerc']
    outDF['FG3PercDif'] = outDF['selfFG3Perc'] - outDF['oppFG3Perc']
    outDF['FTPercDif'] = outDF['selfFTPerc'] - outDF['oppFTPerc']
    outDF['TRDif'] = outDF['selfTR'] - outDF['oppTR']
    outDF['RebPGDif'] = outDF['selfRebPG'] - outDF['oppRebPG']
    outDF['AstPGDif'] = outDF['selfAstPG'] - outDF['oppAstPG']
    outDF['TOPGDif'] = outDF['selfTOPG'] - outDF['oppTOPG']
    outDF['StlPGDif'] = outDF['selfStlPG'] - outDF['oppStlPG']
    outDF['BlkPGDif'] = outDF['selfBlkPG'] - outDF['oppBlkPG']
    outDF['PFPGDif'] = outDF['selfPFPG'] - outDF['oppPFPG']
    outDF['PtsDifDif'] = outDF['selfPtsDif'] - outDF['oppPtsDif']
    outDF['PtsPGDifDif'] = outDF['selfPtsPGDif'] - outDF['oppPtsPGDif']
    outDF['ATRDif'] = outDF['selfATR'] - outDF['oppATR']
    outDF['TrueShtPercDif'] = outDF['selfTrueShtPerc'] - outDF['oppTrueShtPerc']
    outDF['ORPGDif'] = outDF['selfORPG'] - outDF['oppORPG']
    outDF['DRPGDif'] = outDF['selfDRPG'] - outDF['oppDRPG']
    outDF['FTAPGDif'] = outDF['selfFTAPG'] - outDF['oppFTAPG']
    outDF['ConfAppDif'] = outDF['selfConfAppearances'] - outDF['oppConfAppearances']
    outDF['DefMetricDif'] = outDF['selfDefMetric'] - outDF['oppDefMetric']
    return outDF


#### data imports ####

#### data from provided csv's as data frames ####
seeds = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MNCAATourneySeeds.csv'))
tourneyCompactResults = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MNCAATourneyCompactResults.csv'))
regSeasCompactResults = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MRegularSeasonCompactResults.csv'))
regSeasDetailedResults = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MRegularSeasonDetailedResults.csv'))
conferences = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MTeamConferences.csv'))

#### other variables that will be needed ####
columnsCompact = ['Season', 'TeamID', 'G', 'Wins', 'Losses', 'Pts', 'PA']
columnsDetailed = ['Season', 'TeamID', 'G', 'Wins', 'Losses', 'Pts', 'PA', 'FGM', 'FGA', 'FGM3', 'FGA3', 'FTM', 'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl', 'Blk', 'PF']

yVariable = 'gameOutcome'
xVariables = ['SeedDif', 'RecordDif', 'PtsPGDif', 'PtsPGDifDif', 'TrueShtPercDif', 'ORPGDif', 'DRPGDif', 'AstPGDif', 'StlPGDif', 'BlkPGDif', 'TOPGDif', 'ATRDif', 'PFPGDif', 'FTAPGDif', 'DefMetricDif', 'ConfAppDif']
xVariablesDesc = ['Difference in seeds', 'Difference in record', 'Difference in points per game', 'Difference in points per game differential', 'Difference in true shooting percentage',
                  'Difference in offensive rebounds per game', 'Difference in defensive rebounds per game', 'Difference in assists per game', 'Difference in steals per game',
                  'Difference in blocks per game', 'Difference in turnovers per game', 'Difference in assist to turnover ratio', 'Difference in personal fouls per game',
                  'Difference in free throw attempts per game', 'Difference in defensive metric (combination of blk, stl, DR, and PF) per game', 'Difference in conference appearances']
chosenFeatures = ['NumSeedDif', 'RecordDif', 'PtsPGDif', 'PtsPGDifDif', 'TrueShtPercDif', 'ORPGDif', 'DRPGDif', 'AstPGDif', 'StlPGDif', 'BlkPGDif', 'TOPGDif', 'ATRDif']

#### previously generated data ####
regSeasCompactTotals = pd.read_pickle(os.path.join(sys.path[0], '../GeneratedData/regSeasCompactTotals.pkl'))
regSeasDetailedTotals = pd.read_pickle(os.path.join(sys.path[0], '../GeneratedData/regSeasDetailedTotals.pkl'))

#### created data ####
seedResults = createSeedResultsDF(seeds, tourneyCompactResults)
regSeasDetailedTotals = dataAugment(regSeasDetailedTotals)
regSeasCompactTotals = addConferences(regSeasCompactTotals, conferences)
regSeasDetailedTotals = addConferences(regSeasDetailedTotals, conferences)
masterCompact = createMasterDF(seedResults, regSeasCompactTotals)
masterDetailed = createMasterDF(seedResults, regSeasDetailedTotals)
logRegDF = createDetailedLogRegDF(masterDetailed)