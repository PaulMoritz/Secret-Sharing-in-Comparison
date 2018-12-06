import numpy.random as random
import os
import math
from linear import linear
from read_and_write_data import read_field_size, read_data
from function_tools import generate_function, calc_function
from reconstruction_tools import calc_derivative_vector, shareholder_share_list_to_lists, sort_coordinates, divide
from determinant import *
from add_tools import randomly_split, compute_derivative_of_interpolation_polynomial, binomial_coefficient
from reconstruct import reconstruct

random.seed(42)

# get path to DATA directory
cwd = os.getcwd()
main_directory = os.path.abspath(os.path.join(cwd, os.pardir))
data_path = os.path.join(main_directory, "DATA")


# proposed PreMult algorithm
def pre_mult(setup):
    # get all needed data, i.e. field size, highest threshold, IDs of all shareholder
    global all_lambda, all_mu, all_lambda_values, all_mu_values, alpha_and_beta_shares
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
    print(matrix)
    # r = number of shareholders participating
    r = len(shareholders)
    # first step: choose alpha and beta
    all_new_shares_alpha = np.zeros((r, r))
    all_new_shares_beta = np.zeros((r, r))

    # testing only
    alpha_fct = [None] * r
    beta_fct = [None] * r
    alpha_secrets = [None] * r
    beta_secrets = [None] * r

    for i, shareholder in enumerate(shareholders):
        # call rand_shares to compute alpha and beta-shares
        # 2nd and 3rd value only for testing, delete later
        all_new_shares_alpha[i], alpha_secrets[i], alpha_fct[i] = rand_shares(field_size, shareholders, thresholds)
        all_new_shares_beta[i], beta_secrets[i], beta_fct[i] = rand_shares(field_size, shareholders, thresholds)
    all_alpha_shares = [None] * r
    all_beta_shares = [None] * r
    print(alpha_secrets, beta_secrets)
    # sum over all alpha shares of one ID and append a '1' to call linear
    for j in range(r):
        tmp_alpha = []
        tmp_beta = []
        for i in range(r):
            tmp_alpha.append((1, int(all_new_shares_alpha[i][j])))
            tmp_beta.append((1, int(all_new_shares_beta[i][j])))
        all_alpha_shares[j] = tmp_alpha
        all_beta_shares[j] = tmp_beta
    summed_alpha_shares, summed_beta_shares = [], []
    # call linear to compute the sum (step 4 in rand_shares)
    # iterate over all alphas of one share to be able to recursively call linear
    for i in range(r):
        summed_alpha_shares.append(linear(all_alpha_shares[i], field_size))
        summed_beta_shares.append(linear(all_beta_shares[i], field_size))
    '''
    print("All calculated shares for alpha:\n", all_new_shares_alpha)
    print("All calculated shares for beta:\n", all_new_shares_beta)
    summed_alpha_shares = np.sum(all_new_shares_alpha, axis=0) % field_size
    summed_beta_share = np.sum(all_new_shares_beta, axis=0) % field_size
    '''
    print(all_alpha_shares, all_beta_shares)
    summed_alpha_shares = [18, 28, 12]
    summed_beta_shares = [22, 33, 14]
    print("sums (each column represents a shareholder), alpha=", summed_alpha_shares, "beta=", summed_beta_shares)
    # second step: compute delta and epsilon
    max_j = max([shareholder[1] for shareholder in shareholders])
    # each shareholder s_l performs the following steps
    assert(r >= 1), "Can't calculate lambda and mu values"
    for l in range(1, r + 1):
        print("L is ", l)
        # whole computation of delta and epsilon values
        all_lambda, all_mu, all_lambda_values, all_mu_values, alpha_and_beta_shares = \
            create_lambda_and_mu_matrices(field_size, l, matrix, r, shareholders, summed_alpha_shares,
                                          summed_beta_shares, max_j, t)
    # tmp_lambda/mu: in each list for 'l,(i,j)' are the splitted values saved for l, i, j with m € 0...j
    lambda_m = np.split(all_lambda, max_j + 1, axis=1)
    mu_m = np.split(all_mu, max_j + 1, axis=1)
    # temporary variables for testing
    lambda_to_sum = np.split(all_lambda_values, r, axis=0)
    mu_to_sum = np.split(all_mu_values, r, axis=0)
    print(lambda_m, "\n\n", mu_m)
    summed_delta = [None] * (max_j + 1)
    summed_epsilon = [None] * (max_j + 1)
    lambda_non_split = np.zeros((r, max_j + 1))
    mu_non_split = np.zeros((r, max_j + 1))
    # for comparison we take the calculated values and sum them without the distribution, to verify it
    # must be deleted afterwards!
    for i in range(r):
        lambda_non_split = np.add(lambda_non_split, lambda_to_sum[i]) % field_size
        mu_non_split = np.add(mu_non_split, mu_to_sum[i]) % field_size
    lambda_non_split = np.split(lambda_non_split, max_j + 1, axis=1)
    mu_non_split = np.split(mu_non_split, max_j + 1, axis=1)
    # end of delete
    for m in range(max_j + 1):
        delta = np.zeros((r, r))
        epsilon = np.zeros((r, r))
        delta_split = np.split(lambda_m[m], r)
        epsilon_split = np.split(mu_m[m], r)
        print("Delta-split\n", delta_split)
        print("Epsilon-split\n", epsilon_split)
        for i in range(r):
            delta = np.add(delta, delta_split[i]) % field_size
            epsilon = np.add(epsilon, epsilon_split[i]) % field_size
        print("summed delta/epsilon:\n", delta, "\n\n", epsilon)
        summed_delta[m] = np.sum(delta, axis=1) % field_size
        summed_epsilon[m] = np.sum(epsilon, axis=1) % field_size
    print("All summed, delta\n", summed_delta, "\nepsilon\n", summed_epsilon)
    # print("Compare: delta\n", lambda_non_split, "\nepsilon\n", mu_non_split)
    # testing only, delete afterwards
    for m in range(max_j + 1):
        for i in range(r):
            assert((summed_delta[m][i] == lambda_non_split[m][i]) and
                   (summed_epsilon[m][i] == mu_non_split[m][i]))
    print("Distribution of lambda/mu correct")
    # end of delete
    print("alpha_beta ", alpha_and_beta_shares)
    # third step: compute gammas
    gammas_shared = {}
    computed_triple = {}
    # each shareholder gets their own gamma-share value
    for idx, shareholder in enumerate(shareholders):
        result = 0
        j = shareholder[1]
        print("Index", idx)
        # the sum in the calculation
        for m in range(j + 1):
            print(summed_delta, summed_delta[j-m][idx], "m=", m, "j=", j)
            print(summed_epsilon, summed_epsilon[j-m][idx], "m=", m, "j=", j)
            old_result = result
            result = (result + binomial_coefficient(j, m, field_size) *
                      int(summed_delta[j-m][idx]) * int(summed_epsilon[m][idx])) % field_size
            print(result % field_size, "=", old_result, "+", binomial_coefficient(j, m, field_size), "*",
                  int(summed_delta[j-m][idx]), "*", int(summed_epsilon[m][idx]))
        # display resulting shares
        print("Gamma_{} =".format(idx), result)
        gammas_shared[shareholder] = result
        # concatenate the gammas with the before-computed alphas and betas to form a triple for each shareholder
        computed_triple[shareholder] = (alpha_and_beta_shares[shareholder][0], alpha_and_beta_shares[shareholder][1],
                                        gammas_shared[shareholder])
    print(computed_triple)
    return computed_triple, shareholders, alpha_secrets, beta_secrets


