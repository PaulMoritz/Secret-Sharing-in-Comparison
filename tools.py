import numpy as np


# derivate the given function in place (modulo the prime)
# for each pair of coefficients the normal derivation rules apply
# (factor = factor * exponent,
#  exponent = exponent -1)
def derivate_function(function_to_derivate, prime_number):
    for level in function_to_derivate:
        level[0] = (level[0] * level[1]) % prime_number
        # catch x^0, don't subtract exponent here
        if level[1] > 0:
            level[1] -= 1
        else:
            pass
    return function_to_derivate


# calculate the y- values for each shareholder with their given x
def calc_function(coeff_list, x, prime_number):
    result = 0
    for coefficient in coeff_list:
        result = (result + (coefficient[0] * pow(x, coefficient[1])) % prime_number) % prime_number
    return int((result % prime_number))


# prints the calculated coefficients to a readable format of the function
def print_function(coefficients):
    coefficients = list(reversed(coefficients))
    summand = ""
    for coefficient in coefficients:
        if coefficient[0] == 0 and coefficient[1] == 0:
            pass
        elif coefficient[1] == 1:
            summand += " + " + str(coefficient[0]) + "*x"
        elif coefficient[1] == 0:
            summand += " + " + str(coefficient[0])
        else:
            summand += " + " + str(coefficient[0]) + "*x^" + str(coefficient[1])
    print(summand[3:])


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
    print(interpolation_mat)
    return interpolation_mat, max_j


# TODO correct interpretation of req?
# Requirement 1 from the Appendix (Theorem 3 in Paper)
def requirement_1(matrix, highest_derivative, number_of_points):
    sum_over_matrix = 0
    if not len(matrix) >= number_of_points:
        # level number is > people in subset; --> problem?
        print("Requirement for size of interpolation matrix not fulfilled. Did you use a shareholder more than once?")
        return
    for k in range(highest_derivative + 1):
        for j in range(k + 1):
            for i in range(1, number_of_points+1):
                sum_over_matrix += matrix[i-1][j]
        if not sum_over_matrix >= k + 1:
            return False
    return True

