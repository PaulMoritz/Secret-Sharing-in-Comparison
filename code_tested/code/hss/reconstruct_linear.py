from reconstruction_tools import *
from preconditions import *
from read_and_write_data import read_data, read_field_size, read_sharing_type
from function_tools import print_function
import random
from sharing_exceptions import *
from path import get_data_path
import warnings
warnings.filterwarnings("error")

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
# setup             String  the setup name to reconstruct the secret from
# number_of people  Integer number of participating people in the subset, chosen randomly
def reconstruct_linear(setup, number_of_people=0, random_subset=True,
                       subset=empty_dict, reset_version_number=None, print_statements=True):
    # if none of the default values is given, return with error
    if number_of_people == 0 and random_subset is True and subset == empty_dict:
        raise Exception("Please enter either a correct subset of shareholders for 'subset='"
                        "while setting random_subset=False or set random_subset=True"
                        "and provide a number_of_people you want to reconstruct the secret from.")
    # create placeholders for a list of shares, of person IDs and functions
    shares = []
    person_ids = []
    functions_involved = []
    # read all necessary data from the setup
    try:
        data, _, thresholds = read_data(setup, reset_version_number)
        conjunctive = read_sharing_type(setup)
    except FileNotFoundError as e:
        print("Could not find file:\n{}".format(repr(e)))
        return
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
            raise Exception("Please enter a valid Dictionary of (shareholder:share) pairs as subset\n"
                            'Example: subset={"s_0_0": 13, "s_1_0": 11}')
        # read dict of subset into a list of lists
        share_list = dict_to_list(subset)
        number_of_people = len(share_list)
    if print_statements:
        print("All given shareholders: {}".format(tuples))
        print("Subset of {} shareholders randomly selected is {}.".format(number_of_people, share_list))
    # expand the lists of shares and person IDs
    for i, shareholder in enumerate(share_list):
        name = shareholder[0].split('_')
        name = name[1:]
        try:
            shares.append(int(shareholder[1]))
            person_ids.append((int(name[0]), int(name[1])))
        # handling errors
        except ValueError as e:
            print("Wrong format of shareholders given, should be 's_i_j' for ID (i,j)\n{}".format(repr(e)))
            raise
        except IndexError as e:
            print("Wrong format of shareholders given, should be 's_i_j' for ID (i,j)\n{}".format(repr(e)))
            raise
    # sort person IDs and corresponding shares into lexicographic order
    person_ids,  shares = sort_coordinates(person_ids, shares)
    if print_statements:
        print("Coordinates (in lexicographic order) are {}".format(person_ids))
    # read all involved functions (phi)
    for i in range(thresholds[-1]):
        functions_involved.append(i)
    phi = functions_involved
    if print_statements:
        print("Share value column for interpolation (in lexicographic order) is {}".format(shares))
        print("Vector phi of function x^i (with i printed) is {}".format(phi))
    # create an interpolation matrix E and read highest i and j for simplicity
    matrix, max_person_number, highest_derivative = interpolation_matrix(person_ids)
    if print_statements:
        print("The interpolation matrix is \n {}".format(matrix))
        print("\nChecking thresholds and requirements:")
    # check preliminaries for the interpolation
    if not thresholds_fulfilled(setup, person_ids, print_statements, conjunctive):
        raise ThresholdNotFulfilledException
    if not requirement_1(matrix, highest_derivative, max_person_number):
        print("Requirement 1 'Unique Solution' not satisfied with given subset.")
        raise RequirementNotFulfilledException
    elif print_statements:
        print("Requirement 1 'Unique Solution' is satisfied.")
    if supported_sequence(matrix):
        print("Requirement 1 'No supported 1-sequence of odd length' not satisfied with given subset.")
        raise RequirementNotFulfilledException
    elif print_statements:
        print("Requirement 1 'No supported 1-sequence of odd length' is satisfied.")
    if not requirement_2(highest_derivative, field_size, max_person_number):
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
        print("\nResulting matrix of linear equations is:", end='')
        print_matrix(A)
    try:
        # solve the linear equations to get the coefficients
        resulting_matrix, coefficients = gauss_jordan(A, field_size)
        if print_statements:
            print("Using Gauss-Jordan elimination to get the coefficients of the function...")
            print("Resulting matrix is:", end='')
            print_matrix(A)
    except ValueError as e:
        print(e)
        raise
    except RuntimeWarning as e:
        print(e)
        raise
    # sanity check, we might encounter an overdetermined system, check that all equations not worked on equal zero
    # or alternatively are just a copy of the line holding the result; this way the result is also right
    sanity_coefficients = list(coefficients[len(A[0]) - 1:])
    for position, c in enumerate(sanity_coefficients):
        if not c[0] == 0:
            # catch the second case from above (just a copied line)
            if not equal(resulting_matrix[c[1]], resulting_matrix[len(A[0]) - 2]):
                raise ValueError("Error in Calculation, Gauss-Jordan elimination could not produce a correct result")
    # print the final function and the secret
    final_coefficients = list(coefficients[:len(A[0])])
    print(final_coefficients)
    if conjunctive:
        secret = int(final_coefficients[0][0])
    else:
        # input leads to an overdetermined system of equations, (one more)
        # thus the last equation will be 0 and the secret is in the second to last equation
        secret = int(final_coefficients[-2][0])
    if print_statements:
        print("Reading coefficients from interpolated function from the matrix...")
        print("The interpolated function is \t", end='')
        reconstructed_function = print_function(final_coefficients)
        print("The secret is {}".format(secret))
        print("\nReconstruction finished.")
    else:
        reconstructed_function = print_function(final_coefficients, printed=False)
    return secret, reconstructed_function
