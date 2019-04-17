from read_and_write_data import read_data, read_field_size
from function_tools import generate_function, calc_function
from reconstruction_tools import calc_derivative_vector, sort_coordinates, shareholder_share_list_to_lists
import os, sys
hss = os.path.join(os.pardir, "sss")
sys.path.append(hss)
from shamir_add import read_shares


# np.random.seed(42)


def linear(list_of_tuples, field_size, print_result=False):
    resulting_share = 0
    for (scalar, share) in list_of_tuples:
        resulting_share = (resulting_share + scalar * share) % field_size
    if print_result:
        print("Linear result is:", resulting_share)
    return resulting_share


def create_shares_for_messages(setup, m_1, m_2, hierarchical=True):
    messages = {}
    computed_shares = []
    functions = []
    if hierarchical:
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
            functions.append(random_function)
            derivatives = calc_derivative_vector(random_function, degree_of_function, field_size)
            for (i, j) in shareholders:
                computed_shares.append(calc_function(derivatives[j], i, field_size))
        for i, (i, j) in enumerate(shareholders):
            messages[(i, j)] = (computed_shares[i - 1], computed_shares[i + r - 1])
        return messages, message, functions
    else:
        for message in [m_1, m_2]:
            field_size = read_field_size(setup, False)
            shareholders = read_shares(setup, double=True)
            shareholder_ids = list(shareholder[0] for shareholder in shareholders)
            # put those lists into lexicographic order
            r = len(shareholder_ids)
            degree_of_function = int(setup.split(",")[0]) - 1

            random_function = generate_function(degree_of_function, message, field_size)
            functions.append(random_function)
            for i in shareholder_ids:
                computed_shares.append(calc_function(random_function, i, field_size))
        for id in shareholder_ids:
            messages[id] = (computed_shares[id - 1], computed_shares[id + r - 1])
        return messages, message, [[[0, 0]], [[0, 0]]]


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

'''
lambda_1 = 2
lambda_2 = 3
shares, _, derivatives = create_shares_for_messages("2,4", 4, 5, hierarchical=False)
for share in shares:
    print(shares[share])
    linear([(shares[share][0], lambda_1), (shares[share][1], lambda_2)], field_size=read_field_size("1,2,3"), print_result=True)
print(derivatives)
p = multiply_polynomials(derivatives[0], derivatives[1], 997)
print(p)
'''