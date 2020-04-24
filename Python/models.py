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

def fewerTurnoversPGWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamATOPG = float(teamADF.loc[teamADF.index[0], 'WTOPG'])
    else:
        teamATOPG = float(teamADF.loc[teamADF.index[0], 'LTOPG'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBTOPG = float(teamBDF.loc[teamBDF.index[0], 'WTOPG'])
    else:
        teamBTOPG = float(teamBDF.loc[teamBDF.index[0], 'LTOPG'])

    if teamATOPG == teamBTOPG:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamATOPG > teamBTOPG:
        return teamA
    else:
        return teamB

def moreStealsPGWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamAStlPG = float(teamADF.loc[teamADF.index[0], 'WStlG'])
    else:
        teamAStlPG = float(teamADF.loc[teamADF.index[0], 'LStlPG'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBStlPG = float(teamBDF.loc[teamBDF.index[0], 'WStlPG'])
    else:
        teamBStlPG = float(teamBDF.loc[teamBDF.index[0], 'LStlPG'])

    if teamAStlPG == teamBStlPG:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamAStlPG > teamBStlPG:
        return teamA
    else:
        return teamB

# check this one to ensure more/fewer is correct for winner
def fewerFoulsPGWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamAPFPG = float(teamADF.loc[teamADF.index[0], 'WPFPG'])
    else:
        teamAPFPG = float(teamADF.loc[teamADF.index[0], 'LPFPG'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBPFPG = float(teamBDF.loc[teamBDF.index[0], 'WPFPG'])
    else:
        teamBPFPG = float(teamBDF.loc[teamBDF.index[0], 'LPFPG'])

    if teamAPFPG == teamBPFPG:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamAPFPG < teamBPFPG:
        return teamA
    else:
        return teamB

def moreDefReboundsPGWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamADRPG = float(teamADF.loc[teamADF.index[0], 'WDRPG'])
    else:
        teamADRPG = float(teamADF.loc[teamADF.index[0], 'LDRPG'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBDRPG = float(teamBDF.loc[teamBDF.index[0], 'WDRPG'])
    else:
        teamBDRPG = float(teamBDF.loc[teamBDF.index[0], 'LDRPG'])

    if teamADRPG == teamBDRPG:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamADRPG > teamBDRPG:
        return teamA
    else:
        return teamB

def moreBlocksPGWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamABlkPG = float(teamADF.loc[teamADF.index[0], 'WBlkPG'])
    else:
        teamABlkPG = float(teamADF.loc[teamADF.index[0], 'LBlkPG'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBBlkPG = float(teamBDF.loc[teamBDF.index[0], 'WBlkPG'])
    else:
        teamBBlkPG = float(teamBDF.loc[teamBDF.index[0], 'LBlkPG'])

    if teamABlkPG == teamBBlkPG:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamABlkPG > teamBBlkPG:
        return teamA
    else:
        return teamB

# check this one to ensure greater/less than is correct. trying to see if teams whose opponents have lower FG % win more. 
def lowerFGPercLoses(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamAFGPerc = float(teamADF.loc[teamADF.index[0], 'WFGPerc'])
    else:
        teamAFGPerc = float(teamADF.loc[teamADF.index[0], 'LFGPerc'])

    teamBDF = refDF[refDF['LTeamID'] == teamB]
    if teamBDF.empty:
        teamBDF = refDF[refDF['WTeamID'] == teamB]
        teamBFGPerc = float(teamBDF.loc[teamBDF.index[0], 'WFGPerc'])
    else:
        teamBBlkPG = float(teamBDF.loc[teamBDF.index[0], 'LFGPerc'])

    if teamAFGPerc == teamBFGPerc:
        rand = np.random.random()
        if rand < 0.5:
            return teamA
        else:
            return teamB
    elif teamAFGPerc < teamBFGPerc:
        return teamA
    else:
        return teamB