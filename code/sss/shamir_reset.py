import sys
import os
import numpy as np
hss = os.path.join(os.pardir, "hss")
sys.path.append(hss)
from reconstruction_tools import dict_to_list, calc_derivative_vector, divide
from function_tools import generate_function, calc_function, print_function
from read_and_write_data import create_reset_file
from path import get_data_path_sss
from shamir_renew import get_general_information, sum_up_matrix, verify_correctness
from lagrange_interpolation import lagrange_polynomial


# path to DATA directory
data_path = get_data_path_sss()


# renew the share values for a given set of existing shareholders
# setup         the setup to create the share values for
# old_shares    the subset of values to be renewed
#               note that this subset must be authorized (able to reconstruct the secret)
# new_structure "k,n"
def shamir_reset(setup, new_structure, reset_version_number=None, print_statements=True):
    degree_of_function, field_size, number_of_shares, rec_result, shareholder_ids, shareholders = \
        get_general_information(setup)
    shareholder_shares = {}
    for shareholder in shareholders:
        shareholder_shares[shareholder[0]] = shareholder[1]
    print(shareholder_shares)
    k_prime, n_prime = new_structure.split(',')
    k_prime, n_prime = int(k_prime), int(n_prime)
    # start reset by creating random functions of degree thresholds[-1] - 1, with 0 as the free coefficient
    function_dict = create_random_reset_functions(field_size, k_prime, print_statements, shareholder_shares)
    # create a matrix to store the values calculated in the reset
    partial_shares = compute_all_partial_shares_reset(field_size, function_dict, n_prime, number_of_shares)
    for i, row in enumerate(partial_shares):
        b_i = lagrange_polynomial(i, len(shareholder_ids), shareholder_ids, 0, field_size)
        # compute_b_i(shareholder_ids, i, field_size)
        for j, element in enumerate(row):
            partial_shares[i][j] = (int(element) * b_i) % field_size
    print(partial_shares)
    # calculate the sums of all column values in the matrix
    sums = sum_up_matrix(field_size, partial_shares)
    # save the newly calculated values in a new shareholder:share dict
    resulting_shares = {}
    for i in range(n_prime):
        resulting_shares[i + 1] = int(sums[i])
    print(resulting_shares)
    new_result = verify_correctness(field_size, print_statements, rec_result, resulting_shares, setup)
    # create new .csv file to store the information
    print(resulting_shares)
    file_path = create_reset_file(field_size, new_structure, resulting_shares, setup, hierarchical=False)
    if print_statements:
        print("New Shares are saved to {}".format(file_path))
    return resulting_shares, new_result


def compute_all_partial_shares_reset(field_size, function_dict, n_prime, number_of_shares):
    partial_shares = np.zeros((number_of_shares, n_prime))
    # calculate the values with the formula from the paper
    # ( f^(j)_(k)(i) for all new shareholders (i,j) for all k)
    for i, shareholder in enumerate(function_dict):
        current_function = function_dict[shareholder]
        for j in range(1, n_prime + 1):
            try:

                # actual calculation by saving the result of
                # the j'th derivative of the k'th function for value i to the matrix
                partial_shares[i][j - 1] = int(calc_function(current_function, j, field_size))
            # if something goes wrong with the format of the shareholders
            except ValueError as e:
                print("Error in accessing index of shareholder,"
                      "format should be 's_i_j' for ID (i,j)\n{}".format(repr(e)))
                raise
    return partial_shares


def create_random_reset_functions(field_size, k_prime, print_statements, shareholder_shares):
    if print_statements:
        print("Creating random functions with degree {} and free coefficient share_value for old shareholders."
              .format(k_prime - 1))
    # new dict to store all shareholder: function pairs
    function_dict = {}
    for old_shareholder in shareholder_shares:
        function_dict[old_shareholder] = \
            generate_function(k_prime - 1, shareholder_shares[old_shareholder], field_size)
    # print the functions to screen
    if print_statements:
        for sh in function_dict:
            print(sh, ": ", end='')
            print_function(function_dict[sh])
        print("Calculating values for new shareholders from functions")
    return function_dict
