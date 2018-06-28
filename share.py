import os
import pandas as pd
import csv
from function_tools import *

#
# TODO: delete testcases, delete unnecessary prints
#

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")

# seed for testing only! unsafe otherwise
# np.random.seed(4)


# creates shares for all Shareholders in one setup
# needs a message (Integer), a setup and an optional prime number for the finite field
def share(message, setup, prime_number=31):
    filepath = os.path.join(datapath, setup, 'level_stats.csv')
    if not is_prime(prime_number):
        print("Given prime_number is not a prime.")
        return
    message = message % prime_number
    if not isinstance(message, int):
        print("Secret needs to be an integer.")
        return
    try:
        data = pd.read_csv(filepath, skiprows=1, header=None, delimiter=',', )
    except FileNotFoundError as e:
        print("Setup or level statistics doy not exist: {}".format(repr(e)))
        return
    # create list of number of people in each level
    num = list(data.iloc[:, 0])
    print("Read people from levels: " + str(num))
    # create list of thresholds
    thresholds = list(data.iloc[:, 1])
    print("Read thresholds " + str(thresholds))
    highest_threshold = thresholds[-1]
    for i in range(len(thresholds) - 1):
        if not thresholds[i] < thresholds[i + 1]:
            print("Wrong setup for conjunctive structure: threshold for "
                  "level i must always be bigger than threshold(level i-1). \n"
                  "Here: thresholds[{}] = {} > {} = thresholds[{}]".format(i, thresholds[i], thresholds[i + 1], i + 1))
            return
    degree_of_function = int(highest_threshold) - 1
    # calc number of levels
    # get the number of all shareholders
    # generate random coefficients for 0 < c <= prime
    coefficients = generate_function(degree_of_function, message, prime_number)
    print("The randomly generated function is  \t", end='')
    print_function(coefficients)
    print("With this function we calculate shares for the following shareholders:")
    # dict of shareholders and their secrets
    share_list = {}
    old_j = 0
    # create a dict of shareholder:value pairs
    for level, number in enumerate(num):
        # we need to derivate only if we calculate values for a new level
        j = int(thresholds[level])-1
        # print("j is " + str(j))
        # print("Level " + str(old_j) + " shareholder's shares are: s_i_" + str(j))
        while j > old_j:
            derivate_function(coefficients, prime_number)
            old_j += 1
            print("The " + str(old_j) + ". derivative of the function is \t", end='')
            print_function(coefficients)
        # calculate values and append to the share_list dict for each shareholder
        for person in range(1, int(number) + 1):
            shareholder = ("s_{}_{}".format(person, number - 2))
            if person == 1:
                print("With this function we calculate shares for the following shareholders:")
            # calculate the value for the shareholder
            result = calc_function(coefficients, person, prime_number)
            print("Shareholder {}'s share is {}".format(shareholder, result))
            share_list[shareholder] = result
    print("New shares are: {}".format(share_list))

    # write Shares to 'shares.csv' and save it in the setups directory
    try:
        with open(os.path.join(datapath, setup, "shares.csv"), "w", newline='', encoding="utf8") as shares:
            writer = csv.writer(shares)
            writer.writerow(["Chosen finite field size", prime_number])
            writer.writerow(["Shareholder", "Share"])
            writer.writerows(share_list.items())
            print("Shares are saved to folder 'DATA/{}/shares.csv'."
                  "Please don't edit the csv file manually.".format(setup))
    except PermissionError as e:
        print("Can't write to '{}', please close the file and try again. \n {}".format(filepath, repr(e)))


share(1, "newer_test_example_setup", 71)
# derivate_function([[3, 0], [27, 1], [16, 2], [18, 3], [7, 4]], 31)
# print_function([[3, 0], [27, 1], [16, 2], [18, 3], [7, 4]])
