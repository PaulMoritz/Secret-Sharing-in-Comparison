from reconstruct import reconstruct
from reconstruction_tools import read_subset, print_matrix, calc_derivative_vector
from reset_tools import *
from function_tools import generate_function, calc_function
from read_data_from_files import read_data
import numpy as np


new_list = []


def reset(setup, old_shares, new_shares=new_list, create_new_shares_randomly=False, number_of_random_shares=0):
    data, _, thresholds = read_data(setup)
    field_size = int(data[1][0])
    number_of_old_shares = len(old_shares)
    if create_new_shares_randomly:
        new_shares = create_new_shares(number_of_random_shares, len(thresholds))
    if not new_shares:
        print("Please enter a valid set of new shareholders.")
        return
    rec_result = reconstruct(setup, number_of_old_shares,
                             random_subset=False, subset=old_shares, print_statements=False)
    shares = read_subset(old_shares)
    if not shareholders_valid(data, shares):
        print("Invalid shareholder given")
        return
    else:
        print("All given shares are valid.")
    print("Result from Reconstruction: {}".format(rec_result))
    if not isinstance(rec_result, int):
        print("Invalid subset of given shares.")
        return
    else:
        print("Subset is authorized to reset the setup.")
    print("Valid subset of shares given, starting reset...\n")

    # starting reset
    degree_of_function = thresholds[-1] - 1
    function_dict = {}
    for old_shareholder in old_shares:

        share = int(old_shares[old_shareholder])
        function_dict[old_shareholder] = generate_function(degree_of_function, share, field_size)
    print(old_shares)
    for sh in function_dict:
        print(sh, ":", function_dict[sh])
    partial_shares = np.zeros((number_of_old_shares, len(new_shares)))
    for i, shareholder in enumerate(function_dict):
        current_function = function_dict[shareholder]
        for j, other_shareholder in enumerate(new_shares):
            # print("J: ", j)
            derivatives = calc_derivative_vector(current_function, thresholds[-1], field_size)
            i_index = int(other_shareholder[2])
            j_index = int(other_shareholder[4])
            partial_shares[i][j] = calc_function(derivatives[j_index], int(i_index), field_size)
    print_matrix(partial_shares)
    sums = np.sum(partial_shares, axis=0)
    for i, element in enumerate(sums):
        sums[i] = int(element) % field_size
    print(sums)


reset("test_for_reconstruction", old_shares={'s_1_0': '23', 's_11_7': '10', 's_1_1': '39', 's_8_7': '29',
                                             's_3_1': '10', 's_3_7': '60', 's_2_0': '67', 's_1_3': '34', 's_1_4': '65',
                                             's_10_7': '14','s_3_3': '38', 's_4_4': '22', 's_6_4': '32', 's_1_7': '13',
                                             's_3_4': '15','s_6_7': '6', 's_4_7': '16', 's_7_7': '40', 's_2_4': '61',
                                             's_5_7': '69', 's_2_3': '39', 's_5_4': '49', 's_2_7': '59'},
      new_shares=['s_1_2', 's_2_5', 's_3_0', 's_4_4'])
