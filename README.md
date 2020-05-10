Repo for files used for the 2020 Kaggle March Madness competition (https://www.kaggle.com/c/march-madness-analytics-2020). The data for the project was provided on the contest page, and should be extracted to a folder called 'Data' in the folder containing this repo in order to run the code as-is.


Folders and files:

GeneratedData folder contains pickles and csv's output and saved from the project. The pickles allow significant time to be saved since resource intensive code creating data frames does not need to be run multiple times

Python folder contains all python files related to the project:

    data.py: contains functions and methods for extracting, cleaning and managing the raw data

    simulation.py: contains functions and methods for simulating full march madness tournaments and comparing to historical results

    models.py: contains some functions for analyzing the data and others that can be fed to the simulator to drive game-by-game prediction.

    submissionNotebook.ipynb: the final notebook containing the write up of the project.
