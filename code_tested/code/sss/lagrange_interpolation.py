import sys
import os
from scipy.interpolate import interp1d

hss = os.path.join(os.pardir, "hss")
sys.path.append(hss)
from shamir_add import choose_random_subset
from reconstruction_tools import divide
from sharing_exceptions import *
from function_tools import print_function


# lagrange interpolation to compute the value of a polynomial in a point x
# x                     the point to compute its value for
# x_values; y_values    the known pairs of x/y values (two lists of int)
# field_size            the size of the finite field
def interpolate(x, x_values, y_values, field_size, print_statements):
    # make sure the format of x and y fits
    assert len(x_values) != 0 and (len(x_values) == len(y_values)),\
        'x and y cannot be empty and must have the same length'
    k = len(x_values)
    # return the sum over the product of lagrange coefficients with y values
    y_intercept = int((sum(lagrange_polynomial(j, k, x_values, x, field_size) * y_values[j] % field_size
                           for j in range(k))) % field_size)
    polynomial = compute_polynomial(x_values, y_values, k, field_size, print_statements)
    return y_intercept, polynomial


def compute_polynomial(x_values, y_values, k, field_size, print_statements):
    polynomials = []
    for l in range(len(x_values)):
        l_polynomial = []
        for j in range(k):
            l_k_n = 1
            equation = []
            # m: iteration index
            for m in range(k):
                # j: index for this specific lagrange coefficient
                if m != j:
                    # p = divide(x - int(x_values[m]), int(x_values[j]) - int(x_values[m]), field_size) % field_size
                    divisor = divide(1, int(x_values[j]) - int(x_values[m]), field_size)
                    equation.append(([divisor, 1], [(- int(x_values[m]) * divisor) % field_size, 0]))
                    # print("EQ:", equation)
            # print("EQ:", equation)
            try:
                tmp = equation[0]
                # print(tmp)
                for tup in range(1, k-1):
                    tmp = multiply(tmp, equation[tup], field_size)
                tmp = [[(tmp[i][0] * y_values[j]) % field_size, tmp[i][1]] for i in range(len(tmp))]
                # print(tmp)
                l_polynomial.append(tmp)
                # print("-->", l_polynomial)
            except IndexError:
                return -1
    polynomial = sum_polynomials(l_polynomial, field_size)
    if print_statements:
        print("Reconstructed polynomial:", print_function(polynomial, False))
    return polynomial


def sum_polynomials(polynomials, field_size):
    # print("summing", polynomials)
    result = [[0, 0]]*len(polynomials[0])
    for polynomial in polynomials:
        for j in range(len(polynomial)):
            # print(polynomial[j], result[j], polynomial[j])
            result[j] = [(polynomial[j][0] + result[j][0]) % field_size, polynomial[j][1]]
    return result


def multiply(first, second, field_size):
    tmp = []
    # print("First:", first, "Second:", second)
    for i in range(len(first)):
        for j in range(len(second)):
            tmp.append(((first[i][0] * second[j][0]) % field_size, (first[i][1] + second[j][1]) % field_size))

        # print("tmp", tmp)
    known = []
    factor = []
    for i, summand in enumerate(tmp):
        if type(summand) is tuple:
            # print(summand)
            if summand[1] not in known:
                known.append(summand[1])
                factor.append(list(summand))
            else:
                index = find_in_known(summand[1], known)
                # print("f", factor[index][0], index)
                factor[index][0] = (factor[index][0] + summand[0]) % field_size
    return factor


def find_in_known(exponent, known_list):
    for index, element in enumerate(known_list):
        if element == exponent:
            return index
    raise TypeError("Can't find {} in {}".format(exponent, known_list))


# compute lagrange-coefficient l_j(x)
# j             lagrange coefficient of shareholder s_j
# k             number of given points to interpolate from
# x_values      all IDs of participating shareholders
# x             the point to compute its value for
# field_size    the size of the finite field
def lagrange_polynomial(j, k, x_values, x, field_size):
    l_k_n = 1
    # m: iteration index
    for m in range(k):
        # j: index for this specific lagrange coefficient
        if m != j:
            p = divide(x - int(x_values[m]), int(x_values[j]) - int(x_values[m]), field_size) % field_size
            l_k_n = (l_k_n * p) % field_size
    return l_k_n


# reconstruct the free coefficient of a secret polynomial
# knowing a subset of x/y values
# split shares into x and y values and call the interpolation
# setup         the setup to reconstruct for -> (k,n) setup
# shares: dict  the known shares in dictionary format
#               e.g. {'1': 313, '2': 87, '3': 17, '4': 207}
# field_size    the size of the finite field
def reconstruct(setup, shares, field_size, print_statements=True):
    # create lists of x and y-values of used shares
    x_s = list(shares.keys())
    y_s = list(shares.values())
    required_shareholders = int(setup.split(',')[0])
    if required_shareholders > len(x_s):
        raise ThresholdNotFulfilledException("Not enough shareholders ({}) to reconstruct from '{}'"
                                             .format(len(x_s), setup))
    elif required_shareholders < len(x_s):
        minimum_shares = choose_random_subset(shares, required_shareholders)
        if print_statements:
            print("We need to reduce the number of shareholders from {} to a minmal set of {} shareholders.\n"
                  "Shareholders selected are {}".format((x_s, y_s), required_shareholders, minimum_shares))
        x_s = list(minimum_shares.keys())
        y_s = list(minimum_shares.values())
    return interpolate(0, x_s, y_s, field_size, print_statements)


# print(sum_polynomials([[[1,3],[2,2],[5,1],[4,0]],[[5,3],[3,2],[1,1],[0,0]]]))
# print(reconstruct("4,4", {1: 991, 2: 0, 3: 2, 4: 6}, 997))
