import numpy as np
from function_tools import derivate_function
import copy
import pprint


# creates the interpolation matrix E
# efficiently, this is just for visualization and the check if requirement 1 is satisfied
def interpolation_matrix(coordinates):
    max_i = 0
    max_j = 0
    # save maximum numbers of each i and j for further processing
    for coordinate in coordinates:
        max_i = max(max_i, int(coordinate[0]))
        max_j = max(max_j, int(coordinate[1]))
    interpolation_mat = np.zeros((max_i, max_j + 1))
    # set entry to '1' if person is involved in reconstruction
    for coordinate in coordinates:
        interpolation_mat[int(coordinate[0])-1][int(coordinate[1])] = 1
    print("The interpolation matrix is \n {}".format(interpolation_mat))
    return interpolation_mat, max_i, max_j


# calculate the inverse element of a number in the finite field of size field_size
def inverse(number, field_size):
    for i in range(field_size+1):
        if (i * number) % field_size == 1:
            return i
    raise ValueError


# divide two elements in the finite field, used for solving the linear equations
def divide(a, b, field_size):
    try:
        return (a * inverse(b, field_size)) % field_size
    except ValueError:
        print("Error in inverse: no inverse element found for {}.".format(b))
        return


# Gauss Jordan algorithm implemented in a finite field
# follows the principle as stated in wikipedia
# param A           matrix to solve (last entry in each row (equation) is the share value)
# param field_size  size of the field we're working with (for modulo operations)
def gauss_jordan(A, field_size):
    global equation
    # list of already used lines (only use each equation once)
    used = []
    please_break_outer_loop = False
    # for each person involved, i counts from 1 to r-1
    for i in range(len(A)):
        j = i
        found = False
        # break early in an overdetermined system
        if please_break_outer_loop:
            break
        # for each equation in A
        for equation_index, equation in enumerate(A):
            # break if we have seen more equations than variables to solve (overdetermined)
            if j >= len(equation) - 1:
                found = True
                # break outer loop early
                please_break_outer_loop = True
                break
            # found a not already used equation whose index is nonzero
            if equation[j] != 0 and equation_index not in used:
                found = True
                # swap lines if the equation with element != 0 is not at the top (of not yet used equations)
                if not_equal(equation, A[j]):
                    try:
                        A = swap(A, equation, A[j])
                    except ValueError as e:
                        print("Error in swap, unknown Value: {}".format(repr(e)))
                        return
                divisor = equation[j]
                # divide the equation by the j'th element, to get a '1' at equation[j]
                # division as done in a finite field!
                for element_index, element in enumerate(equation):
                    equation[element_index] = divide(element, divisor, field_size)
                used.append(j)
                # for each other equation with equation[j] != 0 subtract the elements of the given equation
                # just as in the algorithm
                for index, other_equation in enumerate(A):
                    if other_equation[j] != 0 and not_equal(other_equation, equation):
                        subtrahend = other_equation[j]
                        for k, element in enumerate(other_equation):
                            A[index][k] = (A[index][k] - subtrahend * equation[k]) % field_size
        # catch the case that no further solving is possible due to an imbalanced system
        if not found:
            print("Can't determine secret due to a non solvable System of equations, please try again")
            raise ValueError("Found a column where no unused equation is nonzero")
    # return the resulting coefficients and the calculated matrix
    coefficients = [[x[-1], i] for i, x in enumerate(A)]
    return A, coefficients


# swaps two lines in a given matrix A
def swap(A, one_line, other_line):
    new_A = []
    # create new matrix, swap the two given lines
    for i, line in enumerate(A):
        if line is not one_line and line is not other_line:
            new_A.append(line)
        elif line is one_line:
            new_A.append(other_line)
        elif line is other_line:
            new_A.append(one_line)
        else:
            raise ValueError
    return new_A


