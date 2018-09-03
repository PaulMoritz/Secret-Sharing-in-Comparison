import pandas as pd
import csv


# read the level statistics from the given file and
# return a list of the people in each level and the according thresholds
def read_level_stats(file_path):
    data = pd.read_csv(file_path, skiprows=1, header=None, delimiter=',', )
    # create list of number of people in each level
    list_of_people_per_level = list(data.iloc[:, 0])
    # print("Read people from levels: " + str(list_of_people_per_level))
    # create list of thresholds
    thresholds = list(data.iloc[:, 1])
    thresholds.insert(0, 0)
    # print("Read thresholds " + str(thresholds))
    return list_of_people_per_level, thresholds


# write the calculated share values to a comma separated file, also save the finite field size
def write_shares(field_size, file_path, resulting_shares):
    with open(file_path, 'w+', newline='', encoding='utf8') as file:
        writer = csv.writer(file)
        writer.writerow(["Chosen finite field size", field_size])
        writer.writerow(["Shareholder", "Share"])
        writer.writerows(resulting_shares.items())
