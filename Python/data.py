#### initialize libraries ####
import numpy as np
import pandas as pd
import os
import sys
import time

#### pull in data from provided csv's as data frames ####
seeds = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MNCAATourneySeeds.csv'))
results = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MNCAATourneyCompactResults.csv'))
regSeasResults = pd.read_csv(os.path.join(sys.path[0], '../Data/2020DataFiles/2020DataFiles/2020-Mens-Data/MDataFiles_Stage1/MRegularSeasonCompactResults.csv'))

#### prepare TourneySeeds data frame ####
seeds['TeamID'] = pd.Categorical(seeds.TeamID) #switch TeamID from int -> categorical type
seeds['section'] = seeds.Seed.str.extract(r'(.)') #use regex to extract bracket region as new column
seeds['numSeed'] = seeds.Seed.str.extract(r'([0-9][0-9])') #extract raw seed number as new column
seeds['playInRank'] = seeds.Seed.str.extract(r'[0-9][0-9](.?)') #if applicable, extract play-in game seeding as new column

seeds['playInRank'].replace(to_replace = ['a', 'b', ''], value = [1, 2, 0], inplace = True) #replace chars with ints in play-in ranks
seeds['playInRank'] = seeds.playInRank.astype(float) #convert strings to floats for play-in ranks

seeds['numSeed'] = seeds.numSeed.astype(float) #also convert numSeeds from strings to floats

seeds['numSeed'] = seeds.numSeed + (seeds.playInRank / 10) #incorporate play-in rank as decimal with regular rank

seeds.drop(['Seed', 'playInRank'], axis = 1, inplace = True) #don't need play-in rank or old seed columns anymore

#### prepare TourneyResults data frame ####
results['WTeamID'] = pd.Categorical(results.WTeamID) #convert team id's to categorical to match TourneySeeds data frame
results['LTeamID'] = pd.Categorical(results.LTeamID)

#### merging data frames ####
seeds.rename(columns = {'TeamID': 'WTeamID'}, inplace = True) #rename column to match results data frame
seedResults = pd.merge(results, seeds, on = ['WTeamID', 'Season']) #merge for winning teams
seedResults.rename(columns = {'section': 'WSection', 'numSeed': 'WNumSeed'}, inplace = True) #rename newly merged columns to reflect winning team only

seeds.rename(columns = {'WTeamID': 'LTeamID'}, inplace = True) #rename column to match up for losing team merge
seedResults = pd.merge(seedResults, seeds, on = ['LTeamID', 'Season']) #merge for losing teams
seedResults.rename(columns = {'section': 'LSection', 'numSeed': 'LNumSeed'}, inplace = True) #rename newly merged columns to reflect losing team only

seeds.rename(columns = {'LTeamID': 'TeamID'}, inplace = True) #rename the team id column in original seeds data frame to return to original

#### create a data frame with regular season W/L and PF/PA ####
years = regSeasResults.Season.unique()
masterSeasonTotals = pd.DataFrame(columns = ['Season', 'TeamID', 'W', 'L', 'PF', 'PA'])

for year in years[0:2]:
    print(year)
    actSeason = regSeasResults[regSeasResults.Season == year]
    actSeason.reset_index(inplace = True)
    teams = actSeason.WTeamID.append(actSeason.LTeamID).unique()
    nrow = len(teams)
    actSeasonTotals = pd.DataFrame(data = np.zeros((nrow, 6)), columns = ['Season', 'TeamID', 'W', 'L', 'PF', 'PA'])

    actSeasonTotals['Season'] = pd.Series(data = [year] * nrow)
    actSeasonTotals['TeamID'] = pd.Series(data = teams)

    for game in range(actSeason.shape[0]):
        WInd = actSeasonTotals.index[actSeasonTotals['TeamID'] == actSeason.loc[game, 'WTeamID']].tolist()[0]
        LInd = actSeasonTotals.index[actSeasonTotals['TeamID'] == actSeason.loc[game, 'LTeamID']].tolist()[0]
        actSeasonTotals.loc[WInd, 'W'] += 1
        actSeasonTotals.loc[LInd, 'L'] += 1
        actSeasonTotals.loc[WInd, 'PF'] += actSeason.loc[game, 'WScore']
        actSeasonTotals.loc[WInd, 'PA'] += actSeason.loc[game, 'LScore']
        actSeasonTotals.loc[LInd, 'PF'] += actSeason.loc[game, 'LScore']
        actSeasonTotals.loc[LInd, 'PA'] += actSeason.loc[game, 'WScore']

    masterSeasonTotals = pd.concat([masterSeasonTotals, actSeasonTotals], axis = 0)