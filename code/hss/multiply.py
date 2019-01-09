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
    triple, shareholders_, alpha_secret, beta_secret = test_pre_mult(setup)
    gamma_secret = (alpha_secret * beta_secret) % field_size
    computed_shares = []
    for i, shareholder in enumerate(person_ids):
        computed_shares.append(dict_to_list(triple)[i][1])
    print("Computed triple from PreMult:", computed_shares)
    delta_shares = {}
    epsilon_shares = {}
    m_1_shares, m_2_shares = {}, {}
    for i, shareholder in enumerate(person_ids):
        m_1_shares["s_{}_{}".format(shareholder[0], shareholder[1])] = messages[shareholder][0]
        m_2_shares["s_{}_{}".format(shareholder[0], shareholder[1])] = messages[shareholder][1]
        delta_i_j, epsilon_i_j = compute_delta_epsilon(messages[shareholder][0], messages[shareholder][1],
                                                       computed_shares[i], field_size)
        delta_shares["s_{}_{}".format(shareholder[0], shareholder[1])] = delta_i_j
        epsilon_shares["s_{}_{}".format(shareholder[0], shareholder[1])] = epsilon_i_j
    print("Shares for m_1, m_2:", m_1_shares, m_2_shares)
    print("delta shares", delta_shares, "\nepsilon shares", epsilon_shares)
    delta, _, _, _, _ = reconstruct(setup, random_subset=False, subset=delta_shares, print_statements=False)
    epsilon, _, _, _, _ = reconstruct(setup, random_subset=False, subset=epsilon_shares, print_statements=False)
    print("Delta:", delta, "Epsilon:", epsilon)
    message_shares = {}
    for i, shareholder in enumerate(person_ids):
        message_shares["s_{}_{}".format(shareholder[0], shareholder[1])] =\
            linear([(1, computed_shares[i][2]), (epsilon, messages[shareholder][0]), (delta, messages[shareholder][1]), (-delta, epsilon)], field_size)
    print("Message shares m:", message_shares)
    m, polynomial, _, _, _ = reconstruct(setup, random_subset=False, subset=message_shares, print_statements=False)
    m1, _, _, _, _ = reconstruct(setup, random_subset=False, subset=m_1_shares, print_statements=False)
    m2, _, _, _, _ = reconstruct(setup, random_subset=False, subset=m_2_shares, print_statements=False)
    print(polynomial)
    if not (gamma_secret + ((epsilon * m1) % field_size) + ((delta * m2) % field_size) - ((epsilon * delta)
            % field_size)) % field_size == (m1 * m2) % field_size:
        print("multiply doesn't reconstruct correctly: ",
              gamma_secret, "+", epsilon, "*", m1, "+", delta, "*", m2, "-", epsilon, "*", delta, "=",
              (gamma_secret + ((epsilon * m1) % field_size) + ((delta * m2) % field_size) - ((epsilon * delta)
              % field_size) % field_size) % field_size, "!=", m1, "*", m2)
    else:
        print("Shares of m computed correctly")


def compute_delta_epsilon(m_1, m_2, computed_shares, field_size):
    share_delta = linear([(1, m_1), (-1, computed_shares[0])], field_size)
    share_epsilon = linear([(1, m_2), (-1, computed_shares[1])], field_size)
    # print(share_delta, share_epsilon, "<--")
    return share_delta, share_epsilon


# multiply("1,2,3", {(1, 0): (7, 13), (2, 1): (14, 22), (3, 2): (6, 8)})
