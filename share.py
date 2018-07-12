import os
import csv
from function_tools import *
from share_tools import *

#
# TODO: delete testcases, delete unnecessary prints
#

# highest prime in range 32 bit:
highest_prime = 2147483647

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")

# seed for testing only! unsafe otherwise
# np.random.seed(531)
# 4 for problem


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
        list_of_people_per_level, thresholds = read_level_stats(filepath)
    except FileNotFoundError as e:
        print("Setup does not exist. {}".format(e))
        return
    for i in range(len(thresholds) - 1):
        if not thresholds[i] <= thresholds[i + 1]:
            print("Wrong setup for conjunctive structure: threshold for "
                  "level i must always be bigger than threshold(level i-1).")
            return
    degree_of_function = thresholds[-1] - 1
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
    for level, number in enumerate(list_of_people_per_level):
        # we need to derivate only if we calculate values for a new level
        j = int(thresholds[level])
        print("Level " + str(old_j) + " shareholder's shares are: s_i_" + str(j))
        while j > old_j:
            derivate_function(coefficients, prime_number)
            old_j += 1
            print("The " + str(old_j) + ". derivative of the function is \t", end='')
            print_function(coefficients)
        # calculate values and append to the share_list dict for each shareholder
        for person in range(1, int(number) + 1):
            shareholder = ("s_{}_{}".format(person, thresholds[level]))
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
            print("Shares are saved to folder 'DATA/{}/shares.csv'. Please don't edit the csv file manually."
                  .format(setup))
    except PermissionError as e:
        print("Can't write to '{}', maybe close the file and try again. \n {}".format(filepath, repr(e)))


share(42, "another_big_example", 71)  # 71 for problems

