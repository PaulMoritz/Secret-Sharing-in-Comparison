import numpy as np


# randomly split a given value into n parts, where n == number
# value     the value to split
# number    the number of parts to split into
def randomly_split(value, number):
    # delta-vector of splitted values
    deltas = []
    remainder = value
    for i in range(number):

        # if this is the last part, insert remainder
        if i + 1 == number:
            deltas.append(remainder)
        # else randomly choose the next part
        else:
            # randomly choose a number in the range 0 - remaining_value
            delta_i = np.random.randint(0, remainder)
            deltas.append(delta_i)
            remainder -= delta_i
    return deltas


# merge person-numbers and thresholds into a level structure
# persons       list of number of persons for each level
# thresholds    list of thresholds for each level
def merge_level_stats(persons, thresholds):
    # different length is not legal
    if not len(persons) == len(thresholds):
        raise ValueError("Wrong format for level structure, {} levels but {} thresholds given"
                         .format(len(persons), len(thresholds)))
    # iterate over lists and merge them
    else:
        merged_structure = []
        for i in range(len(persons)):
            merged_structure.append([persons[i], thresholds[i]])
    return merged_structure


def merge_data(people, thresholds):
    level_list = []
    if len(thresholds) == len(people):
        for i in range(len(thresholds)):
            level_list.append([people[i], thresholds[i]])
    else:
        raise Exception("Thresholds (length {}) and people (length {}) don't fit".format(len(thresholds), len(people)))
    return level_list
