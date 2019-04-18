from multiply_tools import *
from linear import linear
from reconstruction_tools import shareholder_share_list_to_lists, dict_to_list
from read_and_write_data import read_data
from function_tools import print_function
import numpy as np


def multiply(setup, messages, print_statements=True):
    # get all data and call pre_mult to compute the triple of shares
    computed_triples, field_size, gamma_secret, person_ids = prepare_data(setup)
    if True:
        print("Computed triple from PreMult:", computed_triples)
    # create dictionaries for m1, m2, delta, epsilon to store their share values
    share_values = create_dictionaries(computed_triples, field_size, messages, person_ids)
    if print_statements:
        print("Shares for m_1, m_2:", get_shares('m_1', share_values), get_shares('m_2', share_values))
    # reconstruct delta and epsilon from their shares
    delta, _, _, _, _ = reconstruct(setup, random_subset=False, subset=get_shares('delta', share_values), print_statements=False)
    epsilon, _, _, _, _ = reconstruct(setup, random_subset=False, subset=get_shares('epsilon', share_values), print_statements=False)
    if print_statements:
        print("Delta:", delta, "Epsilon:", epsilon)
    message_shares = {}
    # each shareholder computes the share of their message m with the given formula
    for i, shareholder in enumerate(person_ids):
        message_shares["s_{}_{}".format(shareholder[0], shareholder[1])] =\
            linear([(1, computed_triples[i][2]), (epsilon, messages[shareholder][0]), (delta, messages[shareholder][1]), (-delta, epsilon)], field_size)
    if print_statements:
        print("Message shares m:", message_shares)
    m, polynomial, _, _, _ = reconstruct(setup, random_subset=False, subset=message_shares, print_statements=False)
    m1, _, _, _, _ = reconstruct(setup, random_subset=False, subset=get_shares('m_1', share_values), print_statements=False)
    m2, _, _, _, _ = reconstruct(setup, random_subset=False, subset=get_shares('m_2', share_values), print_statements=False)
    if not (gamma_secret + ((epsilon * m1) % field_size) + ((delta * m2) % field_size) - ((epsilon * delta)
            % field_size)) % field_size == (m1 * m2) % field_size:
        print("multiply doesn't reconstruct correctly: ",
              gamma_secret, "+", epsilon, "*", m1, "+", delta, "*", m2, "-", epsilon, "*", delta, "=",
              (gamma_secret + ((epsilon * m1) % field_size) + ((delta * m2) % field_size) - ((epsilon * delta)
              % field_size) % field_size) % field_size, "!=", m1, "*", m2)
        raise ArithmeticError
    elif print_statements:
        print("Shares of m computed correctly")
    return message_shares


# get the shares of one value from all shares, deciding with x
# x:            determines the value to filter for, m_1, m_2, delta or epsilon for all shareholders
def get_shares(x, all_shares):
    x_shares = {}
    # get correct position of all shares in the dictionary
    if x is 'm_1':
        i = 0
    elif x is 'm_2':
        i = 1
    elif x is 'delta':
        i = 2
    elif x is 'epsilon':
        i = 3
    else:
        raise ValueError("Specified type {} does not exist in share_values".format(x))
    for s_id in all_shares:
        x_shares[s_id] = all_shares[s_id][i]
    return x_shares


# create dictionaries with the shareholder as key and
def create_dictionaries(computed_triples, field_size, messages, person_ids):
    share_values = {}
    # compute shares for delta and epsilon for each shareholder
    for i, shareholder in enumerate(person_ids):
        delta_i_j, epsilon_i_j = compute_delta_epsilon(messages[shareholder][0], messages[shareholder][1],
                                                       computed_triples[i], field_size)
        # save all shares in one dict wit shareholder id as key
        share_values["s_{}_{}".format(shareholder[0], shareholder[1])] =\
            (messages[shareholder][0], messages[shareholder][1], delta_i_j, epsilon_i_j)
    return share_values


# get all needed information and preprocess shareholder data and pre_mult, such as the computed triple
def prepare_data(setup):
    field_size = read_field_size(setup)
    data, _, thresholds = read_data(setup)
    t = thresholds[-1]
    shareholder_ids = [tuple(x) for x in data.values]
    person_ids, vector_of_shares = shareholder_share_list_to_lists(shareholder_ids)
    triple, shareholders_, alpha_secret, beta_secret = test_pre_mult(setup)
    gamma_secret = (alpha_secret * beta_secret) % field_size
    computed_shares = []
    for i, shareholder in enumerate(person_ids):
        computed_shares.append(dict_to_list(triple)[i][1])
    return computed_shares, field_size, gamma_secret, person_ids


# get the shares of delta and epsilon by a linear calculation
def compute_delta_epsilon(m_1, m_2, computed_shares, field_size):
    share_delta = linear([(1, m_1), (-1, computed_shares[0])], field_size)
    share_epsilon = linear([(1, m_2), (-1, computed_shares[1])], field_size)
    # print(share_delta, share_epsilon, "<--")
    return share_delta, share_epsilon


# multiply("1,2,3", {(1, 0): (7, 13), (2, 1): (14, 22), (3, 2): (6, 8)})
