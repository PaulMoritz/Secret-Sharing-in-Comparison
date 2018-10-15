import numpy as np
from function_tools import derive_function
import copy


# creates the interpolation matrix E
# efficiently, this is just for visualization and the check if requirement 1 is satisfied
def interpolation_matrix(coordinates):
    # save maximum numbers of each i and j for further processing
    max_i = 0
    max_j = 0
    for coordinate in coordinates:
        # check for maximum seen number
        max_i = max(max_i, int(coordinate[0]))
        max_j = max(max_j, int(coordinate[1]))
    # initialise E as matrix of zeros
    interpolation_mat = np.zeros((max_i, max_j + 1))
    # set entry to '1' if person is involved in reconstruction
    for coordinate in coordinates:
        interpolation_mat[int(coordinate[0])-1][int(coordinate[1])] = 1
    return interpolation_mat, max_i, max_j


# converts a dict to a list
# input: dict
# e.g: read_subset({"s_0_0": 13, "s_1_0": 11})
# returns a list [[sh, s],...] of the shareholder:share pairs
def read_subset(subset):
    list_of_shareholders = []
    for shareholder, share in subset.items():
        list_of_shareholders.append((shareholder, share))
    return list_of_shareholders


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
# follows the principle as stated in the english wikipedia
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
        # swap in the following two cases
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
            # append the vector b in the last column of the new matrix
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
    # array of already correctly positioned rows
    right_position = [False] * len(matrix)
    # resulting matrix
    return_matrix = []
    for i in range(row_length):
        for row_index, row in enumerate(matrix):
            # row is already in the right position but not yet marked in the list
            # (nonzero value in the currently viewed column -> one optimal choice for an upper triangular matrix)
            if not row[i] == 0 and not right_position[row_index]:
                # set row as correctly positioned
                right_position[row_index] = True
                # put row in the next row of the resulting matrix
                return_matrix.append(list(row))
    # append all remaining rows
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
                # switch procedure (for each ID and share to keep the connection)
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


# check if two lines (lists) are identical
# return True only if both lists are equal in each (integer) value
def equal(line, other_line):
    for index, pair in enumerate(line):
        if not int(line[index]) == int(other_line[index]):
            return False
    return True


# just a function to print a matrix row-wise
def print_matrix(matrix):
    # get the maximum number of digits in any number, for better printing only
    maximum = 0
    for line in matrix:
        for element in line:
            if len(str(element)) > maximum:
                maximum = len(str(element))
    print()
    for line in matrix:
        for elem in line:
            if len(str(elem)) < maximum:
                # insert spaces to get all numbers the same space on screen
                for i in range(len(str(elem)), maximum):
                    print(' ', end='')
            # print number
            print('', int(elem), end='')
        print()
    print()


# creates a matrix needed for the Gauss elimination
# param personIDs   holds x-value (person_number) and needed derivative (level) for calculation
# other params needed for derivatives or concatenation with result vector
# returns           matrix A, each line in A is a equation to solve where the result of the equation is the share value
def create_matrix(person_IDs, shares, field_size, phi, highest_derivative):
    degree_of_function = phi[-1]
    # list of coefficients of the currently used function
    current_function = []
    # create the function by adding 1*x^number until phi is matched
    for number in phi:
        current_function.append([1, number])
    # calculate and store all needed derivatives
    derivatives = calc_derivative_vector(current_function, highest_derivative, field_size)
    # create matrix A
    A = np.zeros((len(person_IDs), degree_of_function + 1))
    # fill matrix with the calculated values for each shareholder and function
    for i_index, (person_number, level) in enumerate(person_IDs):
        for j_index in range(degree_of_function + 1):
            current_summand = derivatives[level][j_index]
            A[i_index][j_index] = (current_summand[0] * person_number ** current_summand[1]) % field_size
    # concatenate A and b to a single matrix, to simplify the calculation
    A = concat(A, shares)
    # get an upper triangular form to make the algorithm more efficient
    A = make_triangular_matrix(A)
    return A


# calculates a vector of derivatives of the standard-form of a function of degree t-1
# param phi                    vector phi with all involved degrees of functions, here phi[-1] == t-1
# param highest_derivative     the highest derivative needed for the interpolation,
# we won't need to calculate more than needed
# param field_size             field size for calculation
# returns all_functions
# all_functions[i] holds the i'th derivative of the function
def calc_derivative_vector(current_function, highest_derivative, field_size):
    all_functions = [current_function]
    # append all derivatives to the list of all functions
    for _ in range(highest_derivative):
        # copy to not override the function each time
        tmp_fct = copy.deepcopy(current_function)
        # derive the copy
        current_function = derive_function(tmp_fct, field_size)
        # append to all functions
        all_functions.append(current_function)
    return all_functions
