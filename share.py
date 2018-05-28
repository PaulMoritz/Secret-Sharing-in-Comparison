import os
import numpy as np
import pandas as pd
import csv
from math import pow


#
# TODO: delete testcases
#

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")


# creates shares for all Shareholders in one setup
# needs a message (Integer), a setup and an optional prime number for the finite field
def share(message, setup, prime_number=31):
    filepath = os.path.join(datapath, setup, 'info.csv')
    data = pd.read_csv(filepath, delimiter=',', )
    # create list of number of people in each level
    num = list(data.iloc[4:, 0])
    # create list of thresholds
    thresholds = list(data.iloc[4:, 1])
    highest_threshold = max(thresholds)
    if not highest_threshold == thresholds[-1]:
        print("Wrong setup for conjunctive structure: threshold for"
              "level i must always be bigger than threshold(level i-1).")
        return
    degree_of_function = int(highest_threshold) - 1
    # calc number of levels
    # get the number of all shareholders
    # generate random coefficients for 0 < c <= prime
    coefficients = generate_function(degree_of_function, message, prime_number)
    share_list = {}
    # create a dict of shareholder:value pairs
    for level, number in enumerate(num):
        for person in range(1, int(number) + 1):
            shareholder = ("s_{}_{}".format(person, level))
            if person == 1:
                new_level = True
            else:
                new_level = False
            result = calc_function(coefficients, level, person, new_level, prime_number)
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
    return coefficients


# derivates the given function in place (modulo the prime)
# for each pair of coefficients te normal derivation rules apply
# (factor = factor * exponent,
#  exponent = exponent -1)
def derivate_function(function_to_derivate, prime_number):
    for level in function_to_derivate:
        # TODO Modulo here?
        level[0] = (level[0] * level[1]) % prime_number
        # catch x^0, don't subtract exponent here
        if level[1] > 0:
            level[1] -= 1
        else:
            pass
    return function_to_derivate


# calculate the y- values for each shareholder with their given x
# new_level is set when the result for the first person from a level is calculated
# ASSUMING we only calculate the results in ascending order of Level/Person
def calc_function(coeff_list, level, x, new_level, prime_number):
    if level > 0 and new_level:
        return calc_function(derivate_function(coeff_list, prime_number), level - 1, x, True, prime_number)
    else:
        result = 0
        for coefficient in coeff_list:
            result = (result + (coefficient[0] * pow(x, coefficient[1])) % prime_number) % prime_number
        return int((result % prime_number))


# share(3, "example")
# derivate_function([[3, 0], [27, 1], [16, 2], [18, 3], [7, 4]], 31)
