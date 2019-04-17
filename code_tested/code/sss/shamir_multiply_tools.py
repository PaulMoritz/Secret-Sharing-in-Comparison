import os, sys
hss = os.path.join(os.pardir, "hss")
sys.path.append(hss)
from function_tools import generate_function, calc_function, print_function
from linear import linear
from read_and_write_data import read_field_size
from lagrange_interpolation import reconstruct
from shamir_add import read_shares
from shamir_share import make_random_shares
import numpy as np


# proposed RandShares algorithm
def rand_shares_calculation(field_size, shareholders, polynomial):
    computed_shares = []

    # print("Function: ", print_function(polynomial, printed=False))
    for (i, _) in shareholders:
        computed_shares.append(calc_function(polynomial, i, field_size))
    # print("Computed shares ", computed_shares)
    return computed_shares


def rand_shares_summation(computed_shares, field_size, r):
    all_shares = [None] * r
    # sum over all alpha shares of one ID and append a '1' (neutral element for multiplication) to call linear
    for j in range(r):
        tmp_shares = []
        for i in range(r):
            tmp_shares.append((1, int(computed_shares[i][j])))
        all_shares[j] = tmp_shares
    summed_shares = []
    # call linear to compute the sum (step 4 in rand_shares)
    # iterate over all alphas of one share to be able to recursively call linear
    for i in range(r):
        summed_shares.append(linear(all_shares[i], field_size))
    return summed_shares


def pre_mult(setup, print_statements=True):
    field_size, r, shareholders, degree_of_function, k, n = get_setup_info(setup)
    # first step: choose alpha and beta
    shares_of_alpha, shares_of_beta, shares_of_r, shares_of_r_star, s_alpha, s_beta =\
        call_and_apply_rand_shares(k, field_size, r, shareholders)
    '''
    shares_of_alpha = {1: 12, 2: 17, 3: 22, 4: 27}
    shares_of_beta = {1: 14, 2: 19, 3: 24, 4: 29}
    shares_of_r = {1: 17, 2: 25, 3: 33, 4: 41}
    shares_of_r_star = {1: 16, 2: 46, 3: 108, 4: 214}
    s_alpha = 7
    s_beta = 9
    '''
    if print_statements:
        print("[alpha]", shares_of_alpha, "\n",
              "[beta]", shares_of_beta, "\n",
              "[r]", shares_of_r, "\n",
              "[R]", shares_of_r_star)
    shares_of_d = {}
    for (i, _) in shareholders:
        shares_of_d[i] = (((shares_of_alpha[i] * shares_of_beta[i]) % field_size)
                          + shares_of_r_star[i]) % field_size
        # print(shares_of_d[i], "=", shares_of_alpha[i], "*", shares_of_beta[i], "+", shares_of_r_star[i])
    # reconstruct d with access structure (2k, n)
    d, p = reconstruct("{},{}".format(k*2, n), shares_of_d, field_size)
    shares_of_gamma = {}
    for (i, _) in shareholders:
        shares_of_gamma[i] = (d - shares_of_r[i]) % field_size
        if print_statements:
            print(shares_of_gamma[i], "=", d, "-", shares_of_r[i])
    g, poly = reconstruct(setup, shares_of_gamma, field_size)
    if print_statements:
        print("Reconstructed gamma:", g, "Polynomial:", print_function(poly, False))
    assert (s_alpha * s_beta) % field_size == g, "{}*{} (={}) != {}".format(s_alpha, s_beta, (s_alpha * s_beta) % field_size, g)
    if print_statements:
        print("Successfully created alpha, beta and gamma values")
    triples = {}
    for id in shares_of_alpha:
        triples[id] = (shares_of_alpha[id], shares_of_beta[id], shares_of_gamma[id])
    if print_statements:
        print(triples)
    return triples, s_alpha, s_beta


def call_and_apply_rand_shares(k, field_size, r, shareholders):
    all_new_shares_alpha = np.zeros((r, r))
    all_new_shares_beta = np.zeros((r, r))
    all_new_shares_r_i = np.zeros((r, r))
    all_new_shares_r_i_star = np.zeros((r, r))

    alpha_shares = {}
    beta_shares = {}
    r_i_shares = {}
    r_i_star_shares = {}
    secret_alphas = [None] * r
    secret_betas = [None] * r
    secret_r_is = [None] * r
    for i in range(r):
        secret_alphas[i] = np.random.randint(0, field_size)
        secret_betas[i] = np.random.randint(0, field_size)
        secret_r_is[i] = np.random.randint(0, field_size)
    secret_alpha = sum(secret_alphas) % field_size
    secret_beta = sum(secret_betas) % field_size

    for i, shareholder in enumerate(shareholders):
        random_function_alpha = generate_function(k-1, secret_alphas[i], field_size)
        random_function_beta = generate_function(k-1, secret_betas[i], field_size)
        random_function_r_i = generate_function(k-1, secret_r_is[i], field_size)
        random_function_r_i_star = generate_function(2*(k-1), secret_r_is[i], field_size)

        all_new_shares_alpha[i] = rand_shares_calculation(field_size, shareholders, random_function_alpha)
        all_new_shares_beta[i] = rand_shares_calculation(field_size, shareholders, random_function_beta)
        all_new_shares_r_i[i] = rand_shares_calculation(field_size, shareholders, random_function_r_i)
        all_new_shares_r_i_star[i] = rand_shares_calculation(field_size, shareholders, random_function_r_i_star)
    # print("ALPHA", all_new_shares_alpha)
    # print("BETA", all_new_shares_beta)

    summed_alpha_shares = rand_shares_summation(all_new_shares_alpha, field_size, r)
    summed_beta_shares = rand_shares_summation(all_new_shares_beta, field_size, r)
    summed_r_i_shares = rand_shares_summation(all_new_shares_r_i, field_size, r)
    summed_r_i_star_shares = rand_shares_summation(all_new_shares_r_i_star, field_size, r)
    # print("-->", summed_alpha_shares, summed_beta_shares, summed_r_i_shares, summed_r_i_star_shares)
    for idx, (i, _) in enumerate(shareholders):
        alpha_shares[i] = summed_alpha_shares[idx]
        beta_shares[i] = summed_beta_shares[idx]
        r_i_shares[i] = summed_r_i_shares[idx]
        r_i_star_shares[i] = summed_r_i_star_shares[idx]
    # print(secret_alphas, random_function_alpha, "\n", secret_betas, random_function_beta)

    return alpha_shares, beta_shares, r_i_shares, r_i_star_shares, secret_alpha, secret_beta


def get_setup_info(setup):
    field_size = read_field_size(setup, hierarchical=False)
    shareholders = read_shares(setup, double=True)

    print("Shareholders:", shareholders)
    k, n = setup.split(',')
    k, n = int(k), int(n)
    degree_of_function = k - 1
    # r = number of shareholders participating
    r = len(shareholders)
    return field_size, r, shareholders, degree_of_function, k, n


# _, _, shares = make_random_shares(2, 4, 42, 997)
# pre_mult("2,4")
