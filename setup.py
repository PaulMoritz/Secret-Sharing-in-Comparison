import numpy as np
import os
import shutil
import time


# deletes the folder and all its files if a directory with the given name exists
def delete_setup(name):
    cwd = os.getcwd()
    filepath = os.path.join(cwd, "DATA", name)
    if os.path.exists(filepath):
        shutil.rmtree(filepath)
        print("Setup deleted.")
    else:
        print("Name does not exist.")


def list_setups():
    cwd = os.getcwd()
    datapath = os.path.join(cwd, "DATA")
    print("Current setups are:")
    for subdir, dirs, files in os.walk(datapath):
        for directory in dirs:
            print(directory)


# builds a new setup with all given parameters and
# creates a directory in the DATA-path with an info file
def setup(name, lvl_list, conjunctive=True):
    # create path
    cwd = os.getcwd()
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
    file = open(os.path.join(filepath, "info.txt"), 'w+')
    file.write(name + "\n" + str(conjunctive) + "\n" + str(time.strftime("%d.%m.%Y at %H:%M:%S")) + "\n")
    for level in lvl_list:
        file.write(str(level) + "\n")
    print("Setup \"" + name +"\" successfully created!")
    file.close()