# concatenates the vector b holding the results to the equations stores in A to A
# efficiently we increase the dimension of A and store b in the new space
def concat(A, b):
    mat = np.zeros((len(A), len(A[0])+1), dtype=int)
    for i, line in enumerate(mat):
        for j, _ in enumerate(line):
            if j == len(line)-1:
                mat[i][j] = b[i]
            else:
                mat[i][j] = A[i][j]
    return mat


# create an upper triangular matrix from the matrix given
# param matrix              the matrix to triangulate
# returns return_matrix     resulting upper triangular matrix
def make_triangular_matrix(matrix):
    row_length = len(matrix[0])
    right_position = [False] * len(matrix)
    return_matrix = []
    for i in range(row_length):
        for row_index, row in enumerate(matrix):
            if not row[i] == 0 and not right_position[row_index]:
                right_position[row_index] = True
                return_matrix.append(list(row))
    for i, element in enumerate(right_position):
        if element is False:
            return_matrix.append(matrix[i])
    return return_matrix


# sorts the coordinates (and the according shares) into lexicographic order as described in the paper
def sort_coordinates(coords, shares):
    for i in range(len(coords)):
        for j in range(i + 1, len(coords)):
            # if the order is not as stated, switch
            if coords[i][0] > coords[j][0] or (coords[i][0] == coords[j][0] and coords[i][1] >= coords[j][1]):
                # print("switching i: {} >  j: {}". format(coords[i], coords[j]))
                tmp = coords[j]
                coords[j] = coords[i]
                coords[i] = tmp
                tmp_share = shares[j]
                shares[j] = shares[i]
                shares[i] = tmp_share
    return coords, shares


# checks if two equations (lists of lists) are not equal in any coefficient
# returns True if not all coefficients are equal, False otherwise
def not_equal(other_equation, one_equation):
    for i, _ in enumerate(one_equation):
        if not one_equation[i] == other_equation[i]:
            return True
    return False


# just a function to print a matrix row-wise
def print_matrix(matrix):
    maximum = 0
    for line in matrix:
        for element in line:
            if len(str(element)) > maximum:
                maximum = len(str(element))
    print()
    for line in matrix:
        for elem in line:
            if len(str(elem)) < maximum:
                for i in range(len(str(elem)), maximum):
                    print(' ', end='')
            print('', elem, end='')
        print()
    print()


# creates a matrix needed for the Gauss elimination
# param personIDs   holds x-value (person_number) and needed derivative (level) for calculation
# other params needed for derivatives or concatenation with result vector
# returns           matrix A, each line in A is a equation to solve where the result of the equation is the share value
def create_matrix(person_IDs, shares, field_size, phi, highest_derivative):
    degree_of_function = phi[-1]
    derivatives = calc_derivative_vector(phi, highest_derivative, field_size)
    # create matrix A
    A = np.zeros((len(person_IDs), degree_of_function + 1))
    for i_index, (person_number, level) in enumerate(person_IDs):
        for j_index in range(degree_of_function + 1):
            current_summand = derivatives[level][j_index]
            A[i_index][j_index] = (current_summand[0] * person_number ** current_summand[1]) % field_size
    # concatenate A and b to a single matrix, to simplify the calculation
    A = concat(A, shares)
    A = make_triangular_matrix(A)
    return A


# calculates a vector of derivatives of the standard-form of a function of degree t-1
# param phi                    vector phi with all involved degrees of functions, here phi[-1] == t-1
# param highest_derivative     the highest derivative needed for the interpolation,
# we won't need to calculate more than needed
# param field_size             field size for calculation
# returns all_functions
# all_functions[i] holds the i'th derivative of the function
def calc_derivative_vector(phi, highest_derivative, field_size):
    all_functions = []
    current_function = []
    for j in range(highest_derivative + 1):
        if j == 0:
            for number in phi:
                current_function.append([1, number])
        else:
            tmp_fct = copy.deepcopy(current_function)
            current_function = derivate_function(tmp_fct, field_size)
        all_functions.append(current_function)
    return all_functions
