import numpy as np
import pandas as pd

#function to find accuracy of picking highest seed every time
#input: 
#   seedResults: a data frame with merged seed info and results of tournament games from data file
#output:
#   accuracy: a decimal reflecting ratio of correct guesses
def highSeedWins(seedResults):
    nrow = seedResults.shape[0] #number of rows in the data frame
    seedResults['WExpected'] = seedResults.WTeamID #new column to hold winner we think will win each game; initialize to the actual winner id's

    #loop to populate the expected winner column
    for i in range(nrow):
        if seedResults.loc[i, 'WNumSeed'] >= seedResults.loc[i, 'LNumSeed']: #if the winner's seed is higher than the loser's
            seedResults.loc[i, 'WExpected'] = seedResults.loc[i, 'LTeamID'] #then replace the winner's id with the loser's id

    seedResults['correctGuess'] = seedResults.WExpected == seedResults.WTeamID #new column that is a T/F depending on whether our guess matched the actual

    accuracy = seedResults.correctGuess.sum() / nrow #accuracy is average of T/F column

    return accuracy

