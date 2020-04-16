#### initialize libraries ####
import numpy as np
import pandas as pd
import os
import sys
import time

#### pull in data from provided csv's as data frames ####
seeds = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MNCAATourneySeeds.csv'))
tourneyCompactResults = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MNCAATourneyCompactResults.csv'))
regSeasCompactResults = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MRegularSeasonCompactResults.csv'))
regSeasDetailedResults = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MRegularSeasonDetailedResults.csv'))

#### other variables that will be needed ####
columnsCompact = ['Season', 'TeamID', 'G', 'W', 'L', 'Pts', 'PA']
columnsDetailed = ['Season', 'TeamID', 'G', 'W', 'L', 'Pts', 'PA', 'FGM', 'FGA', 'FGM3', 'FGA3', 'FTM', 'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl', 'Blk', 'PF']

#### data functions ####

#function that creates a data frame containing the game-level results of each tournament since 1985, including the seed and bracket region of each participant
#inputs:
#   seeds: a data frame pulled directly from MNCAATourneySeeds.csv
#   results: a data frame pulled directly from MNCAATourneyCompactResults.csv
#output:
#   seedResults: the created data frame with all information merged and cleaned
def createSeedResults1985DF(seeds, results):
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
            actSeasonTotals.loc[WInd, 'W'] += 1 #increment winning team's win total by 1
            actSeasonTotals.loc[LInd, 'L'] += 1 #increment losing team's loss total by 1
            actSeasonTotals.loc[WInd, 'Pts'] += actSeason.loc[game, 'WScore'] #add the winning team's points scored to their season PF total
            actSeasonTotals.loc[WInd, 'PA'] += actSeason.loc[game, 'LScore'] #add the losing team's points scored to the winning team's PA total
            actSeasonTotals.loc[LInd, 'Pts'] += actSeason.loc[game, 'LScore'] #do the same for the losing team
            actSeasonTotals.loc[LInd, 'PA'] += actSeason.loc[game, 'WScore']

            if ncol > 7: #test to see if this is the detailed run (otherwise this code won't run)
                for j in columns[7:]: #iterate through remaining data items
                    actSeasonTotals.loc[WInd, j] += actSeason.loc[game, ('W' + j)] #follow the procedure from above for winner and loser
                    actSeasonTotals.loc[LInd, j] += actSeason.loc[game, ('L' + j)]

        masterSeasonTotals = pd.concat([masterSeasonTotals, actSeasonTotals], axis = 0) #collect all the active seasons together in the master data frame created above

    masterSeasonTotals['G'] = masterSeasonTotals['W'] + masterSeasonTotals['L'] #fill in games played column with sum of win and loss columns

    return masterSeasonTotals

#function that merges the seedResults and regSeasTotals data frames created above
#inputs:
#   seedResults1985: defined above
#   regSeasTotals1985: defined above
#outputs:
#   outDF: a data frame that merges these two data frames such that the wins, losses and point totals from the regular season are included for both teams (W/L)
def createSeedResultRegTotals1985DF(seedResults1985, regSeasTotals1985):
    srFn = seedResults1985[:] #create copy to avoid modifying original
    rstFn = regSeasTotals1985[:]

    rstFn.rename(columns = {'TeamID': 'WTeamID'}, inplace = True) #this procedure is the same as in createSeedResults1985DF function above
    outDF = pd.merge(srFn, rstFn, on = ['WTeamID', 'Season'])
    outDF.rename(columns = {'W': 'WWins', 'L': 'WLosses', 'PF': 'WPF', 'PA': 'WPA'}, inplace = True)

    rstFn.rename(columns = {'WTeamID': 'LTeamID'}, inplace = True)
    outDF = pd.merge(outDF, rstFn, on = ['LTeamID', 'Season']) 
    outDF.rename(columns = {'W': 'LWins', 'L': 'LLosses', 'PF': 'LPF', 'PA': 'LPA'}, inplace = True)

    return outDF