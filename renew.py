from reconstruct import reconstruct
from reconstruction_tools import read_subset, calc_derivative_vector
from reset_tools import *
from function_tools import generate_function, calc_function, print_function
from read_data_from_files import read_data
from share_tools import write_shares
import numpy as np
import os.path as path

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")
new_list = []


# renew the share values for a given set of existing shareholders
# setup         the setup to create the share values for
# old_shares    the subset of values to be renewed
#               note that this subset must be authorized (able to reconstruct the secret)
def renew(setup, old_shares):
    new_shares = list(old_shares.keys())
    # get all necessary data, i.e. the maximum degree of the functions and the size of the finite field
    data, _, thresholds = read_data(setup)
    field_size = int(data[1][0])
    number_of_old_shares = len(old_shares)
    degree_of_function = thresholds[-1] - 1
    # check if the old shares can reconstruct the correct secret and if all given shareholders actually exist
    rec_result = reconstruct(setup, number_of_old_shares,
                             random_subset=False, subset=old_shares, print_statements=False)
    shares = read_subset(old_shares)
    if not shareholders_valid(data, shares):
        print("Invalid shareholder given, please try again with a correct input.")
        return
    else:
        print("All given shares are valid.")
    if not isinstance(rec_result, int):
        print("Invalid subset of given shares.")
        return
    else:
        print("Old subset is authorized to reset the setup.")
    print("Result from Reconstruction: {}\n"
          "Finite Field of size {} used.\n"
          "New shareholders to be created are: {}\n"
          "Valid subset of shares given, starting renewal...".format(rec_result, field_size, new_shares))
    # start renew by creating random functions of degree thresholds[-1] - 1, with 0 as the free coefficient
    print("Creating random functions with degree {} for old shareholders.".format(degree_of_function))
    function_dict = {}
    for old_shareholder in old_shares:
        function_dict[old_shareholder] = generate_function(degree_of_function, 0, field_size)
    # print the functions to screen
    for sh in function_dict:
        print(sh, ": ", end='')
        print_function(function_dict[sh])
    print("Calculating values for new shareholders from functions")
    # create a matrix to store the values calculated in the renew
    partial_shares = np.zeros((number_of_old_shares + 1, len(new_shares)))
    # sanity check, should never cause problems
    assert (len(partial_shares) == len(partial_shares[0]) + 1), 'Wrong format of the matrix of partial results ' \
                                                                'for the new share values.'
    # write the old share values to the first row of the matrix
    for ind, value in enumerate(old_shares):
        partial_shares[0][ind] = old_shares[value]
    # calculate the other values with the formula from the paper
    # ( f^(j)_(k)(i) for all new shareholders (i,j) for all k)
    for i, shareholder in enumerate(function_dict):
        current_function = function_dict[shareholder]
        for j, other_shareholder in enumerate(new_shares):
            # get all needed derivatives of the current function
            derivatives = calc_derivative_vector(current_function, thresholds[-1], field_size)
            splitted_id = other_shareholder.split("_")
            try:
                # get the indices of the ID (i,j) of current new shareholder
                i_index = int(splitted_id[1])
                j_index = int(splitted_id[2])
                # actual calculation by saving the result of
                # the j'th derivative of the k'th function for value i to the matrix
                partial_shares[i + 1][j] = int(calc_function(derivatives[j_index], int(i_index), field_size))
            # if something goes wrong with the format of the shareholders
            except ValueError as e:
                print("Error in accessing index of shareholder,"
                      "format should be 's_i_j' for ID (i,j)\n{}".format(repr(e)))
                return
    sums = np.sum(partial_shares, axis=0)
    for i, element in enumerate(sums):
        sums[i] = int(element) % field_size
    # This should never happen, just making sure
    assert (len(sums) == len(new_shares)), "Number of results and new shareholders do not match."
    resulting_shares = {}
    for i in range(len(sums)):
        resulting_shares[new_shares[i]] = int(sums[i])
    # create a new file of renewed values each time and give them a unique number
    number_of_reset = 0
    while path.isfile(path.join(datapath, setup, 'shares_after_renew_{}.csv'.format(number_of_reset))):
        number_of_reset += 1
    filepath = path.join(datapath, setup, 'shares_after_renew_{}.csv'.format(number_of_reset))
    write_shares(field_size, filepath, resulting_shares)
    print("The resulting new shares for the given structure are:\n{}"
          "\nNew Shares are saved to {}".format(resulting_shares, filepath))
    # check if the new shares produce the same result in the reconstruction as the old ones
    # if not, raise an error
    new_result = reconstruct(setup, random_subset=False, subset=resulting_shares, print_statements=False)
    if not (new_result == rec_result):
        raise ValueError("New Shares don't produce the same result ({}) "
                         "as old shares ({}).".format(new_result, rec_result))
    else:
        print("New Shares give the same result as old shares ({}), renew successful.".format(new_result))


'''
renew("Small_Company", old_shares={'s_1_1': '3', 's_1_0': '38', 's_2_2': '37', 's_2_1': '2', 's_4_2': '1'})

renew("test_for_reconstruction", old_shares={'s_1_0': '23', 's_11_7': '10', 's_1_1': '39', 's_8_7': '29',
                                             's_3_1': '10', 's_3_7': '60', 's_2_0': '67', 's_1_3': '34', 's_1_4': '65',
                                             's_10_7': '14', 's_3_3': '38', 's_4_4': '22', 's_6_4': '32', 's_1_7': '13',
                                             's_3_4': '15', 's_6_7': '6', 's_4_7': '16', 's_7_7': '40', 's_2_4': '61',
                                             's_5_7': '69', 's_2_3': '39', 's_5_4': '49', 's_2_7': '59'},)
'''
