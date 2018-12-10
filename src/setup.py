import os
import shutil
import time
import csv
import os.path
from read_and_write_data import write_level_stats
from path import get_data_path


# path to DATA directory
data_path = get_data_path()


# deletes the folder and all its files if a directory with the given name exists
def delete_setup(name):
    file_path = os.path.join(data_path, name)
    # only if file exists
    if os.path.exists(file_path):
        try:
            shutil.rmtree(file_path)
            print("'{}' deleted.".format(name))
        except PermissionError as e:
            print("Can't delete setup. Please check Error: {}".format(e))
            raise
    else:
        print("'{}' does not exist.".format(name))


# lists all created setups in the DATA directory
def list_setups():
    print("Current setups are:")
    for subdir, dirs, files in os.walk(data_path):
        for directory in dirs:
            print(directory)


# builds a new setup with all given parameters and
# creates a directory in the DATA-path with an info file
def setup(name, lvl_list, field_size=997, conjunctive=True):
    file_path = os.path.join(data_path, name)
    # check if name already exists, return with info printed when yes
    if os.path.exists(file_path):
        raise FileExistsError("Name \"{}\" already exists. Please choose another.".format(name))
    # troubleshooting with input parameters
    sum_of_all_people = 0
    for level_number, level in enumerate(lvl_list):
        sum_of_all_people += level[0]
        if len(level) != 2:
            raise ValueError("Wrong number of Arguments in lvl_list: list of level with length {} "
                             "found ({}). lvl_list must be of Format [[num_level_1,"
                             "threshold_level_1],[num_level_2, threshold_level_2],...]".format(len(level), level))
        for element in level:
            if not isinstance(element, int):
                raise TypeError("Error: Non-Integer value as level/threshold.")
        if sum_of_all_people < level[1]:
            raise ValueError("Threshold of level {} is {}, which is more than all "
                             "shareholders existing up to this point ({})."
                             .format(level_number, level[1], sum_of_all_people))
    # create new directory to store the data in
    try:
        os.mkdir(file_path)
    except OSError as e:
        print("Directory could not be created, please try again. "
              "Make sure you don't use any of the following characters in the setup name: \ / : * ? < > |\n{}"
              .format(repr(e)))
        raise
    # create info.csv file
    create_info_file(conjunctive, file_path, lvl_list, name, field_size)


# create the info.csv file for the given setup
def create_info_file(conjunctive, file_path, lvl_list, name, field_size):
    # get creation time
    created = str(time.strftime("%d.%m.%Y at %H:%M:%S"))
    # write data in csv format and save as 'info.csv'
    with open(os.path.join(file_path, "info.csv"), 'w+', newline='', encoding='utf8') as file:
        writer = csv.writer(file, delimiter=',')
        metadata = [['Name', name], ['Created', created],
                    ["Conjunctive?", conjunctive], ["Finite field size", field_size]]
        writer.writerows(metadata)
        write_level_stats(lvl_list, os.path.join(file_path, "level_stats.csv"))
    print("Setup \"{}\" successfully created!\nStored in {}".format(name, file_path))


# print the info to a given setup
def get_info(name):
    file_path = os.path.join(data_path, name, 'info.csv')
    path_to_level_stats = os.path.join(data_path, name, 'level_stats.csv')
    # check if setup exists
    if not os.path.exists(file_path):
        raise FileNotFoundError("Setup does not exist.")
    # else case:
    with open(file_path, 'r') as info_file:
        reader = csv.reader(info_file, delimiter=',')
        # get name
        name = next(reader)[1]
        # get creation date
        date = next(reader)[1]
        # get Con/Disjunctive
        conjunctive = next(reader)[1]
        # check if 'True' is written in file,
        # needs separate method because bool('False') evaluates to True
        if str2bool(conjunctive):
            type_string = 'Conjunctive'
        else:
            type_string = 'Disjunctive'
        # get all info from the level stats file
        with open(path_to_level_stats, 'r') as stats_file:
            lines = stats_file.read().splitlines()
            # Print all meta- & level-Info:
        print("Name: {}\nType: {}\nCreated: {}".format(name, type_string, date))
        print("Level structure is displayed as [number_of_people_in_level, threshold]:")
        for i in range(1, len(lines)):
            print("Level {} structure is: [{}]".format(i, lines[i]))


# check if given String is either "True", "true" or 1/"1"
# return True if so, else False
def str2bool(string_representation):
    return str(string_representation.lower()) in ("true", "1")
