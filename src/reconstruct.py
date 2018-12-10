from reconstruction_tools import *
from preconditions import *
from determinant import *
from read_and_write_data import read_data, read_field_size
from function_tools import print_function
from exceptions import *
import random
from path import get_data_path

#
# All Requirements taken from Traverso, G., Demirel, D, Buchmann, J: Dynamic and Verifiable Hierarchical Secret Sharing
#

# seed for testing only!
# random.seed(42)

# path to DATA directory
data_path = get_data_path()


empty_dict = {}


# reconstruct a secret with a given subset of people, only if
# all thresholds are satisfied and
# all requirements for a unique solution are given.
# setup                     String  the setup name to reconstruct the secret from
# number_of people          Integer number of participating people in the subset, chosen randomly
# random_subset             Boolean, if the subset is to be chosen randomly or manually
# subset                    the manually inserted subset, dictionary structure
# reset_version_number      if the used setup is already a reset/renew, specifies the setup
# print_statements          whether console outputs will be printed
def reconstruct(setup, number_of_people=0, random_subset=True, subset=empty_dict,
                reset_version_number=None, print_statements=True):
    # if none of the default values is given, return with error
    if number_of_people == 0 and random_subset is True and subset == empty_dict:
        raise ValueError("Please enter either a correct subset of shareholders for 'subset='"
                         "while setting random_subset=False or set random_subset=True"
                         "and provide a number_of_people you want to reconstruct the secret from.")
    # create placeholders for a list of shares, of person IDs and functions

    functions_involved = []
    # read all necessary data from the setup
    try:
        data, _, thresholds = read_data(setup, reset_version_number)
    except FileNotFoundError as e:
        print("Could not find file:\n{}".format(repr(e)))
        raise
    # get size of finite field
    field_size = read_field_size(setup)
    # read data of shareholders into tuples
    tuples = [tuple(x) for x in data.values]
    # if chosen, select a random sample of given shareholders
    if random_subset:
        try:
            share_list = random.sample(tuples, number_of_people)
        except ValueError as e:
            print("More people chosen ({}) than existing, please choose at most {} shareholders.\n{}"
                  .format(number_of_people, len(tuples), repr(e)))
            raise
    # else use given subset
    else:
        # catch case subset == {}
        if not subset:
            raise ValueError("Please enter a valid Dictionary of (shareholder:share) pairs as subset\n"
                             'Example: subset={"s_0_0": 13, "s_1_0": 11}')
        # read dict of subset into a list of lists
        share_list = dict_to_list(subset)
        number_of_people = len(share_list)
    if print_statements:
        print("All given shareholders: {}".format(tuples))
        print("Subset of {} shareholders randomly selected is {}.".format(number_of_people, share_list))
    # expand the lists of shares and person IDs
    person_ids, shares = shareholder_share_list_to_lists(share_list)
    # sort person IDs and corresponding shares into lexicographic order
    person_ids,  shares = sort_coordinates(person_ids, shares)
    if print_statements:
        print("Coordinates (in lexicographic order) are {}".format(person_ids))
    # read all involved functions (phi)
    for i in range(thresholds[-1]):
        functions_involved.append(i)
    phi = functions_involved
    # leads to a non-square matrix
    if not len(person_ids) == len(phi):
        raise ValueError("\nMatrix A is of format {}x{} but must be square for determinant calculation. "
                         "(You need exactly {} shareholders to reconstruct)"
                         .format(len(person_ids), len(phi), len(phi)))
    if print_statements:
        print("Share value column for interpolation (in lexicographic order) is {}".format(shares))
        print("Vector phi of function x^i (with i printed) is {}".format(phi))
    # create an interpolation matrix E and read highest i and j for simplicity
    matrix, max_person_number, highest_derivative = interpolation_matrix(person_ids)
    if print_statements:
        print("The interpolation matrix is \n {}".format(matrix))
        print("\nChecking thresholds and requirements:")
    # check preliminaries for the interpolation
    if not thresholds_fulfilled(setup, person_ids, print_statements):
        raise ThresholdNotFulfilledException("Threshold not fulfilled.")
    if not requirement_1(matrix, highest_derivative, max_person_number):
        print("Requirement 1 'Unique Solution' not satisfied with given subset.")
        raise RequirementNotFulfilledException("Requirement 1 not fulfilled")
    elif print_statements:
        print("Requirement 1 'Unique Solution' is satisfied.")
    if supported_sequence(matrix):
        print("Requirement 1 'No supported 1-sequence of odd length' not satisfied with given subset.")
        raise RequirementNotFulfilledException("Found supported 1-sequence with odd length")
    elif print_statements:
        print("Requirement 1 'No supported 1-sequence of odd length' is satisfied.")
    if not requirement_2(highest_derivative, field_size, len(person_ids)):
        pass
        # TODO figure x_k out for precondition 2; FULFILLMENT OF REQUIREMENT 2 NOT IMPLEMENTED
        '''
        print("Requirement 2 'Unique solution over finite field of size {}'"
              "not satisfied with given subset.".format(field_size))
        return
        '''
    elif print_statements:
        print("Requirement 2 'Unique solution over finite field of size {}' is satisfied.".format(field_size))

    # create a matrix with the linear equations to solve
    A = create_matrix(person_ids, shares, field_size, phi, highest_derivative)
    if print_statements:
        print("\nAll requirements for a unique solution are given, starting interpolation...")

    # calculate matrix A from the paper
    a_matrix = calculate_a_matrix(person_ids, phi, int(field_size))
    matrix_path = os.path.join(data_path, setup, 'matrix_A.txt')
    np.savetxt(matrix_path, a_matrix, fmt='%d')

    if print_statements:
        print("Calculated matrix A(E, X, phi) =", end='')
        print_matrix(a_matrix)

    # matrix must be square to get the determinants
    if len(a_matrix) == len(a_matrix[0]):
        # get determinant
        det = int(determinant(a_matrix, field_size))
        if print_statements:
            print("Determinant of A is {}".format(det))
        # calculate the matrices with the share vectors as the i'th column
        matrices = get_matrices(a_matrix, shares)
        # for matrix in matrices:
        #    print(matrices[matrix])
        # determinant as integer value, needs to be rounded because of calculation
        # print("Calculating determinants")
        determinants = [0]*len(matrices)
        for i in range(len(matrices)):
            # print("Determinant for matrices[{}]".format(i))
            # print_matrix(matrices[i])
            determinants[i] = int(determinant(matrices[i], field_size) % field_size)
            # print("is {} -> saved to {} (i={})".format(determinants[i], determinants, i))
        # determinants = [int(determinant(matrices[i], field_size) % field_size) for i in range(len(matrices))]
        if print_statements:
            print("Determinants of reconstruction matrices are {}".format(determinants))

        if print_statements:
            print("Retrieved determinants, starting reconstruction of coefficients")
        resulting_function = []
        # divide the determinants to get the coefficients for the resulting function
        for k, determinant_value in enumerate(determinants):
            tmp_result = divide(determinant_value, det, field_size)
            resulting_function.append([tmp_result, k])
        if print_statements:
            print("The reconstructed function is\n{}".format(print_function(resulting_function, printed=False)))
        # secret message is the free coefficient
        secret = resulting_function[0][0]
        if print_statements:
            print("The reconstructed message is {}\n\n".format(secret))
        return secret, resulting_function, det, determinants, a_matrix
    else:
        raise NotImplementedError("Should never be reached")


