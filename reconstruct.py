import os
from tools import *
import pandas as pd
import random

#
# All Requirements taken from Traverso, G., Demirel, D, Buchmann, J: Dynamic and Verifiable Hierarchical Secret Sharing
#


# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")


# reconstruct a secret with a given subset of people, only if
# all thresholds are satisfied and
# all requirements for a unique solution are given.
# setup             String  the setup name to reconstruct the secret from
# number_of people  Integer number of participating people in the subset, chosen randomly
def reconstruct(setup, number_of_people):
    # read the list and extract shareholder information
    shares = []
    person_IDs = []
    functions_involved = []
    try:
        filepath = os.path.join(datapath, setup, 'shares.csv')
        data = pd.read_csv(filepath, skiprows=0, header=None, delimiter=',', )
        field_size = data[1][0]
    except FileNotFoundError:
        print("Shares for setup '{}' not yet created.".format(setup))
        return
    # read data of shareholders into tuples
    tuples = [tuple(x) for x in data.values[2:]]
    print("All given shareholders: {}".format(tuples))
    # select a random sample of given shareholders
    share_list = random.sample(tuples, number_of_people)
    print("Subset of {} shareholders randomly selected is {}.".format(number_of_people, share_list))
    # TODO compare input to shares from given setup?!
    for i, shareholder in enumerate(share_list):
        name = shareholder[0].split('_')
        name = name[1:]
        functions_involved.append(name[1])
        shares.append(shareholder[1])

        person_IDs.append((name[0], name[1]))
    print("Coordinates are {}".format(person_IDs))

    phi = sorted(set(functions_involved))
    print("Share value column for interpolation is {}".format(shares))
    print("Vector phi of function x^i with i printed is {}".format(phi))
    matrix, max_person_number, highest_derivative = interpolation_matrix(person_IDs)
    print("\nChecking thresholds:")
    if not thresholds_fulfilled(setup, person_IDs):
        return
    if requirement_1(matrix, highest_derivative, len(share_list)):
        print("Requirement 1 'Unique Solution' is satisfied.")
    else:
        print("Requirement 1 'Unique Solution' not satisfied with given subset.")
        return
    if supported_sequence(matrix):
        print("Requirement 1 'No supported 1-sequence of odd length' is satisfied.")
    else:
        print("Requirement 1 'No supported 1-sequence of odd length' not satisfied with given subset.")
        return
    if requirement_2(highest_derivative, field_size, max_person_number):
        print("Requirement 2 'Unique solution over finite field of size {}' is satisfied.".format(field_size))
    else:
        print("Requirement 2 'Unique solution over finite field of size {}'"
              "not satisfied with given subset.".format(field_size))
        return
    print("\nAll requirements for a unique solution are given, starting interpolation...")


# check for each given threshold from the setup if it is satisfied by the subset of shareholders
# return True if all thresholds stand, else return False
def thresholds_fulfilled(setup, person_IDs):
    filepath = os.path.join(datapath, setup, 'level_stats.csv')
    thresholds = []
    count_of_persons = 0
    try:
        data = pd.read_csv(filepath, skiprows=1, header=None, delimiter=',')
        thresholds = data[1].values
    except FileNotFoundError as e:
        print(e)
    for number_of_level, item in enumerate(thresholds):
        for person in person_IDs:
            if int(person[1]) == number_of_level:
                count_of_persons += 1
        if count_of_persons < int(item):
            print("Threshold {} not fulfilled, the subset contains only {} people up to this level."
                  "(Should be at least {})".format(number_of_level, count_of_persons, item))
            return False
        else:
            print("Threshold {} fulfilled.".format(number_of_level))
    return True


# reconstruct("another_example1", 4)