# compute the delta and epsilon values used
def create_lambda_and_mu_matrices(field_size, l, matrix, r, shareholders, summed_alpha_shares, summed_beta_shares, max_j, t):
    alpha_and_beta_shares = {}
    # array with r^2 rows and r*(j + 1) columns
    all_lambda = np.zeros((r * r, r * (max_j + 1)))
    all_mu = np.zeros((r * r, r * (max_j + 1)))
    all_lambda_values = np.zeros((r * r, (max_j + 1)))
    all_mu_values = np.zeros((r * r, (max_j + 1)))
    # each shareholder performas the summations
    for i, shareholder in enumerate(shareholders):
        # stored for later processing
        alpha_and_beta_shares[shareholder] = [int(summed_alpha_shares[i]), int(summed_beta_shares[i])]
        # needs to be done for each m in 0...j
        for m in range(shareholder[1] + 1):
            # computation and split of lambda/mu values
            tmp_lambda, tmp_mu, lambda_l_m, mu_l_m = compute_and_split_lambda_mu(field_size, i, l, m, matrix, r,
                                                                                 shareholder, summed_alpha_shares,
                                                                                 summed_beta_shares, t)
            all_lambda_values[i + (l - 1) * r][m] = lambda_l_m
            all_mu_values[i + (l - 1) * r][m] = mu_l_m
            print("non- splitted lambda is\n", all_lambda_values, "non-splitted mu is\n", all_mu_values)
            print("splitted lambda is\n", tmp_lambda, "splitted mu is\n", tmp_mu)
            for item in tmp_lambda:
                print("Lambda: Current value", item, "from ", shareholder, "m=", m)
                for index in range(len(item)):
                    all_lambda[i + (l - 1) * r][r * m + index] = item[index]
            for item in tmp_mu:
                print("Mu: Current value", item, "from ", shareholder, "m=", m)
                for index in range(len(item)):
                    all_mu[i + (l - 1) * r][r * m + index] = item[index]
            print("put into matrices\n", all_lambda, "and mu\n", all_mu)
    return all_lambda, all_mu, all_lambda_values, all_mu_values, alpha_and_beta_shares


