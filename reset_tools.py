import random
import os
import re

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")


# create new shares for the reset randomly
#
# currently not used as reset is not working for non-quadratic matrices
#
def create_new_shares(number_of_shares, number_of_levels):
    shares = []
    for index in range(number_of_shares):
        shares.append("s_{}_{}".format(index, random.randint(0, number_of_levels)))
    shares = sorted(shares, key=lambda x: int(re.search(r'\d+$', x).group()))
    return shares


# check if all given shareholders also exist in the given data
# return True if all shares are valid, false otherwise
def shareholders_valid(data, shares):
    tuples = [tuple(x) for x in data.values[2:]]
    for share in shares:
        if share not in tuples:
            print("Could not find {} in the shares  {}.".format(share, tuples))
            return False
    return True


# make a list of all shareholders by a given level structure
# return this list and the maximum degree of the functions used later (biggest threshold -1)
#
# currently not used as reset is not working for non-quadratic matrices
#
def level_structure_to_id(shares):
    people_per_level = []
    thresholds = [0]
    list_of_new_shareholders = []
    for level in shares:
        people_per_level.append(level[0])
        thresholds.append(level[1])
    for level_index in range(len(people_per_level)):
        for person_number in range(people_per_level[level_index]):
            list_of_new_shareholders.append("s_{}_{}".format(person_number + 1, thresholds[level_index]))
    degree_of_function = thresholds[-1] - 1
    return list_of_new_shareholders, degree_of_function
