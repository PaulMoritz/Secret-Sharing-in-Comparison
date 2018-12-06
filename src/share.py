import os
import copy
from function_tools import derive_function, generate_function, calc_function, print_function, is_prime
from read_and_write_data import write_shares, read_level_stats
from reconstruction_tools import calc_derivative_vector
import numpy as np


# path to DATA directory
cwd = os.getcwd()
main_directory = os.path.abspath(os.path.join(cwd, os.pardir))
data_path = os.path.join(main_directory, "DATA")

# seed for testing only! unsafe otherwise
# np.random.seed(42)


# creates shares for all Shareholders in one setup
# needs a message (Integer), a setup and an optional prime number for the finite field
def share(setup, message, field_size=31, name="", print_statements=True):
    file_path = os.path.join(data_path, setup, 'level_stats.csv')
    # make sure number is in finite field
    if message > field_size:
        old_message = message
        message = message % field_size
        print("Due to the size of the finite field ({}), the secret was changed to {} ({} % {}).\n"
              .format(field_size, message, old_message, field_size))
    # check for prime as secret message
    if not is_prime(field_size):
        raise ValueError("Given prime_number is not a prime.")
    # error handling (no integer given)
    if not isinstance(message, int):
        raise TypeError("Secret needs to be an integer.")
    # if setup exists, read all needed data
    try:
        list_of_people_per_level, thresholds = read_level_stats(file_path)
    except FileNotFoundError as e:
        print("Setup does not exist. {}".format(e))
        raise
    # more error handling
    for i in range(len(thresholds) - 1):
        if not thresholds[i] <= thresholds[i + 1]:
            raise ValueError("Wrong setup for conjunctive structure: threshold for "
                             "level i must always be bigger than threshold(level i-1).")
    # for conjunctive setup, get the maximum degree of the function to generate
    degree_of_function = thresholds[-1] - 1
    # generate random coefficients c for 0 < c <= prime and a function of those
    coefficients = generate_function(degree_of_function, message, field_size)
    original_function = copy.deepcopy(coefficients)
    print("The randomly generated function is  \t", end='')
    print_function(coefficients)
    derivatives = calc_derivative_vector(coefficients, (thresholds[-1] - 1), field_size)
    # create a dict of shareholder:value pairs
    share_dict = {}
    # needed to check if the function needs to be derived
    old_j = 0
    person_number = 1
    for level, number in enumerate(list_of_people_per_level):
        # we need to derive only if we calculate values for a new level
        j = int(thresholds[level])
        while j > old_j:
            # if threshold is bigger than current j, we need to derive n times
            # to get the correct derivative to work with
            old_j += 1
            if print_statements:
                print("The {}. derivative of the function is \t{}"
                      .format(old_j, print_function(derivatives[old_j], printed=False)))
        current_function = derivatives[j]
        # calculate values and append to the share_dict dict for each shareholder
        for person in range(1, int(number) + 1):
            shareholder = ("s_{}_{}".format(person_number, thresholds[level]))
            if person == 1 and print_statements:
                print("With this function we calculate shares for the following shareholders:")
            # calculate the value for the shareholder
            result = calc_function(current_function, person_number, field_size)
            person_number += 1
            if print_statements:
                print("Shareholder {}'s share is {}".format(shareholder, result))
            share_dict[shareholder] = result
    if print_statements:
        # print the dict to the screen
        print("New shares are: {}".format(share_dict))
    # write Shares to 'shares.csv' and save it in the setups directory
    try:
        if name:
            write_shares(field_size, os.path.join(data_path, setup, "shares_{}.csv".format(name)), share_dict)
            print("Shares are saved to folder 'DATA/{}/shares_{}.csv'. Please don't edit the csv file manually."
                  .format(setup, name))
        else:
            write_shares(field_size, os.path.join(data_path, setup, "shares.csv"), share_dict)
            print("Shares are saved to folder 'DATA/{}/shares.csv'. Please don't edit the csv file manually."
                  .format(setup))
    # error handling
    except PermissionError as e:
        print("Can't write to '{}', maybe try to close the file and try again. \n {}".format(file_path, repr(e)))
        raise
    return original_function, share_dict
