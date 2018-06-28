import numpy as np
from function_tools import print_function, derivate_function
import copy
import pprint


# creates the interpolation matrix E
def interpolation_matrix(coordinates):
    max_i = 0
    max_j = 0
    for coordinate in coordinates:
        max_i = max(max_i, int(coordinate[0]))
        max_j = max(max_j, int(coordinate[1]))
    interpolation_mat = np.zeros((max_i, max_j + 1))
    for coordinate in coordinates:
        interpolation_mat[int(coordinate[0])-1][int(coordinate[1])] = 1
    print("The interpolation matrix is \n {}".format(interpolation_mat))
    return interpolation_mat, max_i, max_j - 1


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
def gauss_jordan(A, b, field_size):
    print("Using Gauss Jordan to get the coefficients of the function")
    # concatenate A and b to a single matrix, to simplify the calculation
    A = concat(A, b)
    A = [list(reversed(x)) for x in set(tuple(x) for x in A)]
    pprint.pprint(A)
    # list of already used lines (only use each equation once)
    used = []
    # print(A)
    # print(b)
    for i in range(len(A)):
        # print("i: ", i)
        j = i
        for equation_index, equation in enumerate(A):
            # break if we have more equations than variables to solve
            if j >= len(equation) - 1:
                break
            if equation[j] != 0 and equation_index not in used:
                print("TRUE")
                # swap lines if the equation with element != 0 is not at the top (of not yet used equations)
                if equation is not A[j]:
                    try:
                        A = swap(A, equation, A[j])
                        print("Not yet divided ", equation)
                    except ValueError as e:
                        print("Error in swap, unknown Value: {}".format(repr(e)))
                        return
                print("A is ", A)
                print(equation)
                divisor = equation[j]
                # divide the equation by the j'th element, to get a '1' at equation[j]
                # division as done in a finite field!
                for element_index, element in enumerate(equation):
                    equation[element_index] = divide(element, divisor, field_size)
                    print("DIVIDED {} / {} = {}".format(element, divisor, equation[element_index]))
                used.append(j)
                print("Used lines ", used)
                # for each other equation with equation[j] != 0 subtract the elements of the given equation
                # just as in the algorithm
                for index, other_equation in enumerate(A):
                    if other_equation[j] != 0 and other_equation is not equation:
                        substitute = other_equation[j]
                        print(substitute)
                        print(other_equation)
                        for k, element in enumerate(other_equation):
                            tmp = A[index][k]
                            A[index][k] = (A[index][k] - substitute * equation[k]) % field_size
                            print("j {} Line {}, {} - {} * {} is {}"
                            .format(k, other_equation, tmp, substitute, equation[k], A[index][k]))
                # break
    pprint.pprint(A)
    # print the resulting function and return the calculated matrix
    coefficients = [[x[-1], i] for i, x in enumerate(A[:len(equation) - 1])]
    print("The interpolated function is \t", end='')
    print_function(coefficients)
    return A


# swaps two lines in a given matrix A
def swap(A, one_line, other_line):
    # print("SWAP ",A)
    new_A = []
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
            if j == 0:
                mat[i][j] = b[i]
            else:
                mat[i][j] = A[i][j-1]
    print(mat)
    return mat


# calculates the matrix A that holds the system of linear equations to solve
# returns (and prints) the matrix
def calculate_matrix(field_size, highest_derivative, person_IDs, phi):
    # get the functions involved in the system of linear equations
    print("Calculating matrix A")
    current_function = []
    all_functions = []
    for i in range(phi[-1]):
        current_function.append([1, i])
    current_function.reverse()
    all_functions.append(current_function)
    tmp_function = copy.deepcopy(current_function)
    for i in range(highest_derivative):
        tmp_function = copy.deepcopy(tmp_function)
        all_functions.append(derivate_function(tmp_function, int(field_size)))
    # create matrix A
    A = np.zeros((len(person_IDs), phi[-1]))
    for index, pair in enumerate(person_IDs):
        current_function = all_functions[pair[1]]
        factors = []
        for variable in current_function:
            tmp = (variable[0] * pair[0] ** variable[1]) % field_size
            # print(variable[0],' * ', pair[0],' ** ',variable[1], ' = ', tmp)
            factors.append(tmp)
        A[index] = factors
    print("Calculated matrix A(E, X, phi) = \n {}\n".format(A))
    return A


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
