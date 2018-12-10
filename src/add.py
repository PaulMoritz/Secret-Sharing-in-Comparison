from read_and_write_data import read_data, create_add_file, read_field_size
from reconstruction_tools import dict_to_list, calc_derivative_vector, sort_coordinates, shareholder_share_list_to_lists
from reconstruct import reconstruct
from function_tools import calc_function
from determinant import determinant, get_minor
from reconstruct_linear import reconstruct_linear
from add_tools import *
from exceptions import *
import math
import numpy as np
import os
from copy import deepcopy
from path import get_data_path


# np.random.seed(42)

# get path to DATA directory
data_path = get_data_path()



# add a new shareholder to the given setup without altering the thresholds
# setup                     the setup to work on
# old_shares (dict)         an authorised subset of old shares to perform the computations
# new_shareholder_id        a tuple of (i, j) to specify the shareholder to add
# choose_id_randomly        if true, the id will be chosen randomly from the given structure
# reset_version_number      if the used setup is already a reset/renew, specifies the setup
# print_statements          whether console outputs will be printed
def add(setup, old_shares, new_shareholder_id=(0, 0), choose_id_randomly=False,
        reset_version_number=None, print_statements=True, function_f=[]):
    existing_shares = deepcopy(old_shares)
    # get the name of the new shareholder from the tuple
    new_shareholder = 's_{}_{}'.format(new_shareholder_id[0], new_shareholder_id[1])
    # i and j for the formulas
    i, j = new_shareholder_id[0], new_shareholder_id[1]
    # get all needed information about the setup from the files
    data, persons_per_level, thresholds = read_data(setup, reset_version_number)
    field_size = read_field_size(setup)
    # biggest threshold, needed for computation
    t = thresholds[-1]
    # number_of_existing_shares V(also needed for calculation)
    r = len(existing_shares)
    if choose_id_randomly:
        # TODO: implement random shareholder
        raise NotImplementedError
    # update level structure with the added shareholder
    for idx in range(len(thresholds)):
        if j == thresholds[idx]:
            persons_per_level[idx] += 1
    level_structure = merge_data(persons_per_level, thresholds[1:])
    # make a list of the already existing shares
    shares = dict_to_list(existing_shares)
    try:
        rec_result, rec_function, determinant_of_original_matrix, other_determinants, _ =\
            reconstruct(setup, r, random_subset=False, subset=existing_shares, print_statements=False)
        matrix_path = os.path.join(data_path, setup, 'matrix_A.txt')
        matrix = np.loadtxt(matrix_path, dtype=int)
    except TypeError as e:
        print("Could not reconstruct from old shares, thus no authorised subset is given.\n{}".format(e))
        raise
    # troubleshooting
    if not isinstance(rec_result, int):
        raise TypeError("Invalid subset of given shares.")
    elif print_statements:
        print("Old subset is authorized to reset the setup.")
    # check if all shareholders actually exist
    '''
    if not shareholders_valid(data, shares):
        raise InvalidShareholderException("Invalid shareholder given, please try again with a correct input.")
    
    elif print_statements:
        print("All given shares are valid.\n"
              "Result from Reconstruction: {} (constructed function is {})\n"
              "Finite Field of size {} used.\n"
              "New shareholder to be added is: {}\n"
              "Valid subset of shares given, starting renewal...\n"
              .format(rec_result, rec_function, field_size, new_shareholder))
    '''
    # create an empty matrix of results, where each row represents the splitted delta values of one old shareholder and
    # each column represents the delta-values one old shareholder received from all other shareholders (incl the own)
    splitted_results = np.zeros((r, r))
    # lists to store the ids and shares of each old shareholder
    # get a list of the old shares
    existing_shares_list = dict_to_list(existing_shares)
    # get two lists of IDs and shares out of that list above
    person_ids, shares = shareholder_share_list_to_lists(existing_shares_list)
    # bring IDs and Shares into lexicographic order
    person_ids, vector_of_shares = sort_coordinates(person_ids, shares)
    # actual computation formula for each old shareholder
    for ind in range(len(existing_shares)):
        # value l from the formula beginning with 1
        l = ind + 1
        # result for each shareholder
        summed = compute_derivative_of_interpolation_polynomial(determinant_of_original_matrix, field_size, i, j, l,
                                                                matrix, t - 1)
        # multiply the resulting sum by the share value to get lambda_l
        lambda_l = int(vector_of_shares[ind]) * int(summed) % field_size
        print(lambda_l)
        # if the result is positive, randomly split into r parts
        if lambda_l > 0:
            splitted = randomly_split(lambda_l, r)
        # if it is zero, append a vector of zeros in the according row of the resulting matrix
        elif lambda_l == 0:
            splitted = [0] * r
        # else something must have gone wrong....
        else:
            raise ValueError("No split for value distribution possible(value < 0), lambda_l ={}".format(lambda_l))
        # make sure to have te correct formats
        assert(len(splitted_results[0]) == r and len(splitted) == r), "Wrong format for distribution of delta-values"
        # append result to matrix
        splitted_results[ind] = splitted
    if print_statements:
        print("Splitted results are (row wise) \n{}".format(splitted_results))
    # calculate the sums for each shareholder in the finite field
    sums = np.sum(splitted_results, axis=0)
    for i, element in enumerate(sums):
        sums[i] = int(element) % field_size
    if print_statements:
        print("Sums mod {} are (column wise): {}".format(field_size, sums))
    # compute the sum for the new shareholder to get the final share value (mod field size of course)
    new_share = np.sum(sums, axis=0)
    if print_statements:
        print("Share for new Shareholder {} is {}".format(new_shareholder, int(new_share % field_size)))
    # add shareholder to the structure
    existing_shares[new_shareholder] = int(new_share % field_size)
    derivatives = calc_derivative_vector(function_f, new_shareholder_id[1], field_size)
    assert(int(new_share % field_size) == calc_function(derivatives[new_shareholder_id[1]], new_shareholder_id[0], field_size)),\
        "New Share ({}) does not equal f^({})({})={}"\
        .format(new_share, j, i, calc_function(derivatives[j], i, field_size))
    # make sure that the new structure with the added shareholder is still authorised
    # NOTE that here linear reconstruction is necessary because of the resulting non-quadratic matrix form
    result, result_function = \
        reconstruct_linear(setup, len(existing_shares), random_subset=False, subset=existing_shares,
                           print_statements=False)
    if not result == rec_result:
        raise ValueError("Reconstructed result after add ({}) in setup {} does not match secret {}"
                         .format(result, setup, rec_result))
    else:
        file_path, number_of_add = create_add_file(field_size, level_structure, existing_shares, setup)
        if print_statements:
            print("The resulting new shares for the given structure are:\n{}"
                  "\nNew Shares are saved to {}".format(existing_shares, file_path))
        return existing_shares, result


# add("1,3", {'s_1_0': 615, 's_1_1': 178, 's_2_1': 309}, (2, 1))
