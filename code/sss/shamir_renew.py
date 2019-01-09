import sys
import numpy as np
import os
hss = os.path.join(os.pardir, "hss")
sys.path.append(hss)
from function_tools import generate_function, calc_function, print_function
from read_and_write_data import read_data, read_field_size
from read_and_write_data import create_renew_file
from path import get_data_path_sss
from shamir_add import read_shares
from lagrange_interpolation import reconstruct


# path to DATA directory
data_path = get_data_path_sss()


# renew the share values for a given set of existing shareholders
# setup         the setup to create the share values for
# old_shares    the subset of values to be renewed
#               note that this subset must be authorized (able to reconstruct the secret)
def shamir_renew(setup, reset_version_number=None, print_statements=True):
    degree_of_function, field_size, number_of_shares, rec_result, shareholder_ids, shareholders = \
        get_general_information(setup)

    # start renew by creating random functions of degree thresholds[-1] - 1, with 0 as the free coefficient
    function_dict = create_random_renew_functions(degree_of_function, field_size, print_statements, shareholders)
    partial_shares = compute_all_partial_shares_renew(field_size, function_dict, number_of_shares, shareholder_ids,
                                                      shareholders)
    # calculate the sums of all column values in the matrix
    sums = sum_up_matrix(field_size, partial_shares)
    # This should never happen, just making sure
    assert (len(sums) == len(shareholder_ids)), "Number of results and new shareholders do not match."
    # save the newly calculated values in a new shareholder:share dict
    resulting_shares = {}
    for i in range(len(sums)):
        resulting_shares[shareholder_ids[i]] = int(sums[i])
    new_result = verify_correctness(field_size, print_statements, rec_result, resulting_shares, setup)
    # create new .csv file to store the information
    print(resulting_shares)
    file_path = create_renew_file(field_size, resulting_shares, setup, hierarchical=False)
    if print_statements:
        print("New Shares are saved to {}".format(file_path))
    return resulting_shares, new_result


def compute_all_partial_shares_renew(field_size, function_dict, number_of_shares, shareholder_ids, shareholders):
    # create a matrix to store the values calculated in the renew
    partial_shares = np.zeros((number_of_shares + 1, len(shareholder_ids)))
    # sanity check, should never cause problems
    assert (len(partial_shares) == len(partial_shares[0]) + 1), 'Wrong format of the matrix of partial results ' \
                                                                'for the new share values.'
    # write the old share values to the first row of the matrix
    for ind, value in enumerate(shareholders):
        partial_shares[0][ind] = shareholders[value[0] - 1][1]
    # calculate the other values with the formula from the paper
    # ( f^(j)_(k)(i) for all new shareholders (i,j) for all k)
    for i, shareholder in enumerate(function_dict):
        current_function = function_dict[shareholder]
        for j, shareholder_id in enumerate(shareholder_ids):
            try:
                # actual calculation by saving the result of the k'th function for value i to the matrix
                partial_shares[i + 1][j] = int(calc_function(current_function, shareholder_id, field_size))
            # if something goes wrong with the format of the shareholders
            except ValueError as e:
                print("Error in accessing index of shareholder,\n{}".format(repr(e)))
                raise
    return partial_shares


def verify_correctness(field_size, print_statements, rec_result, resulting_shares, setup):
    # check if the new shares produce the same result in the reconstruction as the old ones
    new_result = reconstruct(setup, resulting_shares, field_size)
    # if not, raise an error
    if not (new_result == rec_result):
        raise ValueError("New Shares don't produce the same result ({}) "
                         "as old shares ({}).".format(new_result, rec_result))
    elif print_statements:
        # print all calculated information to the screen
        print("\nThe resulting new shares for the given structure are:")
        for share in resulting_shares:
            print("{} : {}".format(share, resulting_shares[share]))
        print("New Shares give the same result as old shares ({}), renewal successful."
              .format(new_result))
    return new_result


def sum_up_matrix(field_size, partial_shares):
    sums = np.sum(partial_shares, axis=0)
    # make the results fit into the finite field
    for i, element in enumerate(sums):
        sums[i] = int(element) % field_size
    return sums


def create_random_renew_functions(degree_of_function, field_size, print_statements, shareholders):
    if print_statements:
        print("Creating random functions with degree {} and free coefficient 0 for old shareholders."
              .format(degree_of_function))
    # new dict to store all shareholder: function pairs
    function_dict = {}
    for old_shareholder in shareholders:
        function_dict[old_shareholder] = generate_function(degree_of_function, 0, field_size)
    # print the functions to screen
    if print_statements:
        for sh in function_dict:
            print(sh, ": ", end='')
            print_function(function_dict[sh])
        print("Calculating values for new shareholders from functions")
    return function_dict


def get_general_information(setup):
    shareholders = read_shares(setup)
    print(shareholders)
    share_dict = dict(shareholders)
    shareholder_ids = list(shareholder[0] for shareholder in shareholders)
    # get all necessary data, i.e. the maximum degree of the functions and the size of the finite field
    field_size = read_field_size(setup, hierarchical=False)
    number_of_shares = len(shareholders)
    k, n = setup.split(',')
    k, n = int(k), int(n)
    degree_of_function = k - 1
    # check if the old shares can reconstruct the correct secret and if all given shareholders actually exist
    rec_result = reconstruct(setup, share_dict, field_size)
    return degree_of_function, field_size, number_of_shares, rec_result, shareholder_ids, shareholders

