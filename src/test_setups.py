import sys
import os
import pandas as pd
import yaml
import random
import numpy as np
from setup import *
from share import share
from reconstruct import reconstruct
from reconstruction_tools import  print_matrix, dict_to_list
from determinant import *
from function_tools import print_function
from renew import renew
from reset import reset
from add import add
from add_tools import merge_data
from path import get_data_path

# random.seed(42)

# path to DATA directory
data_path = get_data_path()

prime = 997


def main():
    print("\n" * 10)

    with open("tassa_setups.yaml", 'r') as stream:
        try:
            docs = yaml.load_all(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)
        for doc in docs:
            thresholds = doc['thresholds']
            people = doc['people']
            name = doc['name']
            print("Name: {}\nPeople per level: {}\nThresholds: {}".format(name, people, thresholds))
            print("Field size is {}".format(prime))
            levels = merge_data(people, thresholds)
            random_message = random.randint(0, prime - 1)
            fixed_message = 42
            print("Generated message is {}".format(random_message))

            # setup
            delete_setup(doc['name'])
            print("\nCalling setup('{}', {}):".format(name, levels))
            setup(name, levels, field_size=prime)

            # share
            print("\nCalling share('{}', {}, prime_number={}, print_statements=False):"
                  .format(name, random_message, prime))
            original_function, original_shares = share(name, random_message, field_size=prime, print_statements=True)

            # reconstruct
            print("\nCalling reconstruct('{}', number_of_people={}, "
                  "random_subset=True, subset={{}}, print_statements=False):"
                  .format(name, thresholds[-1]))
            try:
                secret, resulting_function, original_determinant, other_determinants, matrix\
                    = reconstruct(name, thresholds[-1], print_statements=True)
            except TypeError as e:
                print("Could not reconstruct to a valid integer-result (test_setups): {}".format(e))
                sys.exit(1)
            if not secret == random_message:
                print("Reconstruction in setup {} calculated an incorrect result (should be {} but was {})"
                      .format(name, random_message, secret))
                sys.exit(1)
            else:
                print("The reconstructed function is\t{}, the message is\t{}\n\t"
                      "(Original function was\t{} with secret\t{})"
                      .format(print_function(resulting_function, printed=False), secret,
                              print_function(original_function, printed=False), random_message))

            print("\nOriginal shares were:")
            for each_share in original_shares:
                print(each_share, ":", original_shares[each_share])

            # renew
            print("\nCalling renew('{}', {}):"
                  .format(name, "{'shares': 'all'}"))
            resulting_shares, renew_result = renew(name, {'shares': 'all'}, print_statements=False)
            print("Resulting shares after renew are:")
            for each_share in resulting_shares:
                print("{} : {}".format(each_share, resulting_shares[each_share]))
            if renew_result == random_message:
                print("New Result ({}) is the same as the original message, renew successful.".format(renew_result))
            else:
                print("WTF?! {} != {} (in renew)".format(renew_result, random_message))

            # reset
            other_determinants.insert(0, original_determinant)
            old_shares = old_shares_to_dict(name)
            new_structure = levels.copy()
            new_structure[-1] = ([levels[-1][0] + 3, levels[-1][1] + 3])
            new_structure2 = levels.copy()
            new_structure2.append([1, levels[-1][1] + 1])
            # new_structure2.append([1, new_structure2[-1][1] + 1])

            # new_structure.append([1, levels[-1][1] + 1])
            print("\nCalling reset('{}', {}, new_shares={}):".format(name, old_shares, new_structure2))
            shares = reset(name, old_shares, new_shares=new_structure2, print_statements=False)
            print("New shares after reset are:")
            for each_share in shares:
                print(each_share, ":", shares[each_share])
            print("Reset successful.")

            # add
            max_options = []
            j_s = []
            used = []
            share_list = dict_to_list(old_shares)
            for item in share_list:
                j_value = item[0].split('_')
                j_value = j_value[2]
                j_s.append(j_value)
            for idx, j in enumerate(j_s):
                try:
                    if not j_s[idx] == j_s[idx + 1]:
                        max_options.append(share_list[idx][0])
                        used.append(j)
                except IndexError:
                    if not j_s[idx] in used:
                        max_options.append(share_list[idx][0])
                        used.append(j)
            max_options = [(int(item.split('_')[1]) + 1, int(item.split('_')[2])) for item in max_options]
            for option in max_options:
                print("\nCalling add('{}', {}, {}".format(name, old_shares, option))
                add_shares, add_result = add(name, old_shares, option, print_statements=True,
                                             function_f=original_function)
                print("New shares after add {} are:".format(option))
                for each_share in add_shares:
                    print(each_share, ":", add_shares[each_share])
                if add_result == random_message :
                    print("Shareholders reconstruct to message {}, add successful.".format(add_result))
            print("="*211, "\n\n")


def old_shares_to_dict(name):
    all_shares = {}
    shares_path = os.path.join(data_path, name, 'shares.csv')
    shares = pd.read_csv(shares_path, skiprows=0, header=0, delimiter=',', )
    tuples = [tuple(x) for x in shares.values]
    for (x, y) in tuples:
        all_shares[x] = y
    print(all_shares)
    return all_shares


if __name__ == '__main__':
    main()
