import numpy as np
import os
import shutil
import time
import csv

#
# TODO: more comments!
#

cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")

# deletes the folder and all its files if a directory with the given name exists
def delete_setup(name):
    filepath = os.path.join(cwd, "DATA", name)
    if os.path.exists(filepath):
        shutil.rmtree(filepath)
        print("Setup deleted.")
    else:
        print("Name does not exist.")


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
        print("Name \"" + name + "\" already exists. Please choose another.")
        return
    # more troubleshooting with input parameters
    for level in lvl_list:
        if level.__len__() != 2:
            print("""Wrong number of Arguments in lvl_list: list of level with length """ + str(level.__len__()) + """ found.
lvl_list must be of Format [[num_level_1, threshold_level_1],[num_level_2, treshold_level_2],....]""")
            return
        for element in level:
            if not isinstance(element, int):
                print("Error: Non-Integer value as level/threshold.")
                return
    os.mkdir(filepath)
    created = str(time.strftime("%d.%m.%Y at %H:%M:%S"))
    with open(os.path.join(filepath, "info.csv"), 'w+', newline ='', encoding ='utf8') as file:
        writer = csv.writer(file,delimiter=',')
        metadata =[['Name', name], ['Created', created], ["Conjunctive?",conjunctive], [''],["number of people", "threshold"] ]
        writer.writerows(metadata)
        writer.writerows(lvl_list)
    print("Setup \"" + name +"\" successfully created!")


def get_info(name):
    filepath = os.path.join(cwd, "DATA", name, 'info.txt')
    if not os.path.exists(filepath):
        print("Setup does not exist.")
        return
    with open(filepath, 'r') as infofile:
        # get name
        name = infofile.readline()
        # get Con/Disjuntive
        conjunctive = infofile.readline()
        if conjunctive:
            type_string = 'Conjunctive'
        else:
            type_string = 'Disjunctive'
        # get creation date
        date = infofile.readline()
        i=0
        lines = infofile.read().splitlines()
        #Print all level-Info:
        print("Name: " + name + '\n' + "Type: " + type_string + '\n' + "Created: " + date)
        print("Level strucure is displayed as [num_people, treshold]")
        for i in range(lines.__len__()):
            print("Level " + str(i+1) + " structure is: " + str(lines[i]))

#delete_setup("Big_Company")
#setup("Big_Company", [[1,0],[3,2],[7,4],[35,10]], True)