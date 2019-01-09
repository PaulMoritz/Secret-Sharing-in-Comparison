import os
import random
import sys

hss = os.path.join(os.pardir, "HSS")
sys.path.append(hss)
from function_tools import generate_function, calc_function, is_prime
from read_and_write_data import write_shares
from setup import create_info_file
from path import get_data_path_sss

# path to DATA/SSS directory
data_path = get_data_path_sss()

random.seed(42)


# generate a random function and compute share-values for participating shareholders
def make_random_shares(minimum_number_of_shares, number_of_people, message, field_size):
    # create new directory to store the data in
    setup_name = "{},{}".format(minimum_number_of_shares, number_of_people)
    file_path = os.path.join(data_path, setup_name)
    message = check_preconditions(field_size, message)
    try:
        os.mkdir(file_path)
    except OSError as e:
        print("Could not create setup {}".format(file_path))
    if minimum_number_of_shares > number_of_people:
        raise ValueError("pool secret would be irrecoverable")
    # generate random polynomial with secret as free coefficient
    polynomial = generate_function(minimum_number_of_shares - 1, message, field_size)
    shares = {}
    # calculate shares for all shareholders
    for i in range(1, number_of_people + 1):
        shares[i] = calc_function(polynomial, i, field_size)
    create_info_file("-", file_path, [], setup_name, field_size, hierarchical=False)
    # write computed shares to file
    write_shares(field_size, os.path.join(file_path, "shares.csv"), shares)
    return polynomial[0][0], polynomial, shares


def check_preconditions(field_size, message):
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
    return message

