import numpy as np
import math


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
    print("The interpolation matrix is \n {}".format(interpolation_mat))
    return interpolation_mat,max_i, max_j


# TODO correct interpretation of req?
# Requirement 1 from the Appendix (Theorem 3 in Paper)
def requirement_1(matrix, highest_derivative, number_of_points):
    sum_over_matrix = 0
    if not len(matrix) >= number_of_points:
        # level number is > people in subset; --> problem?
        print("Requirement for size of interpolation matrix not fulfilled.")
        return
    for k in range(highest_derivative + 1):
        for j in range(k + 1):
            for i in range(1, number_of_points+1):
                sum_over_matrix += matrix[i-1][j]
        if not sum_over_matrix >= k + 1:
            return False
    return True


# check for a supported 1-sequence of odd length/ second part of the first requirement as stated in Theorem 3
def supported_sequence(matrix):
    for j, row in enumerate(matrix):
        row_sequence_head = 0
        in_one_sequence = False
        max_sequence = 0
        number_of_ones = 0
        head = 0
        for i, element in enumerate(row):
            if element == 1:
                number_of_ones += 1
                if not in_one_sequence:
                    in_one_sequence = True
                    head = i
                if i == len(row) - 1:
                    if number_of_ones > max_sequence:
                        row_sequence_head = head
                        max_sequence = number_of_ones
            else:
                if in_one_sequence:
                    in_one_sequence = False
                    if number_of_ones > max_sequence:
                        row_sequence_head = head
                        max_sequence = number_of_ones
                number_of_ones = 0
        if max_sequence % 2:
            if check_supported(matrix, j, row_sequence_head):
                return True
    return False


def check_supported(matrix, j, i):
    for row_num, row in enumerate(matrix):
        if not row_num == j:
            for index, element in enumerate(row):
                if index < i:
                    if element == 1:
                        return True
    return False


# Requirement 2 from the Appendix (Theorem 4)
def requirement_2(d, q, max_pers_num):
    res = 2**(- d + 2) * (d - 1)**((d - 1)/2) * math.factorial(d - 1) * max_pers_num**(((d - 1)*(d - 2))/2)
    if not float(q) > res:
        return False
    return True

