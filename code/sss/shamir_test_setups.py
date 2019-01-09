from lagrange_interpolation import reconstruct
from shamir_share import make_random_shares
from shamir_renew import shamir_renew
from shamir_add import shamir_add, choose_random_subset
from shamir_reset import shamir_reset
import random
import yaml
import sys
import os
hss = os.path.join(os.pardir, "HSS")
sys.path.append(hss)
from function_tools import print_function
from setup import delete_setup


def main():
    field_size = 997
    with open("shamir_setups.yaml", 'r') as stream:
        try:
            docs = yaml.load_all(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)
        for doc in docs:
            delete_setup(doc['setup'], hierarchical=False)
            setup = doc['setup']
            info = setup.split(',')
            minimum_number_of_shares = int(info[0])
            number_of_people = int(info[1])
            random_message = random.randint(0, field_size - 1)
            secret, polynomial, shares = make_random_shares(minimum_number_of_shares=minimum_number_of_shares,
                                                            number_of_people=number_of_people, message=random_message,
                                                            field_size=field_size)
            print("Setup", setup)
            print('secret:\t\t\t', secret)
            print('shares:', shares)
            print("f(x) =", print_function(polynomial, False))
            reconstructed = reconstruct(setup, shares, field_size)
            print('secret recovered:\t', reconstructed)
            assert (reconstructed == random_message), "Incorrect reconstruction"
            print("Reconstruction successful\n")

            # renew
            _, renew_result = shamir_renew(setup)
            assert (renew_result == random_message), "Incorrect reconstruction"
            print("Renew successful\n")
            # add
            _, add_shares = shamir_add(setup, shares, number_of_people+1, field_size)
            minimum_add_shares = choose_random_subset(add_shares, minimum_number_of_shares)
            print("Subset for reconstruction: ", minimum_add_shares)
            add_result = reconstruct(setup, minimum_add_shares, field_size)
            assert (add_result == random_message), "Incorrect reconstruction, {} != message {}"\
                .format(add_result, random_message)
            print("Add successful\n")
            # reset
            reset_shares, _ = shamir_reset(setup, "{},{}".format(minimum_number_of_shares+1, number_of_people+2))
            print("Reset successful\n")
            print("="*211, "\n\n")


if __name__ == '__main__':
    main()