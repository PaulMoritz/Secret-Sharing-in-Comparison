import os
import numpy as np
import pandas as pd
import csv
from math import pow


#
# TODO: delete testcases, delete unnecessary prints
#

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")


# creates shares for all Shareholders in one setup
# needs a message (Integer), a setup and an optional prime number for the finite field
def share(message, setup, prime_number=31):
    filepath = os.path.join(datapath, setup, 'info.csv')
    message = message % prime_number
    try:
        data = pd.read_csv(filepath, delimiter=',', )
    except FileNotFoundError as e:
        print("Setup does not exist. " + str(e))
        return
    # create list of number of people in each level
    num = list(data.iloc[4:, 0])
    # create list of thresholds
    thresholds = list(data.iloc[:, 1])
    thresholds = thresholds[4:]
    # print(thresholds)
    highest_threshold = max(thresholds)
    if not highest_threshold == thresholds[-1]:
        print("Wrong setup for conjunctive structure: threshold for "
              "level i must always be bigger than threshold(level i-1).")
        return
    degree_of_function = int(highest_threshold) - 1
    # calc number of levels
    # get the number of all shareholders
    # generate random coefficients for 0 < c <= prime
    coefficients = generate_function(degree_of_function, message, prime_number)
    # dict of shareholders and their secrets
    share_list = {}
    old_level = 0
    # create a dict of shareholder:value pairs
    for level, number in enumerate(num):
        # we need to derivate only if we calculate values for a new level
        while level > old_level:
            derivate_function(coefficients, prime_number)
            old_level += 1
        # calculate values and append to the share_list dict for each shareholder
        for person in range(1, int(number) + 1):
            shareholder = ("s_{}_{}".format(person, level))
            # print(level)
            # calculate the value for the shareholder
            result = calc_function(coefficients, person, prime_number)
            share_list[shareholder] = result
    print(share_list)

    # write Shares to 'shares.csv' and save it in the setups directory
    with open(os.path.join(datapath, setup, "shares.csv"), "w", newline='', encoding="utf8") as shares:
        writer = csv.writer(shares)
        writer.writerow(["Shareholder", "Share"])
        writer.writerows(share_list.items())
        print("New Shares in folder 'DATA/" + setup + "/shares.csv' created.")


# generates coefficients for the function
# Format: [[a_0, 0], [a_1, 1, [a_2, 2] ...] for f(x) = a_0 *x^0 + a_1 *x^1 + a_2 *x^2....
# with a_0 = message
def generate_function(in_degree, message, prime_number):
    coefficients = [[message, 0]]
    for i in range(1, in_degree + 1):
        a_i = np.random.randint(1, prime_number)
        coefficients.append([a_i, i])
    # print("list" + str(coefficients))
    return coefficients


# derivates the given function in place (modulo the prime)
# for each pair of coefficients the normal derivation rules apply
# (factor = factor * exponent,
#  exponent = exponent -1)
def derivate_function(function_to_derivate, prime_number):
    for level in function_to_derivate:
        level[0] = (level[0] * level[1]) % prime_number
        # catch x^0, don't subtract exponent here
        if level[1] > 0:
            level[1] -= 1
        else:
            pass
    return function_to_derivate


# calculate the y- values for each shareholder with their given x
def calc_function(coeff_list, x, prime_number):
    # print(coeff_list)
    result = 0
    for coefficient in coeff_list:
        result = (result + (coefficient[0] * pow(x, coefficient[1])) % prime_number) % prime_number
    # print(result % prime_number)
    return int((result % prime_number))


# share(1, "zeros")
# derivate_function([[3, 0], [27, 1], [16, 2], [18, 3], [7, 4]], 31)
