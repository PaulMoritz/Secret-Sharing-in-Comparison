import numpy.random as random
import os
import math
from linear import linear
from read_and_write_data import read_field_size, read_data
from function_tools import generate_function, calc_function
from reconstruction_tools import calc_derivative_vector, shareholder_share_list_to_lists, sort_coordinates
from determinant import *
from add_tools import compute_derivative_of_interpolation_polynomial, binomial_coefficient, split_value
from reconstruct import reconstruct
from path import get_data_path


random.seed(42)

# get path to DATA directory
data_path = get_data_path()


# proposed PreMult algorithm
def pre_mult(setup):
    # get all needed data, i.e. field size, highest threshold, IDs of all shareholder
    global all_lambda, all_mu, all_lambda_values, all_mu_values, alpha_and_beta_shares
    field_size, matrix, r, shareholders, t, thresholds = get_setup_info(setup)
    # first step: choose alpha and beta
    all_new_shares_alpha = np.zeros((r, r))
    all_new_shares_beta = np.zeros((r, r))

    # testing only
    alpha_secrets = [None] * r
    beta_secrets = [None] * r

    # call rand shares algorithm for each shareholder to get alpha and beta shares
    for i, shareholder in enumerate(shareholders):
        # call rand_shares to compute alpha and beta-shares
        # 2nd and 3rd value only for testing, delete later
        all_new_shares_alpha[i], alpha_secrets[i] = rand_shares_calculation(field_size, shareholders, thresholds)
        all_new_shares_beta[i], beta_secrets[i], = rand_shares_calculation(field_size, shareholders, thresholds)
    summed_alpha_shares = rand_shares_summation(all_new_shares_alpha, alpha_secrets, field_size, r)
    summed_beta_shares = rand_shares_summation(all_new_shares_beta, beta_secrets, field_size, r)
    summed_alpha_shares = [18, 28, 12]
    summed_beta_shares = [22, 33, 14]
    # second step: compute delta and epsilon
    # we need the maximum j-value for further calculation/ indices
    max_j = max([shareholder[1] for shareholder in shareholders])
    # each shareholder s_l performs the following steps
    assert(r >= 1), "Can't calculate lambda and mu values"
    # whole computation of delta and epsilon values
    alpha_and_beta_shares = {}
    # array with r^2 rows and r*(j + 1) columns
    all_lambda = np.zeros((r * r, r * (max_j + 1)))
    all_mu = np.zeros((r * r, r * (max_j + 1)))
    # those are for testing only!
    all_lambda_values = np.zeros((r * r, (max_j + 1)))
    all_mu_values = np.zeros((r * r, (max_j + 1)))
    for l in range(1, r + 1):
        # print("L is ", l)

        # each shareholder performs the summations
        for i, shareholder in enumerate(shareholders):
            # stored for later processing
            alpha_and_beta_shares[shareholder] = [int(summed_alpha_shares[i]), int(summed_beta_shares[i])]
            # needs to be done for each m in 0...j
            compute_and_split_lambda_mu(all_lambda, all_lambda_values, field_size, i, l, matrix,
                                        r, shareholder, summed_alpha_shares, t)
            compute_and_split_lambda_mu(all_mu, all_mu_values, field_size, i, l, matrix,
                                        r, shareholder, summed_beta_shares, t)

    # tmp_lambda/mu: in each list for 'l,(i,j)' are the splitted values saved for l, i, j with m € 0...j
    lambda_m = split_matrices_on_y_axis(all_lambda, max_j+1)
    mu_m = split_matrices_on_y_axis(all_mu, max_j+1)

    # testing only!
    lambda_non_split, mu_non_split = test_matrix_match_on_non_splitted(all_lambda_values, all_mu_values, field_size,
                                                                       lambda_m, max_j, mu_m, r)
    summed_delta = compute_delta_epsilon(field_size, lambda_m, max_j, r)
    summed_epsilon = compute_delta_epsilon(field_size, mu_m, max_j, r)
    # print("Compare: delta\n", lambda_non_split, "\nepsilon\n", mu_non_split)
    assert_matching_matrices(lambda_non_split, max_j, mu_non_split, r, summed_delta, summed_epsilon)
    print("alpha_beta ", alpha_and_beta_shares)
    # third step: compute gammas
    computed_triple = compute_and_add_gamma_shares(alpha_and_beta_shares, field_size, shareholders, summed_delta,
                                                   summed_epsilon)
    print(computed_triple)
    return computed_triple, shareholders, alpha_secrets, beta_secrets


