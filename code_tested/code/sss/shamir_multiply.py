from shamir_multiply_tools import *
from linear import linear
from lagrange_interpolation import reconstruct
from reconstruction_tools import shareholder_share_list_to_lists, dict_to_list
from read_and_write_data import read_data
from function_tools import print_function
import numpy as np


def multiply(setup, messages, print_statements=True):
    field_size = read_field_size(setup, hierarchical=False)
    shareholders = read_shares(setup, double=True)
    shareholder_ids = list(shareholder[0] for shareholder in shareholders)
    triple, s_alpha, s_beta = pre_mult(setup, print_statements)

    s_gamma = (s_alpha * s_beta) % field_size
    computed_shares = []
    for i, shareholder in enumerate(shareholder_ids):
        computed_shares.append(dict_to_list(triple)[i][1])
    if print_statements:
        print("Computed triples from PreMult:", computed_shares)
    delta_shares = {}
    epsilon_shares = {}
    m_1_shares, m_2_shares = {}, {}
    try:
        for i, shareholder in enumerate(shareholder_ids):
            m_1_shares[shareholder] = messages[shareholder][0]
            m_2_shares[shareholder] = messages[shareholder][1]
            delta_i_j, epsilon_i_j = compute_delta_epsilon(messages[shareholder][0], messages[shareholder][1],
                                                           computed_shares[i], field_size)
            delta_shares[shareholder] = delta_i_j
            epsilon_shares[shareholder] = epsilon_i_j
    except KeyError:
        print("Key '{}' not found in {}".format(shareholder, messages.keys()))
        raise
    if print_statements:
        print("Shares for m_1, m_2:", m_1_shares, m_2_shares)
    delta, _ = reconstruct(setup, delta_shares, field_size, False)
    epsilon, _ = reconstruct(setup, epsilon_shares, field_size, False)
    if print_statements:
        print("Delta:", delta, "Epsilon:", epsilon)
    message_shares = {}
    for i, shareholder in enumerate(shareholder_ids):
        message_shares[shareholder] =\
            linear([(1, computed_shares[i][2]), (epsilon, messages[shareholder][0]), (delta, messages[shareholder][1]), (-delta, epsilon)], field_size)
    if print_statements:
        print("Message shares m:", message_shares)
    m, polynomial = reconstruct(setup, message_shares, field_size)
    m1, _ = reconstruct(setup, m_1_shares, field_size, False)
    m2, _ = reconstruct(setup, m_2_shares, field_size, False)
    if not (s_gamma + ((epsilon * m1) % field_size) + ((delta * m2) % field_size) - ((epsilon * delta)
            % field_size)) % field_size == (m1 * m2) % field_size:
        print("multiply doesn't reconstruct correctly: ",
              s_gamma, "+", epsilon, "*", m1, "+", delta, "*", m2, "-", epsilon, "*", delta, "=",
              (s_gamma + ((epsilon * m1) % field_size) + ((delta * m2) % field_size) - ((epsilon * delta)
              % field_size) % field_size) % field_size, "!=", (m1 * m2) % field_size, "=", m1, "*", m2)
        return False
    elif print_statements:
        print("Shares of m computed correctly")
    return True


def compute_delta_epsilon(m_1, m_2, computed_shares, field_size):
    share_delta = linear([(1, m_1), (-1, computed_shares[0])], field_size)
    share_epsilon = linear([(1, m_2), (-1, computed_shares[1])], field_size)
    # print(share_delta, share_epsilon, "<--")
    return share_delta, share_epsilon


# multiply("2,4", {1: (560, 361), 2: (119, 717), 3: (675, 76), 4: (234, 432)})
