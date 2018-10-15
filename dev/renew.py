from reconstruct import reconstruct
from reconstruction_tools import read_subset, calc_derivative_vector
from reset_tools import *
from function_tools import generate_function, calc_function, print_function
from read_data_from_files import read_data
from share_tools import write_shares
import numpy as np
import os.path as path

# path to DATA directory
cwd = os.getcwd()
main_directory = os.path.abspath(os.path.join(cwd, os.pardir))
data_path = os.path.join(main_directory, "DATA")


# renew the share values for a given set of existing shareholders
# setup         the setup to create the share values for
# old_shares    the subset of values to be renewed
#               note that this subset must be authorized (able to reconstruct the secret)
def renew(setup, old_shares):
    # if old shares == {'shares': 'all'} use all shares from the setup; special case for convenience
    if old_shares == {'shares': 'all'}:
        old_shares = get_all_shares_from_setup(setup)
    new_shares = list(old_shares.keys())
    # get all necessary data, i.e. the maximum degree of the functions and the size of the finite field
    data, _, thresholds = read_data(setup)
    field_size = int(data[1][0])
    number_of_old_shares = len(old_shares)
    degree_of_function = thresholds[-1] - 1
    # check if the old shares can reconstruct the correct secret and if all given shareholders actually exist
    try:
        rec_result, rec_function = reconstruct(setup, number_of_old_shares,
                                               random_subset=False, subset=old_shares, print_statements=False)
    except TypeError:
        print("Could not reconstruct from old shares, thus no authorised subset is given.")
        return
    # convert dict of subset to list
    shares = read_subset(old_shares)
    # troubleshooting
    if not isinstance(rec_result, int):
        print("Invalid subset of given shares.")
        return
    else:
        print("Old subset is authorized to reset the setup.")
    # check if all shareholders actually exist
    if not shareholders_valid(data, shares):
        print("Invalid shareholder given, please try again with a correct input.")
        return
    else:
        print("All given shares are valid.")
    print("Result from Reconstruction: {} (constructed function is {})\n"
          "Finite Field of size {} used.\n"
          "New shareholders to be created are: {}\n"
          "Valid subset of shares given, starting renewal...\n"
          .format(rec_result, rec_function, field_size, new_shares))
    # start renew by creating random functions of degree thresholds[-1] - 1, with 0 as the free coefficient
    print("Creating random functions with degree {} and free coefficient 0 for old shareholders."
          .format(degree_of_function))
    # new dict to store all shareholder: function pairs
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
    # calculate the sums of all column values in the matrix
    sums = np.sum(partial_shares, axis=0)
    # make the results fit into the finite field
    for i, element in enumerate(sums):
        sums[i] = int(element) % field_size
    # This should never happen, just making sure
    assert (len(sums) == len(new_shares)), "Number of results and new shareholders do not match."
    # save the newly calculated values in a new shareholder:share dict
    resulting_shares = {}
    for i in range(len(sums)):
        resulting_shares[new_shares[i]] = int(sums[i])
    # check if the new shares produce the same result in the reconstruction as the old ones
    new_result, new_function = reconstruct(setup, random_subset=False, subset=resulting_shares, print_statements=False)
    # if not, raise an error
    if not (new_result == rec_result):
        raise ValueError("New Shares don't produce the same result ({}) "
                         "as old shares ({}).".format(new_result, rec_result))
    else:
        # print all calculated information to the screen
        print("\nThe resulting new shares for the given structure are:")
        for share in resulting_shares:
            print("{} : {}".format(share, resulting_shares[share]))
        print("Old shares reconstruct the following polynomial:\t\t {}\n"
              "New generated shares reconstruct the following polynomial:\t {}\n"
              "New Shares give the same result as old shares ({}), renewal successful."
              .format(rec_function, new_function, new_result))
        # create new .csv file to store the information
        file_path = create_renew_file(field_size, resulting_shares, setup)
        print("New Shares are saved to {}".format(file_path))


# create a unique file saving the resulting share-values in the corresponding directory
def create_renew_file(field_size, resulting_shares, setup):
    # create a new file of renewed values each time and give them a unique number
    number_of_reset = 0
    # search the smallest possible number not yet used for a new file
    while path.isfile(path.join(data_path, setup, 'shares_after_renew_{}.csv'.format(number_of_reset))):
        number_of_reset += 1
    # create this file
    file_path = path.join(data_path, setup, 'shares_after_renew_{}.csv'.format(number_of_reset))
    write_shares(field_size, file_path, resulting_shares)
    return file_path