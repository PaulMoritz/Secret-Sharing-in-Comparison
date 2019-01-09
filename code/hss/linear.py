from read_and_write_data import read_data, read_field_size
from function_tools import generate_function, calc_function
from reconstruction_tools import calc_derivative_vector, sort_coordinates, shareholder_share_list_to_lists
import numpy as np


np.random.seed(42)


def linear(list_of_tuples, field_size, print_result=False):
    resulting_share = 0
    for (scalar, share) in list_of_tuples:
        resulting_share = (resulting_share + scalar * share) % field_size
    if print_result:
        print("Linear result is:", resulting_share)
    return resulting_share


def create_shares_for_messages(setup, m_1, m_2):
    messages = {}
    computed_shares = []
    functions = []
    for message in [m_1, m_2]:
        field_size = read_field_size(setup)
        data, _, thresholds = read_data(setup)
        shareholder_ids = [tuple(x) for x in data.values]
        person_ids, vector_of_shares = shareholder_share_list_to_lists(shareholder_ids)
        # put those lists into lexicographic order
        shareholders, _ = sort_coordinates(person_ids, vector_of_shares)
        r = len(shareholders)
        degree_of_function = thresholds[-1] - 1

        random_function = generate_function(degree_of_function, message, field_size)
        if message == m_1:
            random_function = [[2, 0], [2, 1], [3, 2]]
        else:
            random_function = [[3, 0], [6, 1], [4, 2]]
        functions.append(random_function)
        print("function: ", random_function)
        derivatives = calc_derivative_vector(random_function, degree_of_function, field_size)
        for (i, j) in shareholders:
            print((i, j))
            computed_shares.append(calc_function(derivatives[j], i, field_size))
        print("Computed shares ", computed_shares, "(msg {})".format(message))
    for i, (i, j) in enumerate(shareholders):
        messages[(i, j)] = (computed_shares[i - 1], computed_shares[i + r - 1])
    print(messages)

    return messages, message, functions


def multiply_polynomials(f, g, field_size):
    resulting_polynomial = []
    for [f_factor, f_exponent] in f:
        for [g_factor, g_exponent] in g:
            summand = [(f_factor * g_factor) % field_size, (f_exponent + g_exponent)]
            already_included = False
            for coefficient in resulting_polynomial:
                if summand[1] == coefficient[1]:
                    coefficient[0] += summand[0]
                    already_included = True
            if not already_included:
                resulting_polynomial.append(summand)
    return resulting_polynomial


lambda_1 = 2
lambda_2 = 3
shares, _, derivatives = create_shares_for_messages("1,2,3", 4, 5)
for share in shares:
    print(shares[share])
    linear([(shares[share][0], lambda_1), (shares[share][1], lambda_2)], field_size=read_field_size("1,2,3"), print_result=True)
print(derivatives)
p = multiply_polynomials(derivatives[0], derivatives[1], 997)
print(p)



