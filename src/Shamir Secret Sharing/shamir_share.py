import os
import sys
sys.path.append(os.pardir)
from function_tools import generate_function, calc_function, is_prime, print_function
from lagrange_interpolation import reconstruct
from read_and_write_data import write_shares
from path import get_data_path_sss
import os
import random
import yaml

# path to DATA/SSS directory
data_path = get_data_path_sss()

random.seed(42)


# generate a random function and compute share-values for participating shareholders
def make_random_shares(minimum_number_of_shares, number_of_people, message, field_size):
    # create new directory to store the data in
    file_path = os.path.join(data_path, "{},{}".format(minimum_number_of_shares, number_of_people))
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
    try:
        os.mkdir(file_path)
    except OSError as e:
        pass
    if minimum_number_of_shares > number_of_people:
        raise ValueError("pool secret would be irrecoverable")
    # generate random polynomial with secret as free coefficient
    polynomial = generate_function(minimum_number_of_shares - 1, message, field_size)
    shares = {}
    # calculate shares for all shareholders
    for i in range(1, number_of_people + 1):
        shares[i] = calc_function(polynomial, i, field_size)
    # write computed shares to file
    write_shares(field_size, os.path.join(file_path, "shares.csv"), shares)
    return polynomial[0][0], polynomial, shares


def main():
    field_size = 997
    with open("shamir_setups.yaml", 'r') as stream:
        try:
            docs = yaml.load_all(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)
        for doc in docs:
            setup = doc['setup']
            info = setup.split(',')
            minimum_number_of_shares = int(info[0])
            number_of_people = int(info[1])
            random_message = random.randint(0, field_size - 1)
            secret, polynomial, shares = make_random_shares(minimum_number_of_shares=minimum_number_of_shares,
                                                number_of_people=number_of_people, message=random_message,
                                                field_size=field_size)
            print("Setup", setup)
            print('secret:\t\t\t', secret)
            print('shares:', shares)
            print("f(x) =", print_function(polynomial, False))
            reconstructed = reconstruct(setup, shares, field_size)
            print('secret recovered:\t', reconstructed)
            assert (reconstructed == random_message), "Incorrect reconstruction"
            print("Reconstruction successful")


if __name__ == '__main__':
    main()