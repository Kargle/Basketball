import numpy as np
import pandas as pd
import sklearn.model_selection
import sklearn.linear_model
from data import createDetailedLogRegDF

#### supporting functions ####

def sigmoid(x):
    return (1 / (1 + np.exp(-x)))

def AIC(y, ySigmoid, k):
    n = y.shape[0]
    residuals = y - ySigmoid
    RSS = (residuals ** 2).sum()
    AIC = float(2 * k - (2 * n * np.log(RSS / n)))
    return AIC

def generateSigVals(yTrain, xTrain, xTest):
    model = sklearn.linear_model.LogisticRegression()
    fittedModel = model.fit(xTrain, yTrain)

    rawVals = np.matmul(xTest, fittedModel.coef_[0])
    sigVals = sigmoid(rawVals)

    return [sigVals, fittedModel]

#### logistic models ####

def logisticSelect(yVariable, xVariables, logRegDF, testCondition = 5):
    logRegTemp = logRegDF[:]
    xVariablesTemp = xVariables[:]

    y = logRegTemp[yVariable].to_numpy()

    searching = True

    while searching:
        fullDF = logRegTemp[xVariablesTemp]
        x = fullDF.to_numpy()
        xTrain, xTest, yTrain, yTest = sklearn.model_selection.train_test_split(x, y, test_size = 0.2)
        
        output = (generateSigVals(yTrain, xTrain, xTest))

        fullModelAIC = AIC(yTest, output[0], xTest.shape[1])

        AICTestVals = []
        
        for i in xVariablesTemp:
            x = fullDF.drop(columns = i).to_numpy()
            xTrain, xTest, yTrain, yTest = sklearn.model_selection.train_test_split(x, y, test_size = 0.2)
            
            sigVals = (generateSigVals(yTrain, xTrain, xTest))[0]

            AICTestVals.append(AIC(yTest, sigVals, x.shape[1]))

        bestTestAICInd = AICTestVals.index(min(AICTestVals))
        bestTestAIC = min(AICTestVals)

        if fullModelAIC - bestTestAIC > testCondition and len(xVariablesTemp) > 2:
            xVariablesTemp.pop(bestTestAICInd)
        else:
            searching = False

    bestModel = [output[1], xVariablesTemp]
        
    return bestModel

def logisticSelectMulti(yVariable, xVariables, logRegDF, trials):
    xVariableCounts = [0] * len(xVariables)

    for _ in range(trials):
        keptVariables = logisticSelect(yVariable, xVariables, logRegDF)[1]
        for i in keptVariables:
            xVariableCounts[xVariables.index(i)] += 1
    
    xVariableFreq = [x / trials for x in xVariableCounts]

    return xVariableFreq

def generateModel(yVariable, xVariables, logRegDF):
    y = logRegDF[yVariable].to_numpy()
    x = logRegDF[xVariables].to_numpy()

    model = sklearn.linear_model.LogisticRegression()
    fittedModel = model.fit(x, y)

    return fittedModel
        
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

def logRegPredict(teamA, teamB, refDF):
    tempDF = refDF[:]
    columns = ['NumSeed', 'Record', 'PtsPG', 'PtsPGDif', 'TrueShtPerc', 'ORPG', 'DRPG', 'AstPG', 'StlPG', 'BlkPG', 'TOPG', 'ATR', 'PFPG', 'FTA']
    #columns = ['PtsPG', 'TrueShtPerc', 'ORPG', 'DRPG', 'AstPG', 'StlPG', 'TOPG']
    coefs = np.array([-0.12527087010224833, -0.8478265586030146, 0.01907879378890501, 0.115046426987495, 0.05076787040868571, 0.07487047889229337, -0.10432085193602231, -0.08300822076128096, 0.019934487471426208, 0.056491390641182186, 0.0037638206945899877, -0.09985223088243766, -0.050215625731525285, -0.06529454750694046])
    #coefs = np.array([ 0.00643839,  2.12819211,  0.13969725,  0.09989202,  0.07317713, 0.1416132 , -0.29635142])

    tempDF = createDetailedLogRegDF(tempDF)

    teamADF = tempDF[tempDF['selfTeamID'] == teamA]
    prefixA = 'self'
    if teamADF.empty:
        teamADF = tempDF[tempDF['oppTeamID'] == teamA]
        prefixA = 'opp'   
    teamADF = teamADF.loc[teamADF.index[0],]
    teamASeed = teamADF[prefixA + 'NumSeed']
    
    teamBDF = tempDF[tempDF['selfTeamID'] == teamB]
    prefixB = 'self'
    if teamBDF.empty:
        teamBDF = tempDF[tempDF['oppTeamID'] == teamB]
        prefixB = 'opp'
    teamBDF = teamBDF.loc[teamBDF.index[0],]
    teamBSeed = teamADF[prefixB + 'NumSeed']

    teamAColumns = [prefixA + x for x in columns]
    teamBColumns = [prefixB + x for x in columns]
    difColumns = [x + 'Dif' for x in columns]
    
    teamADF = teamADF[teamAColumns]
    teamBDF = teamBDF[teamBColumns]

    difDF = pd.DataFrame(data = np.zeros(shape = (1, len(difColumns))), columns = difColumns)

    for i in columns:
        difDF[i + 'Dif'] = teamADF[prefixA + i] - teamBDF[prefixB + i]

    x = difDF.to_numpy()

    raw = np.matmul(x, coefs)
    sig = float(sigmoid(raw))
    prediction = round(sig)

    seedDif = teamASeed - teamBSeed
    #if seedDif >= 10:
    #    return teamA
    #elif seedDif <= -10:
    #    return teamB
    #else:
    if int(prediction) == 1:
        return teamA
    else:
        return teamB