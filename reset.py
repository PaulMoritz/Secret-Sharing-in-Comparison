from reconstruct import reconstruct
from reconstruction_tools import read_subset, print_matrix, calc_derivative_vector
from reset_tools import *
from function_tools import generate_function, calc_function
from read_data_from_files import read_data
import numpy as np
import os.path as path
import csv

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")
new_list = []


def reset(setup, old_shares, new_shares=new_list, create_new_shares_randomly=False, number_of_random_shares=0):
    data, _, thresholds = read_data(setup)
    field_size = int(data[1][0])
    number_of_old_shares = len(old_shares)
    if create_new_shares_randomly:
        new_shares = create_new_shares(number_of_random_shares, len(thresholds))
        degree_of_function = thresholds[-1] - 1
    else:
        new_shares, degree_of_function = level_structure_to_id(new_shares)
    if not new_shares:
        print("Please enter a valid set of new shareholders "
              "(or a number >0 if you want to create random new shares).")
        return
    rec_result = reconstruct(setup, number_of_old_shares,
                             random_subset=False, subset=old_shares, print_statements=False)
    shares = read_subset(old_shares)
    if not shareholders_valid(data, shares):
        print("Invalid shareholder given")
        return
    else:
        print("All given shares are valid.")
    print("Result from Reconstruction: {}\n"
          "Finite Field of size {} used.\n"
          "New shareholders to be created are: {}".format(rec_result, field_size, new_shares))
    if not isinstance(rec_result, int):
        print("Invalid subset of given shares.")
        return
    else:
        print("Old subset is authorized to reset the setup.")
    print("Valid subset of shares given, starting reset...\n")

    # starting reset
    print("Creating random functions with degree {} for old shareholders.".format(degree_of_function))
    function_dict = {}
    for old_shareholder in old_shares:
        share = int(old_shares[old_shareholder])
        function_dict[old_shareholder] = generate_function(degree_of_function, share, field_size)
    print(old_shares)
    for sh in function_dict:
        print(sh, ":", function_dict[sh])
    print("Calculating values for new shareholders from functions.")
    partial_shares = np.zeros((number_of_old_shares, len(new_shares)))
    for i, shareholder in enumerate(function_dict):
        current_function = function_dict[shareholder]
        for j, other_shareholder in enumerate(new_shares):
            derivatives = calc_derivative_vector(current_function, thresholds[-1], field_size)
            splitted_id = other_shareholder.split("_")
            try:
                i_index = int(splitted_id[1])
                j_index = int(splitted_id[2])
                partial_shares[i][j] = int(calc_function(derivatives[j_index], int(i_index), field_size))
                print("Save {} to matrix [{}][{}], SH is ({},{}), "
                      "fct is {} ({}. der. of {})"
                      .format(int(partial_shares[i][j]), i, j, i_index, j_index,
                              derivatives[j_index], j_index, derivatives[0]))
            except ValueError as e:
                print("Error in accessing index of shareholder,"
                      "format should be 's_i_j' for ID (i,j)\n{}".format(repr(e)))
                return
    print_matrix(partial_shares)
    sums = np.sum(partial_shares, axis=0)
    print("Summed values for each column are {}".format(sums))
    for i, element in enumerate(sums):
        sums[i] = int(element) % field_size
    print("Values mod {} are (column wise): {}".format(field_size, sums))
    # This should never happen, just making sure
    assert (len(sums) == len(new_shares)), "Number of results and new shareholders do not match."
    resulting_shares = {}
    for i in range(len(sums)):
        resulting_shares[new_shares[i]] = int(sums[i])
    # create a new reset each time and give them a unique number
    number_of_reset = 0
    while path.isfile(path.join(datapath, setup, 'shares_after_reset_{}.csv'.format(number_of_reset))):
        number_of_reset += 1
    filepath = path.join(datapath, setup, 'shares_after_reset_{}.csv'.format(number_of_reset))
    with open(filepath, 'w+', newline='', encoding='utf8') as file:
        writer = csv.writer(file)
        writer.writerow(["Chosen finite field size", field_size])
        writer.writerow(["Shareholder", "Share"])
        writer.writerows(resulting_shares.items())

    print("The resulting new shares for the given structure are:\n{}"
          "\nNew Shares are saved to {}".format(resulting_shares, filepath))
    new_result = reconstruct(setup, random_subset=False, subset=resulting_shares, print_statements=False)
    if not (new_result == rec_result):
        raise ValueError("New Shares don't produce the same result ({}) "
                         "as old shares ({}).".format(new_result, rec_result))
    else:
        print("New Shares give the same result as old shares ({}), reset successful.".format(new_result))


reset("Small_Company", old_shares={'s_1_1': '3', 's_1_0': '38', 's_2_2': '37', 's_2_1': '2', 's_4_2': '1'},
      new_shares=[[1, 1], [5, 2], [4, 4]])
'''
reset("test_for_reconstruction", old_shares={'s_1_0': '23', 's_11_7': '10', 's_1_1': '39', 's_8_7': '29',
                                             's_3_1': '10', 's_3_7': '60', 's_2_0': '67', 's_1_3': '34', 's_1_4': '65',
                                             's_10_7': '14', 's_3_3': '38', 's_4_4': '22', 's_6_4': '32', 's_1_7': '13',
                                             's_3_4': '15', 's_6_7': '6', 's_4_7': '16', 's_7_7': '40', 's_2_4': '61',
                                             's_5_7': '69', 's_2_3': '39', 's_5_4': '49', 's_2_7': '59'},
      new_shares=[[2, 1], [4, 3], [3, 4], [13, 7], [11, 10]])
'''
