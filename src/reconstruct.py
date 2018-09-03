from reconstruction_tools import *
from preconditions import *
from read_data_from_files import read_data
from function_tools import print_function
import random

#
# All Requirements taken from Traverso, G., Demirel, D, Buchmann, J: Dynamic and Verifiable Hierarchical Secret Sharing
#

# seed for testing only!
random.seed(42)  # 3311

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")

empty_dict = {}


# reconstruct a secret with a given subset of people, only if
# all thresholds are satisfied and
# all requirements for a unique solution are given.
# setup             String  the setup name to reconstruct the secret from
# number_of people  Integer number of participating people in the subset, chosen randomly
def reconstruct(setup, number_of_people=0, random_subset=True, subset=empty_dict, print_statements=True):
    # if none of the default values is given, return with error
    if number_of_people == 0 and random_subset is True and subset == empty_dict:
        print("Please enter either a correct subset of shareholders for 'subset='"
              "while setting random_subset=False or set random_subset=True"
              "and provide a number_of_people you want to reconstruct the secret from.")
        return
    # read the list and extract shareholder information
    shares = []
    person_IDs = []
    functions_involved = []
    # read all necessary data from the setup
    try:
        data, _, thresholds = read_data(setup)
    except FileNotFoundError as e:
        print("Could not find file:\n{}".format(repr(e)))
        return
    field_size = int(data[1][0])
    # read data of shareholders into tuples
    tuples = [tuple(x) for x in data.values[2:]]
    # select a random sample of given shareholders
    if random_subset:
        try:
            share_list = random.sample(tuples, number_of_people)
        except ValueError as e:
            print("More people chosen ({}) than existing, please choose at most {} shareholders: {}"
                  .format(number_of_people, len(tuples), repr(e)))
            return
    else:
        if not subset:
            print("Please enter a valid Dictionary of (shareholder:share) pairs as subset\n"
                  'Example: subset={"s_0_0": 13, "s_1_0": 11}')
            return
        share_list = read_subset(subset)
        number_of_people = len(share_list)
    if print_statements:
        print("All given shareholders: {}".format(tuples))
        print("Subset of {} shareholders randomly selected is {}.".format(number_of_people, share_list))
    for i, shareholder in enumerate(share_list):
        name = shareholder[0].split('_')
        name = name[1:]
        try:
            shares.append(int(shareholder[1]))
            person_IDs.append((int(name[0]), int(name[1])))
        except ValueError as e:
            print("Wrong format of shareholders given, should be 's_i_j' for ID (i,j)\n{}".format(repr(e)))
            return
        except IndexError as e:
            print("Wrong format of shareholders given, should be 's_i_j' for ID (i,j)\n{}".format(repr(e)))
            return
    person_IDs,  shares = sort_coordinates(person_IDs, shares)
    if print_statements:
        print("Coordinates (in lexicographic order) are {}".format(person_IDs))
    # read all involved functions (phi)
    for i in range(thresholds[-1]):
        functions_involved.append(i)
    phi = functions_involved
    if print_statements:
        print("Share value column for interpolation (in lexicographic order) is {}".format(shares))
        print("Vector phi of function x^i (with i printed) is {}".format(phi))
    matrix, max_person_number, highest_derivative = interpolation_matrix(person_IDs)
    if print_statements:
        print("The interpolation matrix is \n {}".format(matrix))
        print("\nChecking thresholds and requirements:")
    # check preliminaries for the interpolation
    if not thresholds_fulfilled(setup, person_IDs, print_statements):
        return
    if not requirement_1(matrix, highest_derivative, max_person_number):
        print("Requirement 1 'Unique Solution' not satisfied with given subset.")
        return
    elif print_statements:
        print("Requirement 1 'Unique Solution' is satisfied.")
    if not supported_sequence(matrix):
        print("Requirement 1 'No supported 1-sequence of odd length' not satisfied with given subset.")
        return
    elif print_statements:
        print("Requirement 1 'No supported 1-sequence of odd length' is satisfied.")
    if not requirement_2(highest_derivative, field_size, max_person_number):
        pass
        # TODO figure x_k out for precondition 2
        '''
        print("Requirement 2 'Unique solution over finite field of size {}'"
              "not satisfied with given subset.".format(field_size))
        return
        '''
    elif print_statements:
        print("Requirement 2 'Unique solution over finite field of size {}' is satisfied.".format(field_size))

    # A = calculate_matrix(field_size, highest_derivative, person_IDs, phi)
    # create a matrix with the linear equations to solve
    A = create_matrix(person_IDs, shares, field_size, phi, highest_derivative)
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
        return
    # sanity check, we might encounter a overdetermined system, check that all equations not worked on equal zero
    sanity_coefficients = list(coefficients[len(A[0]):])
    for c in sanity_coefficients:
        if not c[0] == 0:
            print("Error in Calculation, Gauss-Jordan elimination could not produce a correct result")
            return
    # print the final function and the secret
    final_coefficients = list(coefficients[:len(A[0])])
    if print_statements:
        print("Reading coefficients from interpolated function from the matrix...")
        print("The interpolated function is \t", end='')
        reconstructed_function = print_function(final_coefficients)
        print("The secret is {}".format(final_coefficients[0][0]))
        print("\nReconstruction finished.")
    else:
        reconstructed_function = print_function(final_coefficients, printed=False)
    return int(final_coefficients[0][0]), reconstructed_function


# reconstruct("test_for_reconstruction", 23)
# reconstruct("Big_Company", 17)
# reconstruct("test_for_reconstruction", random_subset=False, subset={'s_1_0': 3, 's_2_0': 13, 's_1_1': 53, 's_2_1': 22, 's_3_1': 8, 's_4_1': 45, 's_1_3': 5, 's_2_3': 25, 's_3_3': 26, 's_1_4': 43, 's_2_4': 59, 's_3_4': 50, 's_4_4': 43, 's_5_4': 66, 's_6_4': 50, 's_7_4': 15, 's_8_4': 43, 's_9_4': 38, 's_10_4': 54, 's_11_4': 55, 's_12_4': 30, 's_13_4': 37, 's_1_7': 67, 's_2_7': 2, 's_3_7': 52, 's_4_7': 4, 's_5_7': 0, 's_6_7': 40, 's_7_7': 53, 's_8_7': 39, 's_9_7': 69, 's_10_7': 1, 's_11_7': 48})
# reconstruct("Small_Company",random_subset=False,
#            subset={'s_1_1': '3', 's_1_0': '38', 's_2_2': '37', 's_2_1': '2', 's_4_2': '1'})

# reconstruct("Small_Company",random_subset=False,
#            subset={'s_1_0': 31, 's_2_0': 30, 's_1_1': 15, 's_2_1': 13, 's_1_2': 2, 's_2_2': 41, 's_3_2': 33, 's_4_2': 25})
