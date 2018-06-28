from reconstruction_tools import *
from preconditions import *
import numpy as np
import pandas as pd
import random

#
# All Requirements taken from Traverso, G., Demirel, D, Buchmann, J: Dynamic and Verifiable Hierarchical Secret Sharing
#

# seed for testing only!
# 2 for solution with given example     reconstruct("new_test_example_setup", 9)
# random.seed(2)

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
    try:
        filepath = os.path.join(datapath, setup, 'shares.csv')
        data = pd.read_csv(filepath, skiprows=0, header=None, delimiter=',', )
        field_size = int(data[1][0])
    except FileNotFoundError:
        print("Shares for setup '{}' not yet created.".format(setup))
        return
    # read data of shareholders into tuples
    tuples = [tuple(x) for x in data.values[2:]]
    print("All given shareholders: {}".format(tuples))
    # select a random sample of given shareholders
    try:
        share_list = random.sample(tuples, number_of_people)
    except ValueError:
        print(">>> reconstruct({}, {}): More people chosen than existing, please use at most {} people"
              .format(setup, number_of_people, len(tuples)))
        return
    print("Subset of {} shareholders randomly selected is {}.".format(number_of_people, share_list))
    for i, shareholder in enumerate(share_list):
        name = shareholder[0].split('_')
        name = name[1:]
        functions_involved.append(int(name[1]))
        shares.append(int(shareholder[1]))

        person_IDs.append((int(name[0]), int(name[1])))
    person_IDs,  shares = sort_coordinates(person_IDs, shares)
    print("Coordinates (in lexicographic order) are {}".format(person_IDs))

    phi = sorted(set(functions_involved))
    print("Share value column for interpolation (in lexicographic order) is {}".format(shares))
    print("Vector phi of function x^i (with i printed) is {}".format(phi))
    matrix, max_person_number, highest_derivative = interpolation_matrix(person_IDs)
    # check preliminaries for the interpolation
    print("\nChecking thresholds:")
    if not thresholds_fulfilled(setup, person_IDs, number_of_people):
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

    '''
    a_matrix = calculate_a_matrix(person_IDs, phi_functions, int(field_size))
    print("Calculated matrix A(E, X, phi) =\n {}".format(a_matrix))
    
    try:
        det = np.linalg.det(a_matrix)
        print("Determinant of A is {}".format(det))
        matrices = get_matrices(a_matrix, shares)
        print(len(matrices))
        determinants = [np.linalg.det(matrices[i]) for i in range(len(matrices))]
        print(determinants)
    
        print("Can't calculate determinant of non-square matrix.")
    '''

    A = calculate_matrix(field_size, highest_derivative, person_IDs, phi)
    resulting_matrix = gauss_jordan(A, shares, field_size)
    print("Secret is {}".format(resulting_matrix[0][-1]))


#######################################################################################
# NOT USED ANYMORE
def calculate_a_matrix(person_IDs, phi_functions, field_size):
    print("PHI ", str(phi_functions))
    a_matrix = np.zeros((len(person_IDs), len(phi_functions)))
    current_derivative = [0]*len(phi_functions)
    # print(a_matrix)
    for i, row in enumerate(a_matrix):
        x_value = int(person_IDs[i][0])
        derivative_value = int(person_IDs[i][1])
        # print(x_value, derivative_value)
        for j, element in enumerate(row):
            while derivative_value > current_derivative[j]:
                derivate_function([phi_functions[j]], field_size)
                current_derivative[j] += 1
            # print("outer loop ", i, "inner ", j, phi_functions)
            element = phi_functions[j][0] * (x_value ** phi_functions[j][1])
            a_matrix[i][j] = element
            # print(a_matrix)
    return a_matrix


# calculate the matrices with the column vector replacing the i'th column
def get_matrices(matrix, column):
    matrices = {}
    for i in range(len(matrix[0])):
        tmp_matrix = [row[:] for row in matrix]
        for j, row in enumerate(tmp_matrix):
            tmp_matrix[j][i] = column[j]
        matrices[i] = tmp_matrix
    return matrices


# sort_coordinates([(1, 1), (2, 1), (1, 0), (1, 3), (4, 3), (2, 3)], [14, 46, 53, 65, 65, 65])
reconstruct("newer_test_example_setup", 25)
# calculate_A_matrix([('1', '1'), ('1', '2'), ('2', '2'), ('4', '2')], [[1, 1], [1, 2]], 71)
# get_matrices([['1', '1'], ['1', '2'], ['2', '2'], ['4', '2']], ['16', '55', '19', '39'])
# print(inverse(37, 71))
