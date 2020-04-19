import numpy as np
import pandas as pd
        
#### evaluation functions ####

def highSeedWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamASeed = float(teamADF.loc[teamADF.index[0], 'WNumSeed'])
    else:
        teamASeed = float(teamADF.loc[teamADF.index[0], 'LNumSeed'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBSeed = float(teamBDF.loc[teamBDF.index[0], 'WNumSeed'])
    else:
        teamBSeed = float(teamBDF.loc[teamBDF.index[0], 'LNumSeed'])

    if teamASeed == teamBSeed:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamASeed < teamBSeed:
        return teamA
    else:
        return teamB

def betterRecordWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamARecord = float(teamADF.loc[teamADF.index[0], 'WRecord'])
    else:
        teamARecord = float(teamADF.loc[teamADF.index[0], 'LRecord'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBRecord = float(teamBDF.loc[teamBDF.index[0], 'WRecord'])
    else:
        teamBRecord = float(teamBDF.loc[teamBDF.index[0], 'LRecord'])

    if teamARecord == teamBRecord:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamARecord > teamBRecord:
        return teamA
    else:
        return teamB


