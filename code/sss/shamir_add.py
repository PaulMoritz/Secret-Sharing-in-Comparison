import random
import numpy as np
import pandas as pd
import os
import sys
hss = os.path.join(os.pardir, "hss")
sys.path.append(hss)
from path import get_data_path_sss
from reconstruction_tools import divide
from sharing_exceptions import *
from add_tools import split_value
from read_and_write_data import create_add_file, read_field_size


def shamir_add(setup, old_shares, new_shareholder_id, print_statements=True):
    field_size, k, shareholders = get_info(setup)
    # if we have more share info than necessary, reduce subset to a minimal one
    # to prevent computation errors
    reconstruction_shares = find_random_minimum_subset(k, old_shares, print_statements)
    # make sure new id is indeed non existent yet
    for shareholder in shareholders:
        if int(shareholder[0]) == new_shareholder_id:
            raise InvalidShareholderException("ID already exists")
    participating_ids = [int(shareholder_id) for shareholder_id in reconstruction_shares]
    # calculation of splitted sub-shares after applying the formula
    results = calculate_results_add(field_size, new_shareholder_id, participating_ids, print_statements,
                                    reconstruction_shares)
    # sum over columns -> all received parts for each shareholder
    sums = np.sum(results, axis=0)
    for i, element in enumerate(sums):
        sums[i] = int(element) % field_size
    # sum over all computed sigmas (the sums of parts) to get share-value for new shareholder
    new_share = np.sum(sums, axis=0) % field_size
    shareholders.append((new_shareholder_id, new_share))
    print(shareholders)
    shareholders_after_add = {}
    for shareholder in shareholders:
        shareholders_after_add[shareholder[0]] = shareholder[1]
    print(shareholders_after_add)
    if print_statements:
        print("New share for shareholder s_{} is {}".format(new_shareholder_id, new_share))
    create_add_file(field_size, 0, shareholders, setup, hierarchical=False)
    return new_share, shareholders_after_add


def calculate_results_add(field_size, new_shareholder_id, participating_ids, print_statements, reconstruction_shares):
    results = []
    for shareholder in reconstruction_shares:
        shareholder_id = int(shareholder)
        share = reconstruction_shares[shareholder]
        gamma_i = compute_interpolation_constant(shareholder_id, new_shareholder_id, participating_ids, field_size)
        result_i = (share * gamma_i) % field_size
        if print_statements:
            print("Shareholder s_{}:\nResulting gamma {}\nResulting number (gamma*share) {}"
                  .format(shareholder_id, gamma_i, result_i))
        # split result into r parts
        r = len(reconstruction_shares)
        splitted = split_value(result_i, r)
        results.append(splitted)
    return results


def find_random_minimum_subset(k, old_shares, print_statements):
    if len(old_shares) > k:
        reconstruction_shares = choose_random_subset(old_shares, k)
        if print_statements:
            print("Choosing random minimum valid subset of given shares.\n"
                  "Subset is {}".format(reconstruction_shares))
    else:
        reconstruction_shares = old_shares
        if print_statements:
            print("Set of given shares is {}".format(reconstruction_shares))
    return reconstruction_shares


def get_info(setup):
    shareholders = read_shares(setup)
    print(shareholders)
    field_size = read_field_size(setup, hierarchical=False)
    # degree of function
    k, n = setup.split(',')
    k, n = int(k), int(n)
    return field_size, k, shareholders


# participating_ids: i values of all IDs who are involved in the add
def compute_interpolation_constant(i, k, participating_ids, field_size):
    gamma_i = 1
    for j in participating_ids:
        if j != i:
            gamma_i = (gamma_i * divide((k - j) % field_size, (i - j) % field_size, field_size)) % field_size
    return gamma_i


def read_shares(setup):
    data_path = get_data_path_sss()
    file_path = os.path.join(data_path, setup, 'shares.csv')
    data = pd.read_csv(file_path, skiprows=1, header=None, delimiter=',', )
    # create list of number of people in each level
    id = list(data.iloc[:, 0])
    shares = list(data.iloc[:, 1])
    zipped = zip(id, shares)
    return list(zipped)


def choose_random_subset(shares, number):
    subset_ids = random.sample(list(shares), number)
    subset = {}
    for subset_id in subset_ids:
        subset[subset_id] = shares[subset_id]
    return subset


def list_of_shares_to_dict(shares):
    all_shares = {}
    tuples = [tuple(x) for x in shares.values]
    for (x, y) in tuples:
        all_shares[x] = y
    return all_shares


# sub =choose_random_subset({'1': 435, '2':632, '3':70}, 2)
# print(sub)
# add('2,3', {'1': 197, '2': 632, '3': 70}, 4, 997)
