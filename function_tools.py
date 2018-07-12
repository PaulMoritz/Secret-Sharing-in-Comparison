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
        if coefficient[0] == 0:
            pass
        elif coefficient[1] == 1:
            summand += " + " + str(coefficient[0]) + "*x"
        elif coefficient[1] == 0:
            summand += " + " + str(coefficient[0])
        else:
            summand += " + " + str(coefficient[0]) + "*x^" + str(coefficient[1])
    print(summand[3:])


# generates coefficients for the function
# Format: [[a_0, 0], [a_1, 1, [a_2, 2] ...] for f(x) = a_0 *x^0 + a_1 *x^1 + a_2 *x^2....
# with a_0 = message
def generate_function(in_degree, message, prime_number):
    coefficients = [[message, 0]]
    for i in range(1, in_degree + 1):
        a_i = np.random.randint(1, prime_number)
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

