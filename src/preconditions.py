import math
import os
import pandas as pd
#
# All Requirements taken from Traverso, G., Demirel, D, Buchmann, J: Dynamic and Verifiable Hierarchical Secret Sharing
#

# path to DATA directory
cwd = os.getcwd()
main_directory = os.path.abspath(os.path.join(cwd, os.pardir))
data_path = os.path.join(main_directory, "DATA")


# Requirement 1 from the Appendix (Theorem 3 in Paper)
def requirement_1(matrix, highest_derivative, number_of_points):
    # "For all k..."
    for k in range(highest_derivative + 1):
        sum_over_matrix = 0
        # outer sum
        for j in range(k + 1):
            # inner sum
            for i in range(1, number_of_points+1):
                sum_over_matrix += matrix[i-1][j]
        if not sum_over_matrix >= k + 1:
            return False
    return True


# check for a supported 1-sequence of odd length/ second part of the first requirement as stated in Theorem 3
def supported_sequence(matrix):
    max_sequence = 0
    column = 0
    for i, row in enumerate(matrix):
        row_sequence_head = 0
        in_one_sequence = False
        number_of_ones = 0
        head = 0
        for j, element in enumerate(row):
            # start counting, set variables
            if element == 1:
                number_of_ones += 1
                if not in_one_sequence:
                    in_one_sequence = True
                    head = j
                # end of row -> sequence finished
                if j == len(row) - 1:
                    if number_of_ones > max_sequence:
                        row_sequence_head = head
                        max_sequence = number_of_ones
                        number_of_ones = 0
                        column = i
            else:
                # not (anymore) in sequence, if we were, set variables
                if in_one_sequence:
                    in_one_sequence = False
                    if number_of_ones > max_sequence:
                        row_sequence_head = head
                        max_sequence = number_of_ones
                        column = i
                number_of_ones = 0
        # after maximal sequence is found, check if it is of odd length, if yes, check if it supported
    if max_sequence % 2:
        if check_supported(matrix, column, row_sequence_head):
            return True
    return False


# check for a 1-sequence if it is supported (Definition 6)
def check_supported(matrix, j, i):
    nw, sw = False, False
    for row_num, row in enumerate(matrix):
        # check for south-west support
        if row_num < i:
            for index, element in enumerate(row):
                if index < j:
                    if element == 1:
                        sw = True
        # check for north-west support
        if row_num > i:
            for index, element in enumerate(row):
                if index < j:
                    if element == 1:
                        nw = True
    # if both are given, return True
    if nw and sw:
        return True
    return False


# Requirement 2 from the Appendix (Theorem 4)
def requirement_2(d, q, max_pers_num):
    # print(d, q, max_pers_num)
    res = 2**(- d + 2) * (d - 1)**((d - 1)/2) * math.factorial(d - 1) * max_pers_num**(((d - 1)*(d - 2))/2)
    # print(res)
    if not float(q) > res:
        return False
    return True


# checks for each given threshold from the setup if it is satisfied by the subset of shareholders
# returns True if all thresholds stand, else returns False
def thresholds_fulfilled(setup, person_IDs, print_statements):
    file_path = os.path.join(data_path, setup, 'level_stats.csv')
    thresholds = []
    count_of_persons = 0
    try:
        # read the thresholds from data
        data = pd.read_csv(file_path, skiprows=1, header=None, delimiter=',')
        thresholds = data[1].values
    except FileNotFoundError as e:
        print(repr(e))
        raise
    # For each threshold check if enough people are available
    th = list(thresholds)
    # insert t[-1] = 0 as start
    th.insert(0, 0)
    for number_of_level, item in enumerate(th):
        if number_of_level == len(th) - 1:
            break
        for person in person_IDs:
            # if person belongs to level, increase count
            if int(person[1]) == int(item):
                count_of_persons += 1
        # after all persons are viewed, if there are less than the threshold, break
        if count_of_persons < th[number_of_level + 1]:
            print("Threshold {} not fulfilled, the subset contains only {} people up to this level."
                  "(Should be at least {})".format(number_of_level, count_of_persons, th[number_of_level + 1]))
            return False
        else:
            if print_statements:
                print("Threshold t_{} fulfilled.".format(number_of_level + 1))
    # return true only if all thresholds are fulfilled
    return True