def get_setup_info(setup):
    field_size = read_field_size(setup)
    data, _, thresholds = read_data(setup)
    t = thresholds[-1]
    shareholder_ids = [tuple(x) for x in data.values]
    # create a list of the shareholder IDs and a corresponding list of their share-values (only necessary for sorting)
    person_ids, vector_of_shares = shareholder_share_list_to_lists(shareholder_ids)
    # put those lists into lexicographic order
    shareholders, _ = sort_coordinates(person_ids, vector_of_shares)
    print("Shareholders:", shareholders)
    # get the matrix A from the saved file
    matrix_path = os.path.join(data_path, setup, 'matrix_A.txt')
    matrix = np.loadtxt(matrix_path, dtype=int)
    print("Matrix A:\n", matrix)
    # r = number of shareholders participating
    r = len(shareholders)
    return field_size, matrix, r, shareholders, t, thresholds


# proposed RandShares algorithm
def rand_shares_calculation(field_size, shareholders, thresholds):
    computed_shares = []
    degree_of_function = thresholds[-1] - 1
    secret = np.random.randint(0, field_size)
    random_function = generate_function(degree_of_function, secret, field_size)
    # print("Function: ", random_function)
    derivatives = calc_derivative_vector(random_function, degree_of_function, field_size)
    for (i, j) in shareholders:
        computed_shares.append(calc_function(derivatives[j], i, field_size))
    # print("RAND Computed shares ", computed_shares, "(msg {})".format(secret))
    return computed_shares, secret


def rand_shares_summation(all_new_shares, secrets, field_size, r):
    all_shares = [None] * r
    print(secrets)
    # sum over all alpha shares of one ID and append a '1' (neutral element for multiplication) to call linear
    for j in range(r):
        tmp_shares = []
        for i in range(r):
            tmp_shares.append((1, int(all_new_shares[i][j])))
        all_shares[j] = tmp_shares
    summed_shares = []
    # call linear to compute the sum (step 4 in rand_shares)
    # iterate over all alphas of one share to be able to recursively call linear
    for i in range(r):
        summed_shares.append(linear(all_shares[i], field_size))
    print("RAND", summed_shares)
    return summed_shares


# actual apply of the formula for lambda/mu values and split of those into r values
def compute_and_split_lambda_mu(all_values, all_values_non_split, field_size, i, l, matrix, r,
                                shareholder, summed_shares, t):
    for m in range(shareholder[1] + 1):
        # computation and split of lambda/mu values
        tmp_value = []
        # print("\n calculating value_{}^{},{}".format(l, m, shareholder))
        value_l_m = (compute_derivative_of_interpolation_polynomial(
            determinant_of_original_matrix=determinant(matrix, field_size), field_size=field_size,
            i_value=shareholder[0], j_value=m, l_iterator=l, matrix=matrix,
            summation_boundary_t=t-1)
                      * int(summed_shares[l - 1])) % field_size
        # print("Computed value is ", value_l_m)
        # split
        lambda_splitted = split_value(value_l_m, r)
        tmp_value.append(lambda_splitted)

        # testing only
        all_values_non_split[i + (l - 1) * r][m] = value_l_m
        # print("splitted lambda is\n", tmp_value)
        put_splitted_value_into_matrix(all_values, i, l, m, r, shareholder, tmp_value)
        # print("put into matrices\n", all_values)


def put_splitted_value_into_matrix(
        matrix, shareholder_number, l, m, number_of_shareholders, shareholder, splitted_list):
    for item in splitted_list:
        for index in range(len(item)):
            matrix[shareholder_number +
                   (l - 1) * number_of_shareholders][number_of_shareholders * m + index] = item[index]


def split_matrices_on_y_axis(matrix, number_of_split):
    return np.split(matrix, number_of_split, axis=1)


