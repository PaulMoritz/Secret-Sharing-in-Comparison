from reconstruction_tools import divide
from functools import reduce
import operator


# lagrange interpolation
def interpolate(x, x_values, y_values, field_size):
    # compute lagrange-coefficient j
    def lagrange_polynomial(j):
        l_k_n = 1
        for m in range(k):
            if m != j:
                p = divide(x - x_values[m], x_values[j] - x_values[m], field_size) % field_size
                l_k_n *= p
        return l_k_n
    # make sure the format of x and y fits
    assert len(x_values) != 0 and (len(x_values) == len(y_values)),\
        'x and y cannot be empty and must have the same length'
    k = len(x_values)
    # return the sum over the product of lagrange coefficients with y values
    return int((sum(lagrange_polynomial(j)*y_values[j] % field_size for j in range(k))) % field_size)


# split shares into x and y values and call the interpolation
def reconstruct(shares, field_size):
    # create lists of x and y-values of used shares
    x_s = list(shares.keys())
    y_s = list(shares.values())
    return interpolate(0, x_s, y_s, field_size)

