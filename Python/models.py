import numpy as np
import pandas as pd
import sklearn.model_selection
import sklearn.linear_model
import sklearn.preprocessing
from data import createDetailedLogRegDF

#### supporting functions ####

#simple function that takes a value and returns its sigmoid value (for logistic regression)
def sigmoid(x):
    return (1 / (1 + np.exp(-x)))

#function to calculate the AIC value of a model
#inputs:
#   y: the true y values
#   ySigmoid: sigmoid of predicted values
#   k: number of features
#output:
#   AIC: the AIC value
def AIC(y, ySigmoid, k):
    n = y.shape[0]
    residuals = y - ySigmoid
    RSS = (residuals ** 2).sum() #residual sum of squares
    AIC = float(2 * k - (2 * n * np.log(RSS / n)))
    return AIC

#function to run logistic regression and find the sigmoided prediction values
#inputs:
#   yTrain: y values to be used to train the model
#   xTrain: x values to be used to train
#   xTest: x values to be used for prediction
#outputs:
#   sigVals: the sigmoided values of the predicted y's
#   fitted model: the model as fitted on the provided data
def generateSigVals(yTrain, xTrain, xTest):
    model = sklearn.linear_model.LogisticRegression(max_iter = 500, solver = 'lbfgs')
    fittedModel = model.fit(xTrain, yTrain)

    rawVals = np.matmul(xTest, fittedModel.coef_[0])
    sigVals = sigmoid(rawVals)

    return [sigVals, fittedModel]

#### logistic models ####

#function to select variables based on AIC value; starts with full model and drops values with worst AIC impact until improvement no longer certain
#inputs:
#   yVariable: the name of the y value column
#   xVariables: the name of the x value columns
#   logRegDF: DF output by createLogRegDF in data.py
#   testCondition: AIC improvement threshold to stop searching (default 5)
#output:
#   bestModel: the optimal model as determined by AIC selection
def logisticSelect(yVariable, xVariables, logRegDF, testCondition = 5):
    logRegTemp = logRegDF[:]
    xVariablesTemp = xVariables[:]

    y = logRegTemp[yVariable].to_numpy()

    searching = True #stop flag for while loop

    while searching:
        fullDF = logRegTemp[xVariablesTemp] #full DF for this iteration
        x = fullDF.to_numpy()
        #use normalized x values to aid regression
        xTrain, xTest, yTrain, yTest = sklearn.model_selection.train_test_split(sklearn.preprocessing.StandardScaler().fit_transform(x), y, test_size = 0.2)
        
        output = (generateSigVals(yTrain, xTrain, xTest))

        fullModelAIC = AIC(yTest, output[0], xTest.shape[1]) #get AIC value for full model

        AICTestVals = [] #list to hold partial model AIC's
        
        for i in xVariablesTemp: #loop over remaining x variables
            x = fullDF.drop(columns = i).to_numpy() #drop each in turn
            xTrain, xTest, yTrain, yTest = sklearn.model_selection.train_test_split(sklearn.preprocessing.StandardScaler().fit_transform(x), y, test_size = 0.2)
            
            sigVals = (generateSigVals(yTrain, xTrain, xTest))[0] #run logistic regression leaving off ith column

            AICTestVals.append(AIC(yTest, sigVals, x.shape[1])) #put AIC value for this particular regression in AICTestVals list

        bestTestAICInd = AICTestVals.index(min(AICTestVals)) #location of optimal (minimum) AIC value for partial models
        bestTestAIC = min(AICTestVals) #minimum AIC test value is the best partial-model value

        #check to see whether improvement uncertain or number of variables too low to continue
        if fullModelAIC - bestTestAIC > testCondition and len(xVariablesTemp) > 2: 
            xVariablesTemp.pop(bestTestAICInd) #remove least important variable if not
        else:
            searching = False #otherwise stop the search

    bestModel = [output[1], xVariablesTemp] #the optimal model is the full model when search stops
        
    return bestModel

#function to run the logisticSelect function defined above an arbitrary number of times
#inputs:
#   yVariable: the name of the y value column (to be passed on to select function)
#   xVariables: the name of the x value columns (to be passed on to select function)
#   logRegDF: DF output by createLogRegDF in data.py (to be passed on to select function)
#   trials: number of times to run the selection
#output:
#   xVariableFreq: the number of times the variable in each position of xVariables was selected / total number of trials (% / 100)
def logisticSelectMulti(yVariable, xVariables, logRegDF, trials):
    xVariableCounts = [0] * len(xVariables) #initialize counts to 0

    #loop to run logisticSelect 'trials' times
    for _ in range(trials):
        keptVariables = logisticSelect(yVariable, xVariables, logRegDF)[1] #the variables kept by the optimal model
        for i in keptVariables:
            xVariableCounts[xVariables.index(i)] += 1 #add one to counts if variable was selected
    
    xVariableFreq = [x / trials for x in xVariableCounts] #divide counts by trials for ratio of times selected

    return xVariableFreq

