from read_and_write_data import read_data, create_add_file, read_field_size
from reconstruction_tools import dict_to_list, calc_derivative_vector, sort_coordinates, shareholder_share_list_to_lists
from reconstruct import reconstruct
from function_tools import calc_function
from add_tools import *
import numpy as np
import os, sys
from copy import deepcopy
from path import get_data_path
import warnings
warnings.filterwarnings("error")
hss = os.path.join(os.pardir, "sss")
sys.path.append(hss)
from shamir_add import choose_random_subset



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
    existing_shares, field_size, i, j, new_shareholder, persons_per_level, r, t, thresholds = get_needed_add_data(
        new_shareholder_id, old_shares, reset_version_number, setup)
    if choose_id_randomly:
        # TODO: implement random shareholder
        raise NotImplementedError
    # update level structure with the added shareholder
    update_level_structure(j, persons_per_level, thresholds)
    # merge persons and thresholds to one updated level structure
    level_structure = merge_data(persons_per_level, thresholds[1:])
    # make a list of the already existing shares
    shares = dict_to_list(existing_shares)
    determinant_of_original_matrix, matrix, rec_result, rec_function =\
        check_validity_of_subset(existing_shares, r, setup)
    # troubleshooting
    if not isinstance(rec_result, int):
        raise TypeError("Invalid subset of given shares.")
    elif print_statements:
        print("Old subset is authorized to reset the setup.")
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
    compute_and_split_lambdas(determinant_of_original_matrix, existing_shares, field_size, i, j, matrix, r,
                              splitted_results, t, vector_of_shares)
    if print_statements:
        print("Splitted results are (row wise) \n{}".format(splitted_results))
    # calculate the sums for each shareholder in the finite field
    i, new_share = sum_up_values(field_size, i, new_shareholder, print_statements, splitted_results)
    # add shareholder to the structure
    existing_shares[new_shareholder] = int(new_share % field_size)
    # sanity check that we get the correct result
    if function_f:
        derivatives = calc_derivative_vector(function_f, new_shareholder_id[1], field_size)
        assert(int(new_share % field_size) == calc_function(derivatives[new_shareholder_id[1]], new_shareholder_id[0], field_size)),\
            "New Share ({}) does not equal f^({})({})={}"\
            .format(new_share, j, i, calc_function(derivatives[j], i, field_size))
    # make sure that the new structure with the added shareholder is still authorised
    # NOTE that here linear reconstruction is necessary because of the resulting non-quadratic matrix form
    try:
        subset = choose_random_subset_for_level(existing_shares, len(existing_shares)-1, j)
        print("SUBSET", subset)
        result, result_function, _, _, _ = \
            reconstruct(setup, len(subset), random_subset=False, subset=subset, print_statements=print_statements, test=True)
    except RuntimeWarning:
        return -1, -1
    print(rec_function)
    print(result_function)
    if not result == rec_result:
        raise ValueError("Reconstructed result after add ({}) in setup {} does not match secret {}"
                         .format(result, setup, rec_result))
    else:
        file_path, number_of_add = create_add_file(field_size, level_structure, existing_shares, setup)
        if print_statements:
            print("The resulting new shares for the given structure are:\n{}"
                  "\nNew Shares are saved to {}".format(existing_shares, file_path))
        return existing_shares, result


# sum the splitted results as in step 3 of the add algorithm
def sum_up_values(field_size, i, new_shareholder, print_statements, splitted_results):
    sums = np.sum(splitted_results, axis=0)
    for i, element in enumerate(sums):
        sums[i] = int(element) % field_size
    if print_statements:
        print("Sums mod {} are (column wise): {}".format(field_size, sums))
    # compute the sum for the new shareholder to get the final share value (mod field size of course)
    new_share = np.sum(sums, axis=0) % field_size
    if print_statements:
        print("Share for new Shareholder {} is {}".format(new_shareholder, int(new_share % field_size)))
    return i, new_share


# compute the lamdba-coefficients for each shareholder with the provided formula and
# split these values into r parts after ( steps 1, 2 in the algorithm
def compute_and_split_lambdas(determinant_of_original_matrix, existing_shares, field_size, i, j, matrix, r,
                              splitted_results, t, vector_of_shares):
    for ind in range(len(existing_shares)):
        # value l from the formula beginning with 1
        l = ind + 1
        # result for each shareholder
        summed = compute_derivative_of_interpolation_polynomial(determinant_of_original_matrix, field_size, i, j, l,
                                                                matrix, t - 1)
        # multiply the resulting sum by the share value to get lambda_l
        lambda_l = int(vector_of_shares[ind]) * int(summed) % field_size
        # if the result is positive, randomly split into r parts
        splitted = split_value(lambda_l, r)
        # make sure to have te correct formats
        assert (len(splitted_results[0]) == r and len(splitted) == r), "Wrong format for distribution of delta-values"
        # append result to matrix
        splitted_results[ind] = splitted


# check if the given subset can reconstruct a result, delete later
def check_validity_of_subset(existing_shares, r, setup):
    try:
        rec_result, rec_function, determinant_of_original_matrix, other_determinants, _ = \
            reconstruct(setup, r, random_subset=False, subset=existing_shares, print_statements=False)
        matrix_path = os.path.join(data_path, setup, 'matrix_A.txt')
        matrix = np.loadtxt(matrix_path, dtype=int)
    except TypeError as e:
        print("Could not reconstruct from old shares, thus no authorised subset is given.\n{}".format(e))
        raise
    return determinant_of_original_matrix, matrix, rec_result, rec_function


# increase the number of persons for the level the added shareholder is in
def update_level_structure(j, persons_per_level, thresholds):
    for idx in range(len(thresholds)):
        if j == thresholds[idx]:
            persons_per_level[idx] += 1


# get all the needed data, from the field_size, thresholds, i;j of new shareholder etc.
def get_needed_add_data(new_shareholder_id, old_shares, reset_version_number, setup):
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
    return existing_shares, field_size, i, j, new_shareholder, persons_per_level, r, t, thresholds

# add("1,3", {'s_1_0': 615, 's_1_1': 178, 's_2_1': 309}, (2, 1))
