import os
import shutil
import time
import csv

#
# TODO: delete testcases
#

# path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")


# deletes the folder and all its files if a directory with the given name exists
def delete_setup(name):
    filepath = os.path.join(cwd, "DATA", name)
    if os.path.exists(filepath):
        try:
            shutil.rmtree(filepath)
            print("Setup deleted.")
        except PermissionError as e:
            print("Can't delete setup. Please check Error: {}".format(e))
    else:
        print("Name does not exist, no deletion possible.")


# lists all created setups in the DATA directory
def list_setups():
    print("Current setups are:")
    for subdir, dirs, files in os.walk(datapath):
        for directory in dirs:
            print(directory)


# builds a new setup with all given parameters and
# creates a directory in the DATA-path with an info file
def setup(name, lvl_list, conjunctive=True):
    filepath = os.path.join(cwd, "DATA", name)
    # check if name already exists, return with info printed when yes
    if os.path.exists(filepath):
        print("Name \"{}\" already exists. Please choose another.".format(name))
        return
    # more troubleshooting with input parameters
    for level in lvl_list:
        if len(level) != 2:
            print("Wrong number of Arguments in lvl_list: list of level with length {}"
                  " found. lvl_list must be of Format [[num_level_1,"
                  "threshold_level_1],[num_level_2, threshold_level_2],...]".format(len(level)))
            return
        for element in level:
            if not isinstance(element, int):
                print("Error: Non-Integer value as level/threshold.")
                return
    # create new directory to store the data in
    try:
        os.mkdir(filepath)
    except OSError as e:
        print("Directory could not be created, please try again."
              "Be sure you don't use any of the following characters in the setup name: \ / : * ? < > |")
        print(e)
        return
    created = str(time.strftime("%d.%m.%Y at %H:%M:%S"))
    # write data in csv format
    with open(os.path.join(filepath, "info.csv"), 'w+', newline='', encoding='utf8') as file:
        writer = csv.writer(file, delimiter=',')
        metadata = [['Name', name], ['Created', created], ["Conjunctive?", conjunctive], ['']]
        # ["number of people", "threshold"]]
        writer.writerows(metadata)
        # writer.writerows(lvl_list)
    if setup_stats(lvl_list, name):
        print("Setup \"{}\" successfully created!".format(name))
    else:
        print("Because of that, ", end='')
        delete_setup(name)


# write the level stats to a separate file
# makes access for further work on setup easier (no offset for metadata)
def setup_stats(stat_list, name):
    filepath = os.path.join(cwd, "DATA", name)
    thresholds = [x[1] for x in stat_list]
    for i in range(len(thresholds) - 1):
        if not thresholds[i] < thresholds[i + 1]:
            print("Wrong setup for conjunctive structure: threshold for "
                  "level i must always be bigger than threshold(level i-1). \n"
                  "Here: thresholds[{}] = {} > {} = thresholds[{}]".format(i, thresholds[i], thresholds[i + 1], i + 1))
            return False
    with open(os.path.join(filepath, "level_stats.csv"), 'w+', newline='', encoding='utf8') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows([["People", "Threshold"]])
        writer.writerows(stat_list)
        return True


# print the info to a given setup
def get_info(name):
    filepath = os.path.join(cwd, "DATA", name, 'info.csv')
    statspath = os.path.join(cwd, "DATA", name, 'level_stats.csv')
    # check if setup exists
    if not os.path.exists(filepath):
        print("Setup does not exist.")
        return
    with open(filepath, 'r') as infofile:
        reader = csv.reader(infofile, delimiter=',')
        # get name
        name = next(reader)[1]
        # get creation date
        date = next(reader)[1]
        # get Con/Disjunctive
        conjunctive = next(reader)[1]
        if conjunctive:
            type_string = 'Conjunctive'
        else:
            type_string = 'Disjunctive'
        with open(statspath, 'r') as stats_file:
            lines = stats_file.read().splitlines()

        # Print all level-Info:
        print("Name: {} \n Type: {} \n Created: {}".format(name, type_string, date))
        print("Level structure is displayed as [number_of_people, threshold]:")
        for i in range(len(lines) - 1):
            print("Level {} structure is: [{}]".format(i, lines[i + 1]))


# delete_setup("newer_test_example_setup")
# setup("newer_test_example_setup", [[2, 1], [3, 2], [5, 4], [7, 6], [8, 9], [13, 11]], False)
# get_info("newer_test_example_setup")