# computation of lambda and mu values, also the spiltting is done here
def compute_and_split_lambda_mu(field_size, i, l, m, matrix, r, shareholder, summed_alpha_shares, summed_beta_shares, t):
    tmp_lambda = []
    tmp_mu = []
    print("\ncalculating lambda_{}^{},{}".format(l, m, shareholder))
    lambda_l_m = (compute_derivative_of_interpolation_polynomial(
        determinant_of_original_matrix=determinant(matrix, field_size), field_size=field_size,
        i_value=shareholder[0], j_value=m, l_iterator=l, matrix=matrix,
        summation_boundary_t=t-1)
                  * int(summed_alpha_shares[i])) % field_size
    print("Computed lambda value is ", lambda_l_m)
    # split
    if lambda_l_m > 0:
        lambda_splitted = randomly_split(lambda_l_m, r)
    elif lambda_l_m == 0:
        lambda_splitted = [0] * r
    else:
        raise ValueError(
            "No split for value distribution possible(value < 0), lambda_i ={}".format(lambda_l_m))
    tmp_lambda.append(lambda_splitted)
    print("\ncalculating mu_{}^{},{}".format(l, m, shareholder))
    mu_l_m = (compute_derivative_of_interpolation_polynomial(
        determinant_of_original_matrix=determinant(matrix, field_size), field_size=field_size,
        i_value=shareholder[0], j_value=m, l_iterator=l, matrix=matrix,
        summation_boundary_t=t-1)
              * int(summed_beta_shares[i])) % field_size
    print("Computed mu value is ", mu_l_m)
    if mu_l_m > 0:
        mu_splitted = randomly_split(mu_l_m, r)
    elif mu_l_m == 0:
        mu_splitted = [0] * r
    else:
        raise ValueError("No split for value distribution possible(value < 0), mu_i ={}".format(mu_l_m))
    tmp_mu.append(mu_splitted)
    return tmp_lambda, tmp_mu, lambda_l_m, mu_l_m


# proposed RandShares algorithm
def rand_shares(field_size, shareholders, thresholds):
    computed_shares = []
    degree_of_function = thresholds[-1] - 1
    secret = np.random.randint(0, field_size)
    random_function = generate_function(degree_of_function, secret, field_size)
    print("function: ", random_function)
    derivatives = calc_derivative_vector(random_function, degree_of_function, field_size)
    for (i, j) in shareholders:
        computed_shares.append(calc_function(derivatives[j], i, field_size))
    print("Computed shares ", computed_shares, "(msg {})".format(secret))
    return computed_shares, secret, derivatives


# compute the lambda and mu values as in step 2
def compute_lambda_mu(alpha_beta, shareholder_id, l, t, matrix, field_size):
    # index off by one
    result = 0
    for k in range(shareholder_id[1] - 1, t):
        if k < 0:
            continue
        print("shareholder ", shareholder_id, "calculates summand for k=", k)
        (i, j) = shareholder_id
        k_term = divide(math.factorial(k), math.factorial(k - j + 1), field_size)
        minus_one_term = ((-1)**(l - 1 + k)) % field_size
        divided_determinant = divide(int(determinant(get_minor(matrix, l - 1, k), field_size)),
                                     determinant(matrix, field_size), field_size)
        i_term = i**(k - j + 1)
        former_result = result
        result = (result + (k_term * minus_one_term * divided_determinant * i_term) % field_size) % field_size
        print(result, "=", former_result, "+(", k_term, "*", minus_one_term, "*([",
              int(determinant(get_minor(matrix, l - 1, k), field_size)), "/",
              determinant(matrix, field_size), "=", divided_determinant, "])*", i_term, ")")
    return (alpha_beta * result) % field_size



def test_pre_mult():
    outer_field_size = read_field_size("1,2,3")
    triple, shareholders_, alpha_s, beta_s = pre_mult("1,2,3")
    gammas = {}
    print("TRIPLE", triple)
    for i_, value in enumerate(triple):
        gammas["s_{}_{}".format(shareholders_[i_][0], shareholders_[i_][1])] = triple[value][2]
    c, _, _, _, _ = reconstruct("1,2,3", random_subset=False, subset=gammas, print_statements=False)

    alphas = {}
    for i_, value in enumerate(triple):
        alphas["s_{}_{}".format(shareholders_[i_][0], shareholders_[i_][1])] = triple[value][0]
    a, a_f, _, _, _ = reconstruct("1,2,3", random_subset=False, subset=alphas, print_statements=False)
    if sum(alpha_s) % outer_field_size == a:
        print("Alpha reconstructs correctly")
    else:
        print("Not this time....", sum(alpha_s), alpha_s, a)

    betas = {}
    for i_, value in enumerate(triple):
        betas["s_{}_{}".format(shareholders_[i_][0], shareholders_[i_][1])] = triple[value][1]
    b, b_f, _, _, _ = reconstruct("1,2,3", random_subset=False, subset=betas, print_statements=False)
    if sum(beta_s) % outer_field_size == b:
        print("Beta reconstructs correctly")
    print("alpha: {}, beta: {}, gamma: {}".format(a, b, c))
    if a*b % outer_field_size == c:
        print("YYYYYAAAAAAAAAASSSSSSSSSSSSSSEOEOEOEOEOEOEOEOEOEOEOEOAAAAAAAAAOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOEOOOEOOEEEOEOOEEOOEOOEOOEOEOOEOEOEOOEOEOEOEOSSS")
    else:
        print("a*b = {}, try again".format(a*b % outer_field_size))
    # print(a_f, "\n", b_f)


test_pre_mult()
