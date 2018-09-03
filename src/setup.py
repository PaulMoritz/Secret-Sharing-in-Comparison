import os
import shutil
import time
import csv
import os.path

#
# TODO: Only conjunctive secret sharing implemented
#

# path to DATA directory
cwd = os.getcwd()
main_directory = os.path.abspath(os.path.join(cwd, os.pardir))
data_path = os.path.join(main_directory, "DATA")


# deletes the folder and all its files if a directory with the given name exists
def delete_setup(name):
    file_path = os.path.join(data_path, name)
    if os.path.exists(file_path):
        try:
            shutil.rmtree(file_path)
            print("Setup deleted.")
        except PermissionError as e:
            print("Can't delete setup. Please check Error: {}".format(e))
    else:
        print("Name does not exist.")


# lists all created setups in the DATA directory
def list_setups():
    print("Current setups are:")
    for subdir, dirs, files in os.walk(data_path):
        for directory in dirs:
            print(directory)


# builds a new setup with all given parameters and
# creates a directory in the DATA-path with an info file
def setup(name, lvl_list, conjunctive=True):
    file_path = os.path.join(data_path, name)
    # check if name already exists, return with info printed when yes
    if os.path.exists(file_path):
        print("Name \"{}\" already exists. Please choose another.".format(name))
        return
    # more troubleshooting with input parameters
    for level in lvl_list:
        if len(level) != 2:
            print("Wrong number of Arguments in lvl_list: list of level with length {}"
                  " found ({}). lvl_list must be of Format [[num_level_1,"
                  "threshold_level_1],[num_level_2, threshold_level_2],...]".format(len(level), level))
            return
        for element in level:
            if not isinstance(element, int):
                print("Error: Non-Integer value as level/threshold.")
                return
    # create new directory to store the data in
    try:
        os.mkdir(file_path)
    except OSError as e:
        print("Directory could not be created, please try again."
              "Be sure you don't use any of the following characters in the setup name: \ / : * ? < > |")
        print(e)
        return
    created = str(time.strftime("%d.%m.%Y at %H:%M:%S"))
    # write data in csv format
    with open(os.path.join(file_path, "info.csv"), 'w+', newline='', encoding='utf8') as file:
        writer = csv.writer(file, delimiter=',')
        metadata = [['Name', name], ['Created', created], ["Conjunctive?", conjunctive], ['']]
        # ["number of people", "threshold"]]
        writer.writerows(metadata)
        # writer.writerows(lvl_list)
    setup_stats(lvl_list, name)
    print("Setup \"{}\" successfully created!".format(name))


# write the level stats to a separate file
# makes access for further work on setup easier (no offset for metadata)
def setup_stats(stat_list, name):
    file_path = os.path.join(data_path, name)
    with open(os.path.join(file_path, "level_stats.csv"), 'w+', newline='', encoding='utf8') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows([["People", "Threshold"]])
        writer.writerows(stat_list)


# print the info to a given setup
def get_info(name):
    file_path = os.path.join(data_path, name, 'info.csv')
    path_to_level_stats = os.path.join(data_path, name, 'level_stats.csv')
    # check if setup exists
    if not os.path.exists(file_path):
        print("Setup does not exist.")
        return
    with open(file_path, 'r') as info_file:
        reader = csv.reader(info_file, delimiter=',')
        # get name
        name = next(reader)[1]
        # get creation date
        date = next(reader)[1]
        # get Con/Disjunctive
        conjunctive = next(reader)[1]
        if str2bool(conjunctive):
            type_string = 'Conjunctive'
        else:
            type_string = 'Disjunctive'
        with open(path_to_level_stats, 'r') as stats_file:
            lines = stats_file.read().splitlines()
            # Print all level-Info:
            print("Name: {}\nType: {}\nCreated: {}".format(name, type_string, date))
            print("Level structure is displayed as [number_of_people_in_level, threshold]:")
            for i in range(1, len(lines)):
                print("Level {} structure is: [{}]".format(i, lines[i]))


# check if given String is either "True", "true" or 1/"1"
# return True if so, else False
def str2bool(string_representation):
    return str(string_representation.lower()) in ("true", "1")
