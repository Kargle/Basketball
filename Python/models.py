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

def totalPtsDifWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamApointsDif = float(teamADF.loc[teamADF.index[0], 'pointsDif'])
    #else:
    #    teamARecord = float(teamADF.loc[teamADF.index[0], 'LRecord'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBpointsDif = float(teamBDF.loc[teamBDF.index[0], 'pointsDif'])
    #else:
    #    teamBRecord = float(teamBDF.loc[teamBDF.index[0], 'LRecord'])

    if teamApointsDif == teamBpointsDif:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamApointsDif > teamBpointsDif:
        return teamA
    else:
        return teamB

def avgPtsDifWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamAavgPtsDif = float(teamADF.loc[teamADF.index[0], 'avgPtsDif'])
    #else:
    #    teamARecord = float(teamADF.loc[teamADF.index[0], 'LRecord'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBavgPtsDif = float(teamBDF.loc[teamBDF.index[0], 'avgPtsDif'])
    #else:
    #    teamBRecord = float(teamBDF.loc[teamBDF.index[0], 'LRecord'])

    if teamAavgPtsDif == teamBavgPtsDif:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamAavgPtsDif > teamBavgPtsDif:
        return teamA
    else:
        return teamB

def FTpctWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamAFTpct = float(teamADF.loc[teamADF.index[0], 'FTPct'])
    #else:
    #    teamARecord = float(teamADF.loc[teamADF.index[0], 'LRecord'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBFTPct = float(teamBDF.loc[teamBDF.index[0], 'FTPct'])
    #else:
    #    teamBRecord = float(teamBDF.loc[teamBDF.index[0], 'LRecord'])

    if teamAFTpct == teamBFTPct:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamAFTpct > teamBFTPct:
        return teamA
    else:
        return teamB

def AstTORatioWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamAato = float(teamADF.loc[teamADF.index[0], 'ATO'])
    #else:
    #    teamARecord = float(teamADF.loc[teamADF.index[0], 'LRecord'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBato = float(teamBDF.loc[teamBDF.index[0], 'ATO'])
    #else:
    #    teamBRecord = float(teamBDF.loc[teamBDF.index[0], 'LRecord'])

    if teamAato == teamBato:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamAato > teamBato:
        return teamA
    else:
        return teamB
