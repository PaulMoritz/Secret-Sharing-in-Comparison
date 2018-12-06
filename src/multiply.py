from multiply_tools import *
from linear import linear
from reconstruction_tools import shareholder_share_list_to_lists
from read_and_write_data import  read_data
import numpy as np


def multiply(setup, m_1, m_2, computed_shares):
    field_size = read_field_size(setup)
    data, _, thresholds = read_data(setup)
    t = thresholds[-1]
    shareholder_ids = [tuple(x) for x in data.values]
    person_ids, vector_of_shares = shareholder_share_list_to_lists(shareholder_ids)
    delta_shares = {}
    epsilon_shares = {}
    for i, shareholder in enumerate(person_ids):
        delta_i_j, epsilon_i_j = compute_delta_epsilon(setup, m_1, m_2, computed_shares[i], field_size)
        delta_shares["s_{}_{}".format(shareholder[0], shareholder[1])] = delta_i_j
        epsilon_shares["s_{}_{}".format(shareholder[0], shareholder[1])] = epsilon_i_j
    delta, _, _, _, _ = reconstruct(setup, random_subset=False, subset=delta_shares)
    epsilon, _, _, _, _ = reconstruct(setup, random_subset=False, subset=epsilon_shares)
    message_shares = {}
    for i, shareholder in enumerate(person_ids):
        message_shares["s_{}_{}".format(shareholder[0], shareholder[1])] =\
            linear([(1, computed_shares[i][2]), (epsilon, m_1), (delta, m_2), (-delta, epsilon)], field_size)
    print(message_shares)


def compute_delta_epsilon(setup, m_1, m_2, computed_shares, field_size):
    share_delta = linear([(1, m_1), (-1, computed_shares[0])], field_size)
    share_epsilon = linear([(1, m_2), (-1, computed_shares[1])], field_size)
    return share_delta, share_epsilon





multiply("1,2", 3, 5, )