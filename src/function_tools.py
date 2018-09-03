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
def calc_function(function_structure, x, prime_number):
    result = 0
    for coefficient in function_structure:
        result = (result + (int(coefficient[0]) * pow(x, int(coefficient[1]))) % prime_number) % prime_number
    return int((result % prime_number))


# prints the calculated coefficients to a readable format of the function
def print_function(coefficients, printed=True):
    coefficients = list(reversed(coefficients))
    summand = ""
    # for aligned printed functions all coefficients are displayed equally aligned
    # for that, we need to get the maximum number of digits in all numbers
    maximum = 0
    for c in coefficients:
            if len(str(c[0])) > maximum:
                maximum = len(str(c[0]))
    for coefficient in coefficients:

        # special case 0 * x won't be printed
        if coefficient[0] == 0:
            pass
        else:
            summand += " + "
            # for better reading spaces are inserted if a number has less digits than the biggest coefficient
            if len(str(coefficient[0])) < maximum:
                for i in range(len(str(coefficient[0])), maximum):
                    summand += ' '
            # special case x^1 prints only 'x'
            if coefficient[1] == 1:
                summand += str(coefficient[0]) + "*x  "
            # special case x^0 prints only the factor, no x
            elif coefficient[1] == 0:
                summand += str(coefficient[0])
            # common case prints y * x^z
            else:
                summand += str(coefficient[0]) + "*x^" + str(coefficient[1])
    if printed:
        print(summand[3:])
    return summand[3:]


# generates coefficients for the function
# Format: [[a_0, 0], [a_1, 1], [a_2, 2] ...] for f(x) = a_0 *x^0 + a_1 *x^1 + a_2 *x^2....
# with a_0 = message
def generate_function(in_degree, message, prime_number):
    coefficients = [[message, 0]]
    for i in range(1, in_degree + 1):
        a_i = np.random.randint(0, prime_number)
        coefficients.append([a_i, i])
    # print("coefficients are: " + str(coefficients))
    return coefficients


# checks if a number is prime
def is_prime(number):
    if number < 2:
        return False
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    return True
