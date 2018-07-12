import pandas as pd


# read the level statistics from the given file and
# return a list of the people in each level and the according thresholds
def read_level_stats(filepath):
    data = pd.read_csv(filepath, skiprows=1, header=None, delimiter=',', )
    # create list of number of people in each level
    list_of_people_per_level = list(data.iloc[:, 0])
    # print("Read people from levels: " + str(list_of_people_per_level))
    # create list of thresholds
    thresholds = list(data.iloc[:, 1])
    thresholds.insert(0, 0)
    # print("Read thresholds " + str(thresholds))
    return list_of_people_per_level, thresholds

