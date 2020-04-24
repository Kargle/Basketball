import numpy as np
import pandas as pd

#### supporting functions ####

def sigmoid(x):
    return (1 / (1 + np.exp(-x)))

def AIC(y, ySigmoid, k):
    residuals = y - ySigmoid
    RSS = (residuals ** 2).sum()
    AIC = 2 * k - 2 * np.log(RSS)
    return AIC

def AICcomparison(AIC1, AIC2):
    if AIC1 <= AIC2:
        return np.exp((AIC1 - AIC2) / 2)
    else:
        return np.exp((AIC2 - AIC2) / 2)

#### logistic models ####

def logisticFull():
    
        
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

def betterPtsDifWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamAPtsDif = float(teamADF.loc[teamADF.index[0], 'WPtsDif'])
    else:
        teamAPtsDif = float(teamADF.loc[teamADF.index[0], 'LPtsDif'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBPtsDif = float(teamBDF.loc[teamBDF.index[0], 'WPtsDif'])
    else:
        teamBPtsDif = float(teamBDF.loc[teamBDF.index[0], 'LPtsDif'])

    if teamAPtsDif == teamBPtsDif:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamAPtsDif > teamBPtsDif:
        return teamA
    else:
        return teamB

def betterPtsDifPGWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamAPtsPGDif = float(teamADF.loc[teamADF.index[0], 'WPtsPGDif'])
    else:
        teamAPtsPGDif = float(teamADF.loc[teamADF.index[0], 'LPtsPGDif'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBPtsPGDif = float(teamBDF.loc[teamBDF.index[0], 'WPtsPGDif'])
    else:
        teamBPtsPGDif = float(teamBDF.loc[teamBDF.index[0], 'LPtsPGDif'])

    if teamAPtsPGDif == teamBPtsPGDif:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamAPtsPGDif > teamBPtsPGDif:
        return teamA
    else:
        return teamB

def betterFTPercWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamAFTPerc = float(teamADF.loc[teamADF.index[0], 'WFTPerc'])
    else:
        teamAFTPerc = float(teamADF.loc[teamADF.index[0], 'LFTPerc'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBFTPerc = float(teamBDF.loc[teamBDF.index[0], 'WFTPerc'])
    else:
        teamBFTPerc = float(teamBDF.loc[teamBDF.index[0], 'LFTPerc'])

    if teamAFTPerc == teamBFTPerc:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamAFTPerc > teamBFTPerc:
        return teamA
    else:
        return teamB

def betterAstTORatioWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamAATR = float(teamADF.loc[teamADF.index[0], 'WATR'])
    else:
        teamAATR = float(teamADF.loc[teamADF.index[0], 'LATR'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBATR = float(teamBDF.loc[teamBDF.index[0], 'WATR'])
    else:
        teamBATR = float(teamBDF.loc[teamBDF.index[0], 'LATR'])

    if teamAATR == teamBATR:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamAATR > teamBATR:
        return teamA
    else:
        return teamB