#function to generate a logistic regression model
#inputs:
#   yVariable: the name of the y value column
#   xVariables: the name of the x value columns
#   logRegDF: DF output by createLogRegDF in data.py
#output:
#   fittedModel: the model
def generateModel(yVariable, xVariables, logRegDF):
    y = logRegDF[yVariable].to_numpy()
    x = logRegDF[xVariables].to_numpy()

    model = sklearn.linear_model.LogisticRegression()
    fittedModel = model.fit(x, y)

    return fittedModel
        
#### evaluation functions ####

#these are functions that are fed to the simulator and determine the winners of individual games; they all take two teams as inputs and output one of the two teams
#based on criteria inside the function (most often a simple comparison, e.g. whichever team has a better record)

#this function outputs the team with the higher tournament seed (ties broken by RNG)
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

#this one outputs team with better record (ties broken by RNG)
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

#outputs team with better point differenctial (tie broken with RNG)
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

#outputs team with better point differential per game
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

#outputs team with better free throw percentage
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

#outputs team with better assist to turnover ratio
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

#outputs the team that is predicted to win based on logistic regression model using all log reg values
def logRegPredictFull(teamA, teamB, refDF):
    tempDF = refDF[:]
    columns = ['NumSeed', 'Record', 'PtsPG', 'PtsPGDif', 'TrueShtPerc', 'ORPG', 'DRPG', 'AstPG', 'StlPG', 'BlkPG', 'TOPG', 'ATR', 'PFPG', 'FTAPG', 'DefMetric', 'ConfAppearances'] #columns of full model
    #these coefficients were found by running log reg with above variables
    coefs = np.array([-0.10652044, -0.46803654,  0.02073799,  0.11885845,  0.04021554,
        0.06865805, -0.09927938, -0.08682422,  0.01886909,  0.04548005,
        0.00183267, -0.16278378, -0.04832846, -0.06462267,  0.00453879,
        0.00111273])

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

    if int(prediction) == 1:
        return teamA
    else:
        return teamB

#outputs team predicted by a modified version of full logistic regression
def logRegPredictFullJr(teamA, teamB, refDF):
    tempDF = refDF[:]
    columns = ['NumSeed', 'Record', 'PtsPG', 'PtsPGDif', 'TrueShtPerc', 'ORPG', 'DRPG', 'AstPG', 'StlPG', 'BlkPG', 'TOPG', 'ATR']
    coefs = np.array([-0.1277661425254346, -0.9675537604278555, -0.005681323906525973, 0.11413038711685244, -0.024540742010719464, 0.04180380199954239, -0.09256655706875093, -0.04161029124478528, 0.02002168652823342, 0.07146572080518195, -0.04077721508134719, 0.047984788430770614])

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

    if int(prediction) == 1:
        return teamA
    else:
        return teamB

#outputs team predicted by modified LR
def logRegPredictFullJr2(teamA, teamB, refDF):
    tempDF = refDF[:]
    columns = ['PtsPG', 'PtsPGDif', 'TrueShtPerc', 'ORPG', 'DRPG', 'AstPG', 'StlPG', 'BlkPG', 'TOPG', 'ATR', 'PFPG', 'FTA']
    coefs = np.array([0.020714883570040817, 0.17002007754667767, 0.03602944702342518, 0.12329308766779627, -0.12172048042621396, -0.06613829111009499, -0.02885618574988073, 0.12477181224884713, -0.016781619320912718, 0.07356410081655884, -0.0848784870047061, -0.0478585789639538])

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

    if int(prediction) == 1:
        return teamA
    else:
        return teamB

#optimal LR model without seed variable
def logRegPredictMagicSansSeed(teamA, teamB, refDF):
    tempDF = refDF[:]
    columns = ['Record', 'PtsPG', 'PtsPGDif', 'TrueShtPerc', 'ORPG', 'DRPG', 'AstPG', 'StlPG', 'BlkPG', 'TOPG', 'ATR']
    coefs = np.array([-0.3000112640198275, -0.002747095279902614, 0.17618385050626156, 0.037458857171097176, 0.091408841627562, -0.10604946381149698, -0.037403770159481195, -0.03893248026459082, 0.1487904628442653, -0.05756544476815563, 0.3299547245146217])

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

    if int(prediction) == 1:
        return teamA
    else:
        return teamB

#outputs team with fewer turnovers per game
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

#outputs team with more steals per game (used in defensive metric calculation)
def moreStealsPGWins(teamA, teamB, refDF):
    teamADF = refDF[refDF['LTeamID'] == teamA]
    if teamADF.empty:
        teamADF = refDF[refDF['WTeamID'] == teamA]
        teamAStlPG = float(teamADF.loc[teamADF.index[0], 'WStlPG'])
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

#outputs team with fewer turnovers per game (used in defensive metric calculation)
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

#outputs team with more defensive rebounds per game (used in defensive metric calculation)
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

#outputs team with more blocks per game (used in defensive metric calculation)
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

#outputs team with better field goal percentage
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