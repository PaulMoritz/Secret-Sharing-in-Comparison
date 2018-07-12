from reconstruction_tools import *
from preconditions import *
from share_tools import read_level_stats
from function_tools import print_function
import pandas as pd
import random

#
# All Requirements taken from Traverso, G., Demirel, D, Buchmann, J: Dynamic and Verifiable Hierarchical Secret Sharing
#

# seed for testing only!
# random.seed(3211)  # 3311

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")


# reconstruct a secret with a given subset of people, only if
# all thresholds are satisfied and
# all requirements for a unique solution are given.
# setup             String  the setup name to reconstruct the secret from
# number_of people  Integer number of participating people in the subset, chosen randomly
def reconstruct(setup, number_of_people):
    # read the list and extract shareholder information
    shares = []
    person_IDs = []
    functions_involved = []
    threshold_path = os.path.join(datapath, setup, 'level_stats.csv')
    filepath = os.path.join(datapath, setup, 'shares.csv')
    try:
        data = pd.read_csv(filepath, skiprows=0, header=None, delimiter=',', )
        field_size = int(data[1][0])
    except FileNotFoundError:
        print("Shares for setup '{}' not yet created.".format(setup))
        return
    try:
        _, thresholds = read_level_stats(threshold_path)
    except FileNotFoundError as e:
        print("Setup does not exist. {}".format(e))
        return
    # read data of shareholders into tuples
    tuples = [tuple(x) for x in data.values[2:]]
    print("All given shareholders: {}".format(tuples))
    # select a random sample of given shareholders
    try:
        share_list = random.sample(tuples, number_of_people)
    except ValueError as e:
        print("More people chosen ({}) than existing, please choose at most {} shareholders: {}"
              .format(number_of_people, len(tuples), repr(e)))
        return
    print("Subset of {} shareholders randomly selected is {}.".format(number_of_people, share_list))
    for i, shareholder in enumerate(share_list):
        name = shareholder[0].split('_')
        name = name[1:]
        shares.append(int(shareholder[1]))
        person_IDs.append((int(name[0]), int(name[1])))
    person_IDs,  shares = sort_coordinates(person_IDs, shares)
    print("Coordinates (in lexicographic order) are {}".format(person_IDs))
    # read all involved functions (phi)
    for i in range(thresholds[-1]):
        functions_involved.append(i)
    phi = functions_involved
    print("Share value column for interpolation (in lexicographic order) is {}".format(shares))
    print("Vector phi of function x^i (with i printed) is {}".format(phi))
    matrix, max_person_number, highest_derivative = interpolation_matrix(person_IDs)
    # check preliminaries for the interpolation
    print("\nChecking thresholds and requirements:")
    if not thresholds_fulfilled(setup, person_IDs):
        return
    if requirement_1(matrix, highest_derivative, max_person_number):
        print("Requirement 1 'Unique Solution' is satisfied.")
    else:
        print("Requirement 1 'Unique Solution' not satisfied with given subset.")
        return
    if supported_sequence(matrix):
        print("Requirement 1 'No supported 1-sequence of odd length' is satisfied.")
    else:
        print("Requirement 1 'No supported 1-sequence of odd length' not satisfied with given subset.")
        return
    if requirement_2(highest_derivative, field_size, max_person_number):
        print("Requirement 2 'Unique solution over finite field of size {}' is satisfied.".format(field_size))
    # TODO figure x_k out for precondition 2
    '''
    else:
        print("Requirement 2 'Unique solution over finite field of size {}'"
              "not satisfied with given subset.".format(field_size))
        return
    '''

    print("\nAll requirements for a unique solution are given, starting interpolation...")
    # A = calculate_matrix(field_size, highest_derivative, person_IDs, phi)
    # create a matrix with the linear equations to solve
    A = create_matrix(person_IDs, shares, field_size, phi, highest_derivative)
    print("\nResulting matrix of linear equations is:", end='')
    print_matrix(A)
    try:
        # solve the linear equations to get the coefficients
        print("Using Gauss-Jordan elimination to get the coefficients of the function...")
        resulting_matrix, coefficients = gauss_jordan(A, field_size)
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
    print("Reading coefficients from interpolated function from the matrix...")
    print("The interpolated function is \t", end='')
    print_function(final_coefficients)
    print("The secret is {}".format(final_coefficients[0][0]))
    print("\nReconstruction finished.")


reconstruct("another_big_example", 23)