def test_matrix_match_on_non_splitted(all_lambda_values, all_mu_values, field_size, lambda_m, max_j, mu_m, r):
    # temporary variables for testing
    lambda_to_sum = np.split(all_lambda_values, r, axis=0)
    mu_to_sum = np.split(all_mu_values, r, axis=0)
    # for comparison we take the calculated values and sum them without the distribution, to verify it
    # must be deleted afterwards!
    lambda_non_split = np.zeros((r, max_j + 1))
    mu_non_split = np.zeros((r, max_j + 1))
    for i in range(r):
        lambda_non_split = np.add(lambda_non_split, lambda_to_sum[i]) % field_size
        mu_non_split = np.add(mu_non_split, mu_to_sum[i]) % field_size
    lambda_non_split = np.split(lambda_non_split, max_j + 1, axis=1)
    mu_non_split = np.split(mu_non_split, max_j + 1, axis=1)
    # end of delete
    return lambda_non_split, mu_non_split


def compute_delta_epsilon(field_size, value_m, max_j, r):
    summed_value = [None] * (max_j + 1)
    for m in range(max_j + 1):
        value = np.zeros((r, r))
        value_split = np.split(value_m[m], r)
        for i in range(r):
            value = np.add(value, value_split[i]) % field_size
        summed_value[m] = np.sum(value, axis=1) % field_size
    return summed_value


def assert_matching_matrices(lambda_non_split, max_j, mu_non_split, r, summed_delta, summed_epsilon):
    # testing only, delete afterwards
    for m in range(max_j + 1):
        for i in range(r):
            assert ((summed_delta[m][i] == lambda_non_split[m][i]) and
                    (summed_epsilon[m][i] == mu_non_split[m][i]))
    print("Distribution of lambda/mu correct")
    # end of delete


def compute_and_add_gamma_shares(alpha_beta_shares, field_size, shareholders, summed_delta, summed_epsilon):
    gammas_shared = {}
    computed_triple = {}
    # each shareholder gets their own gamma-share value
    for idx, shareholder in enumerate(shareholders):
        result = 0
        j = shareholder[1]
        # the sum in the calculation
        for m in range(j + 1):
            result = (result + binomial_coefficient(j, m, field_size) *
                      int(summed_delta[j - m][idx]) * int(summed_epsilon[m][idx])) % field_size
        # display resulting shares
        print("Gamma_{}_{} =".format(shareholder[0], shareholder[1]), result)
        gammas_shared[shareholder] = result
        # concatenate the gammas with the before-computed alphas and betas to form a triple for each shareholder
        computed_triple[shareholder] = (alpha_beta_shares[shareholder][0], alpha_beta_shares[shareholder][1],
                                        gammas_shared[shareholder])
    return computed_triple


def test_pre_mult(setup):
    outer_field_size = read_field_size(setup)
    triple, shareholders_, alpha_s, beta_s = pre_mult(setup)
    gammas = {}
    for i_, value in enumerate(triple):
        gammas["s_{}_{}".format(shareholders_[i_][0], shareholders_[i_][1])] = triple[value][2]

    alphas = {}
    for i_, value in enumerate(triple):
        alphas["s_{}_{}".format(shareholders_[i_][0], shareholders_[i_][1])] = triple[value][0]
    a, a_f, _, _, _ = reconstruct(setup, random_subset=False, subset=alphas, print_statements=False)
    if sum(alpha_s) % outer_field_size == a:
        print("Alpha reconstructs correctly")
    else:
        print("Not this time....", sum(alpha_s), alpha_s, a)

    betas = {}
    for i_, value in enumerate(triple):
        betas["s_{}_{}".format(shareholders_[i_][0], shareholders_[i_][1])] = triple[value][1]
    b, b_f, _, _, _ = reconstruct(setup, random_subset=False, subset=betas, print_statements=False)
    if sum(beta_s) % outer_field_size == b:
        print("Beta reconstructs correctly")
    print("alpha: {}, beta: {}".format(a, b))
    print(a_f, "\n", b_f)
    p = multiply_polynomials(a_f, b_f, outer_field_size)
    derivatives_p = calc_derivative_vector(p, len(triple)-1, outer_field_size)
    results = []
    for shareholder in shareholders_:
        results.append(calc_function(derivatives_p[shareholder[1]], shareholder[0], outer_field_size))
    print(results)
    for i, gamma in enumerate(gammas):
        assert gammas[gamma] == results[i], "computed gamma-values are incorrect"
        print("{}, gamma share = {}, result of shareholder in p(x) = {} (correct)".format(gamma, gammas[gamma], results[i]))
    print("\n")
    return triple, shareholders_, a, b


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


# result = multiply_polynomials([[5, 0], [1, 1], [3, 2]], [[3, 0], [2, 1], [1, 2]], 997)
# print(result)
# test_pre_mult("1,2,3")
