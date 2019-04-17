import os
import pandas as pd
import csv
import os.path as path
from path import get_data_path, get_data_path_sss


# path to DATA directory
data_path = get_data_path()
shamir_data_path = get_data_path_sss()


# read all possible data from a given setup
def read_data(setup, read_data_number=None):
    # read level stats
    if read_data_number is None:
        threshold_path = os.path.join(data_path, setup, 'level_stats.csv')
    else:
        threshold_path = os.path.join(data_path, setup, 'level_stats_after_reset_{}.csv'.format(read_data_number))
    # read shareholders and values
    file_path = os.path.join(data_path, setup, 'shares.csv')
    data = pd.read_csv(file_path, skiprows=0, header=0, delimiter=',', )
    levels, thresholds = read_level_stats(threshold_path)
    return data, levels, thresholds


def read_field_size(setup, hierarchical=True):
    if not hierarchical:
        field_size_path = shamir_data_path
    else:
        field_size_path = data_path
    info_path = os.path.join(field_size_path, setup, 'info.csv')
    with open(info_path, 'r') as f:
        rows = list(csv.reader(f))
    return int(rows[-1][-1])


def read_sharing_type(setup):
    info_path = os.path.join(data_path, setup, 'info.csv')
    with open(info_path, 'r') as f:
        rows = list(csv.reader(f))
    boolean_type = rows[-2][-1]
    if boolean_type == "False":
        return False
    elif boolean_type == "True":
        return True
    else:
        raise TypeError


# write the level stats to a separate file
# makes access for further work on setup easier (no offset for metadata)
def write_level_stats(stat_list, file_path):
    # save file as 'level_stats.csv'
    with open(file_path, 'w+', newline='', encoding='utf8') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows([["People", "Threshold"]])
        writer.writerows(stat_list)


# create a unique file saving the resulting share-values in the corresponding directory
def create_reset_file(field_size, level_structure, resulting_shares, setup, hierarchical=True):
    # create a new file of reset values each time and give them a unique number
    number_of_reset = 0
    if not hierarchical:
        reset_path = shamir_data_path
    else:
        reset_path = data_path
    # search the smallest possible number not yet used for the new files
    while path.isfile(path.join(reset_path, setup, 'shares_after_reset_{}.csv'.format(number_of_reset))):
        number_of_reset += 1
    # create these files
    file_path = path.join(reset_path, setup, 'shares_after_reset_{}.csv'.format(number_of_reset))
    write_shares(field_size, file_path, resulting_shares)
    if hierarchical:
        level_stats_file_path = path.join(reset_path, setup, 'level_stats_after_reset_{}.csv'.format(number_of_reset))
        write_level_stats(level_structure, level_stats_file_path)
    return file_path, number_of_reset


# create a unique file saving the resulting share-values in the corresponding directory
def create_add_file(field_size, level_structure, resulting_shares, setup, hierarchical=True):
    # create a new file of reset values each time and give them a unique number
    number_of_add = 0
    if not hierarchical:
        add_path = shamir_data_path
    else:
        add_path = data_path
    # search the smallest possible number not yet used for the new files
    while path.isfile(path.join(add_path, setup, 'shares_after_add_{}.csv'.format(number_of_add))):
        number_of_add += 1
    # create these files
    file_path = path.join(add_path, setup, 'shares_after_add_{}.csv'.format(number_of_add))
    write_shares(field_size, file_path, resulting_shares, hierarchical)
    if hierarchical:
        level_stats_file_path = path.join(add_path, setup, 'level_stats_after_add_{}.csv'.format(number_of_add))
        write_level_stats(level_structure, level_stats_file_path)
    return file_path, number_of_add


# create a unique file saving the resulting share-values in the corresponding directory
def create_renew_file(field_size, resulting_shares, setup, hierarchical=True):
    # create a new file of renewed values each time and give them a unique number
    number_of_reset = 0
    if not hierarchical:
        renew_path = shamir_data_path
    else:
        renew_path = data_path
    # search the smallest possible number not yet used for a new file
    while path.isfile(path.join(renew_path, setup, 'shares_after_renew_{}.csv'.format(number_of_reset))):
        number_of_reset += 1
    # create this file
    file_path = path.join(renew_path, setup, 'shares_after_renew_{}.csv'.format(number_of_reset))
    write_shares(field_size, file_path, resulting_shares)
    return file_path


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
def write_shares(field_size, file_path, resulting_shares, hierarchical=True):
    with open(file_path, 'w+', newline='', encoding='utf8') as file:
        writer = csv.writer(file)
        # writer.writerow(["Chosen finite field size", field_size])
        writer.writerow(["Shareholder", "Share"])
        if hierarchical:
            writer.writerows(resulting_shares.items())
        else:
            writer.writerows(resulting_shares)
