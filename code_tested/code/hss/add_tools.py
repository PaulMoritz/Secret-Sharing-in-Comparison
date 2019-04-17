import math
from reconstruction_tools import divide
from determinant import *
import random


# randomly split a given value into n parts, where n == number
# value     the value to split
# number    the number of parts to split into
def randomly_split(value, number):
    # delta-vector of splitted values
    deltas = []
    remainder = value
    for i in range(number):

        # if this is the last part, insert remainder
        if i + 1 == number:
            deltas.append(remainder)
        # else randomly choose the next part
        else:
            # randomly choose a number in the range 0 - remaining_value
            delta_i = np.random.randint(0, remainder)
            deltas.append(delta_i)
            remainder -= delta_i
    return deltas


# merge person-numbers and thresholds into a level structure
# persons       list of number of persons for each level
# thresholds    list of thresholds for each level
def merge_level_stats(persons, thresholds):
    # different length is not legal
    if not len(persons) == len(thresholds):
        raise ValueError("Wrong format for level structure, {} levels but {} thresholds given"
                         .format(len(persons), len(thresholds)))
    # iterate over lists and merge them
    else:
        merged_structure = []
        for i in range(len(persons)):
            merged_structure.append([persons[i], thresholds[i]])
    return merged_structure


def merge_data(people, thresholds):
    level_list = []
    if len(thresholds) == len(people):
        for i in range(len(thresholds)):
            level_list.append([people[i], thresholds[i]])
    else:
        raise Exception("Thresholds (length {}) and people (length {}) don't fit".format(len(thresholds), len(people)))
    return level_list


def compute_derivative_of_interpolation_polynomial(determinant_of_original_matrix, field_size, i_value, j_value,
                                                   l_iterator, matrix, summation_boundary_t):
    result = 0
    # print("I: {} J: {} L: {} T: {}".format(i_value, j_value, l_iterator, summation_boundary_t))
    for k in range(j_value, summation_boundary_t + 1):
        # print("K: {}".format(k))
        # apply the formula for each k
        #
        k_term = divide((math.factorial(k) % field_size),
                        ((math.factorial(k - j_value)) % field_size), field_size)
        minus_one_term = ((-1) ** (l_iterator - 1 + k)) % field_size
        divided_determinant = divide(int(determinant(get_minor(matrix, l_iterator - 1, k), field_size)),
                                     determinant_of_original_matrix, field_size)
        #
        i_term = i_value ** (k - j_value)
        former_result = result
        result = (result + (k_term * minus_one_term * divided_determinant * i_term) % field_size) % field_size
        '''
        print(result, "=", former_result, "+(", k_term, "*", minus_one_term, "*([",
              int(determinant(get_minor(matrix, l_iterator - 1, k), field_size)), "/",
              determinant(matrix, field_size), "=", divided_determinant, "])*", i_term, ")")
        '''
    return result


# compute the binomial coefficient in a finite field with n over k given
# working
def binomial_coefficient(n, k, field_size):
    try:
        if n == k or k == 0:
            return 1
        elif k == 1:
            return n
        else:
            return(int(divide((math.factorial(n) % field_size),
                   ((math.factorial(k) % field_size * math.factorial(n - k) % field_size) % field_size), field_size)))
    except ValueError as e:
        print(e)
        raise ValueError("In binomial_coefficient: n must be bigger or equal k;\n{}".format(e))


def split_value(value, r):
    if value > 0:
        splitted = randomly_split(value, r)
    # if it is zero, append a vector of zeros in the according row of the resulting matrix
    elif value == 0:
        splitted = [0] * r
    # else something must have gone wrong....
    else:
        raise ValueError("No split for value distribution possible(value < 0), lambda_l ={}".format(value))
    return splitted


def choose_random_subset_for_level(shares, number, level):
    print(shares, number, level)
    subset = {}
    keep = {key: val for key, val in shares.items() if int(key.split('_')[2]) != level}
    remove_number = {key: val for key, val in shares.items() if int(key.split('_')[2]) == level}
    print("k", keep, "r", remove_number)
    sample_number = number - len(keep)
    print(remove_number, sample_number)
    subset_ids = random.sample(list(remove_number), sample_number)
    for subset_id in subset_ids:
        subset[subset_id] = shares[subset_id]
    print(subset)
    subset.update(keep)
    print(subset)
    return subset
