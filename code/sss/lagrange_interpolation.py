import sys
import os
hss = os.path.join(os.pardir, "hss")
sys.path.append(hss)
from reconstruction_tools import divide
from sharing_exceptions import *


# lagrange interpolation to compute the value of a polynomial in a point x
# x                     the point to compute its value for
# x_values; y_values    the known pairs of x/y values (two lists of int)
# field_size            the size of the finite field
def interpolate(x, x_values, y_values, field_size):
    # make sure the format of x and y fits
    assert len(x_values) != 0 and (len(x_values) == len(y_values)),\
        'x and y cannot be empty and must have the same length'
    k = len(x_values)
    # return the sum over the product of lagrange coefficients with y values
    return int((sum(lagrange_polynomial(j, k, x_values, x, field_size)*y_values[j] % field_size
                    for j in range(k))) % field_size)


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
def reconstruct(setup, shares, field_size):
    # create lists of x and y-values of used shares
    x_s = list(shares.keys())
    y_s = list(shares.values())
    if int(setup.split(',')[0]) > len(x_s):
        raise ThresholdNotFulfilledException("Not enough shareholders ({}) to reconstruct from {}"
                                             .format(len(x_s), setup))
    return interpolate(0, x_s, y_s, field_size)
