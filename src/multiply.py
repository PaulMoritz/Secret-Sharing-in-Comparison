from multiply_tools import *
from linear import linear
from reconstruction_tools import shareholder_share_list_to_lists, dict_to_list
from read_and_write_data import read_data
from function_tools import print_function
import numpy as np


def multiply(setup, messages):
    field_size = read_field_size(setup)
    data, _, thresholds = read_data(setup)
    t = thresholds[-1]
    shareholder_ids = [tuple(x) for x in data.values]
    person_ids, vector_of_shares = shareholder_share_list_to_lists(shareholder_ids)
    triple, shareholders_, alpha_s, beta_s = pre_mult(setup)
    computed_shares = []
    for i, shareholder in enumerate(person_ids):
        computed_shares.append(dict_to_list(triple)[i][1])
    print(computed_shares)
    delta_shares = {}
    epsilon_shares = {}
    for i, shareholder in enumerate(person_ids):

        delta_i_j, epsilon_i_j = compute_delta_epsilon(messages[shareholder][0], messages[shareholder][1], computed_shares[i], field_size)
        delta_shares["s_{}_{}".format(shareholder[0], shareholder[1])] = delta_i_j
        epsilon_shares["s_{}_{}".format(shareholder[0], shareholder[1])] = epsilon_i_j
    print("delta shares", delta_shares, "\n epsilon shares", epsilon_shares)
    delta, _, _, _, _ = reconstruct(setup, random_subset=False, subset=delta_shares, print_statements=False)
    epsilon, _, _, _, _ = reconstruct(setup, random_subset=False, subset=epsilon_shares, print_statements=False)
    print(delta, epsilon)
    message_shares = {}
    for i, shareholder in enumerate(person_ids):
        message_shares["s_{}_{}".format(shareholder[0], shareholder[1])] =\
            linear([(1, computed_shares[i][2]), (epsilon, messages[shareholder][0]), (delta, messages[shareholder][1]), (-delta, epsilon)], field_size)
    print(message_shares)
    m, polynomial, _, _, _ = reconstruct(setup, random_subset=False, subset=message_shares, print_statements=False)
    print(m, print_function(polynomial, False))


def compute_delta_epsilon(m_1, m_2, computed_shares, field_size):
    share_delta = linear([(1, m_1), (-1, computed_shares[0])], field_size)
    share_epsilon = linear([(1, m_2), (-1, computed_shares[1])], field_size)
    print(share_delta, share_epsilon)
    return share_delta, share_epsilon


multiply("1,2,3", {(1, 0): (541, 138), (2, 1): (845, 943), (3, 2): (870, 540)})