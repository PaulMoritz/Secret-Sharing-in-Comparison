import os
from function_tools import derive_function, generate_function, calc_function, print_function, is_prime
from share_tools import *


# path to DATA directory
cwd = os.getcwd()
main_directory = os.path.abspath(os.path.join(cwd, os.pardir))
data_path = os.path.join(main_directory, "DATA")

# seed for testing only! unsafe otherwise
# np.random.seed(531)


# creates shares for all Shareholders in one setup
# needs a message (Integer), a setup and an optional prime number for the finite field
def share(setup, message, prime_number=31, name=""):
    file_path = os.path.join(data_path, setup, 'level_stats.csv')
    # make sure number is in finite field
    if message > prime_number:
        message = message % prime_number
        print("Due to the size of the finite field ({}), the secret was changed to {}.\n"
              .format(prime_number, message))
    # check for prime as secret message
    if not is_prime(prime_number):
        print("Given prime_number is not a prime.")
        return
    # error handling (no integer given)
    if not isinstance(message, int):
        print("Secret needs to be an integer.")
        return
    # if setup exists, read all needed data
    try:
        list_of_people_per_level, thresholds = read_level_stats(file_path)
    except FileNotFoundError as e:
        print("Setup does not exist. {}".format(e))
        return
    # more error handling
    for i in range(len(thresholds) - 1):
        if not thresholds[i] <= thresholds[i + 1]:
            print("Wrong setup for conjunctive structure: threshold for "
                  "level i must always be bigger than threshold(level i-1).")
            return
    # for conjunctive setup, get the maximum degree of the function to generate
    degree_of_function = thresholds[-1] - 1
    # generate random coefficients c for 0 < c <= prime and a function of those
    coefficients = generate_function(degree_of_function, message, prime_number)
    print("The randomly generated function is  \t", end='')
    print_function(coefficients)
    print("With this function we calculate shares for the following shareholders:")
    # create a dict of shareholder:value pairs
    share_list = {}
    # needed to check if the function needs to be derived
    old_j = 0
    for level, number in enumerate(list_of_people_per_level):
        # we need to derive only if we calculate values for a new level
        j = int(thresholds[level])
        print("Level " + str(old_j) + " shareholder's shares are: s_i_" + str(j))
        while j > old_j:
            # if threshold is bigger than current j, we need to derive n times
            # to get the correct derivative to work with
            derive_function(coefficients, prime_number)
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
    # print the dict to the screen
    print("New shares are: {}".format(share_list))
    # write Shares to 'shares.csv' and save it in the setups directory
    try:
        if name:
            write_shares(prime_number, os.path.join(data_path, setup, "shares_{}.csv".format(name)), share_list)
            print("Shares are saved to folder 'DATA/{}/shares_{}.csv'. Please don't edit the csv file manually."
                  .format(setup, name))
        else:
            write_shares(prime_number, os.path.join(data_path, setup, "shares.csv"), share_list)
            print("Shares are saved to folder 'DATA/{}/shares.csv'. Please don't edit the csv file manually."
                  .format(setup))
    # error handling
    except PermissionError as e:
        print("Can't write to '{}', maybe try to close the file and try again. \n {}".format(file_path, repr(e)))
