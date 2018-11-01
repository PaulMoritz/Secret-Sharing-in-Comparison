from reconstruct import reconstruct
from reconstruction_tools import dict_to_list, print_matrix, calc_derivative_vector,\
    sort_coordinates, shareholder_dict_to_lists, divide
from reset_tools import *
from read_and_write_data import create_reset_file
from function_tools import generate_function, calc_function, print_function
from read_and_write_data import read_data
from determinant import determinant, get_minor
import numpy as np
import copy

# get path to DATA directory
cwd = os.getcwd()
main_directory = os.path.abspath(os.path.join(cwd, os.pardir))
data_path = os.path.join(main_directory, "DATA")
new_list = []
debug = False


# reset the given structure with a given new structure and new shareholders
# setup                         the name of the setup
# old_shares                    a dict of existing shareholders with their respective shares
#                               need to be able to reconstruct the secret
# new_shares                    list of structure of the new setup (Format [[people, threshold],...]
# create_new_shares_randomly    whether the new structure is to be selected randomly or manually
# number_of_random_shares       if randomly selected, the number of shares to be created
# reset_version_number          if the used setup is already a reset/renew, specifies the setup
# print_statements              whether console outputs will be printed
def reset(setup, old_shares, new_shares=new_list, create_new_shares_randomly=False,
          number_of_random_shares=0, reset_version_number=None, print_statements=True):
    # read field size and level structure from data
    data, _, thresholds = read_data(setup, reset_version_number)
    field_size = int(data[1][0])
    level_structure = copy.copy(new_shares)
    # setup for random shares
    if create_new_shares_randomly:
        new_shares = create_new_shares(number_of_random_shares, len(thresholds))
        degree_of_function = thresholds[-1] - 1
        number_of_old_shares = number_of_random_shares
    # setup for given shares
    else:
        number_of_old_shares = len(old_shares)
        new_shares, degree_of_function = level_structure_to_id(new_shares)
    # troubleshooting
    if not new_shares:
        raise ValueError("Please enter a valid set of new shareholders "
                         "(or a number >0 if you want to create random new shares).")
    # get results from reconstruction with old shares, most of it used for console outputs and verification
    rec_result, rec_function, determinant_of_original_matrix, determinants, matrix =\
        reconstruct(setup, number_of_old_shares, random_subset=False, subset=old_shares, print_statements=False)
    # put the dict of old shares into list format
    shares = dict_to_list(old_shares)
    # check if all given shareholders exist
    if not shareholders_valid(data, shares):
        raise ValueError("Invalid shareholder given")
    elif print_statements:
        print("All given shares are valid. "
              "Result from Reconstruction: {}\n"
              "Finite Field of size {} used.\n"
              "New shareholders to be created are: {}".format(rec_result, field_size, new_shares))
    if not isinstance(rec_result, int):
        raise TypeError("Invalid subset of given shares.")
    elif print_statements:
        print("Old subset is authorized to reset the setup.")
        print("Valid subset of shares given, starting reset...\n")

    if print_statements:
        print("Creating random functions with degree {} for old shareholders.".format(degree_of_function))
    if debug:
        print("Old shareholders:", old_shares)
    person_ids = []
    vector_of_shares = []
    # get two lists of shareholder IDs and share values
    old_shares_list = dict_to_list(old_shares)
    person_ids, shares = shareholder_dict_to_lists(person_ids, vector_of_shares, old_shares_list)

    # put those lists into lexicographic order
    person_ids, vector_of_shares = sort_coordinates(person_ids, vector_of_shares)

    # actual reset starts here
    # dictionary of random functions for each old shareholder
    function_dict = {}
    if debug:
        print("\nStep 1: calculate Birkhoff Coefficients")
    # i == l-1
    for i, share in enumerate(vector_of_shares):
        # calculate birkhoff interpolation coefficient
        birkhoff_coefficient = (int(share) * (-1) ** i *
                                divide((determinant(get_minor(matrix, i, 0), field_size)) % field_size,
                                       determinant_of_original_matrix, field_size)) % field_size
        # generate a function with the coefficient as scalar
        function_dict[person_ids[i]] = generate_function(degree_of_function, birkhoff_coefficient, field_size)
        if print_statements or debug:
            print("Birkhoff Coefficient a_{}_0:".format(i + 1), birkhoff_coefficient, "=", share,
                  "*(-1)**", i, "*", (determinant(get_minor(matrix, i, 0), field_size)) % field_size,
                  '/', determinant_of_original_matrix)
    if debug:
        print("\nStep 2: Calculated functions with random coefficients")
        for sh in function_dict:
            print(sh, ":", function_dict[sh])
        print("\nStep 3: compute subshares for new shareholders")
    partial_shares = np.zeros((number_of_old_shares, len(new_shares)))
    for i, shareholder in enumerate(function_dict):
        # for each sh take function of shareholder as current function
        current_function = function_dict[shareholder]
        for j, new_shareholder in enumerate(new_shares):
            # for each new sh calc all needed derivatives of current function
            derivatives = calc_derivative_vector(current_function, level_structure[-1][1], field_size)
            splitted_id = new_shareholder.split("_")
            try:
                # get the indices => the i and j value for calculation
                i_index = int(splitted_id[1])
                j_index = int(splitted_id[2])
                # calculate the result for the j'th derivative of the current function for value i
                # save all results in a matrix where each column corresponds to the results of one new shareholder
                partial_shares[i][j] = int(calc_function(derivatives[j_index], int(i_index), field_size))
                if debug:
                    print("Save {} to position [{}][{}] (row defines old shareholder {}, column new sh {}), "
                          "fct is {} ({}. derivative of {})"
                          .format(int(partial_shares[i][j]), i, j, shareholder, new_shareholder,
                                  derivatives[j_index], j_index, derivatives[0]))
            except ValueError as e:
                raise ValueError("Error in accessing index of shareholder,"
                                 "format should be 's_i_j' for ID (i,j)\n{}".format(repr(e)))

    if debug:
        print_matrix(partial_shares)
    # sum up all columns  and % field_size
    sums = np.sum(partial_shares, axis=0)
    for i, element in enumerate(sums):
        sums[i] = int(element) % field_size
    if print_statements or debug:
        print("Sums mod {} are (column wise): {}".format(field_size, sums))
    # This should never happen, just making sure
    assert (len(sums) == len(new_shares)), "Number of results and new shareholders do not match."
    resulting_shares = {}
    # assign each new shareholder its final result from the summed column
    for i in range(len(sums)):
        resulting_shares[new_shares[i]] = int(sums[i])
    # create a new reset each time and give them a unique number
    file_path, number_of_reset = create_reset_file(field_size, level_structure, resulting_shares, setup)
    if print_statements or debug:
        print("The resulting new shares for the given structure are:\n{}"
              "\nNew Shares are saved to {}".format(resulting_shares, file_path))
    new_result, new_function, _, _, _ = reconstruct(setup, random_subset=False,
                                                    subset=resulting_shares, reset_version_number=number_of_reset,
                                                    print_statements=False)
    if not (new_result == rec_result):
        raise ValueError("In Reset: New Shares for '{}' don't produce the same result ({}) "
                         "as old shares ({}).".format(setup, new_result, rec_result))
    elif print_statements:
        print("Reconstructed function for old Shareholders is {}\n"
              "Reconstructed function for reset shareholders is {}\n"
              "New Shares give the same result as old shares ({}), reset successful."
              .format(print_function(rec_function, False), print_function(new_function, False), new_result))
    return resulting_shares
