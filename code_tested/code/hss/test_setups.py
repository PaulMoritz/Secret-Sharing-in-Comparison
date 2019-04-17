import pandas as pd
import yaml
import random
from setup import *
from share import share
from reconstruct import reconstruct
from reconstruction_tools import dict_to_list
from determinant import *
from function_tools import print_function
from renew import renew
from reset import reset
from add import add
from add_tools import merge_data
from path import get_data_path
from linear import create_shares_for_messages
from multiply import multiply

# random.seed(42)

# path to DATA directory
data_path = get_data_path()

prime = 997
print_statements = False


# main testframe
# tests all given examples in 'tassa_setups.yaml' for setup, share, reconstruct, add, renew, reset, multiply
# (implicitly also pre_mult and linear)
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
            disjunctive_name = "{}_dis".format(name)
            for setup_name in [name, disjunctive_name]:
                print("Name: {}\nPeople per level: {}\nThresholds: {}".format(setup_name, people, thresholds))
                print("Field size is {}".format(prime))
                levels = merge_data(people, thresholds)
                random_message = random.randint(0, prime - 1)
                print("Generated message is {}".format(random_message))
                # setup
                test_setup(levels, setup_name)
                # share
                original_function, original_shares = test_share(random_message, setup_name)
                # reconstruct
                original_determinant, other_determinants = test_reconstruct(original_function, original_shares,
                                                                            random_message, setup_name, thresholds)
                # renew
                test_renew(random_message, setup_name)
                # reset
                old_shares = test_reset(levels, original_determinant, other_determinants, setup_name)
                # add
                test_add(old_shares, original_function, random_message, setup_name)
                # multiply
                test_multiply(setup_name)
                print("~" * 100)
    print("Operation successfully accomplished.")


def test_multiply(setup_name):
    shares_of_messages_for_multiply, _, _ = create_shares_for_messages(setup_name, np.random.randint(0, prime-1),
                                                                       np.random.randint(0, prime-1))
    print("\nCalling multiply('{}', {})".format(setup_name, shares_of_messages_for_multiply))
    shares = multiply(setup_name, shares_of_messages_for_multiply, print_statements=print_statements)
    print("Multiply successful. Computed messages: {}".format(shares))


def test_add(old_shares, original_function, random_message, setup_name):
    # get all possible shareholder IDs to be added
    max_options = get_options_for_add(old_shares)
    # call add on each of those options
    for option in max_options:
        print("\nCalling add('{}', {}, {}".format(setup_name, old_shares, option))
        add_shares, add_result = add(setup_name, old_shares, option, print_statements=print_statements,
                                     function_f=original_function)
        if add_shares == add_result == -1:
            print("add could not be tested due to overflow in linear reconstruction\n\n\n")
        else:
            print("New shares after add {} are:".format(option))
            for each_share in add_shares:
                print(each_share, ":", add_shares[each_share])
            if add_result == random_message:
                print("Shareholders reconstruct to message {}, add successful.".format(add_result))


# get all options for IDs that can be added
# e.g in a setup where (1,0) and (2,1) exist, possible options would be
# (3,0) or (3,1) -> Max person ID + 1 in all already existing levels
def get_options_for_add(old_shares):
    max_options = []
    j_s = []
    used = []
    share_list = dict_to_list(old_shares)
    for item in share_list:
        j_value = item[0].split('_')
        j_value = j_value[2]
        j_s.append(j_value)
    # search for all levels where we can add a person
    for idx, j in enumerate(j_s):
        try:
            if not j_s[idx] == j_s[idx + 1]:
                max_options.append(share_list[idx][0])
                used.append(j)
        except IndexError:
            if not j_s[idx] in used:
                max_options.append(share_list[idx][0])
                used.append(j)
    # save all options as a list
    max_options = [(int(item.split('_')[1]) + 1, int(item.split('_')[2])) for item in max_options]
    return max_options


def test_reset(levels, original_determinant, other_determinants, setup_name):
    other_determinants.insert(0, original_determinant)
    old_shares = old_shares_to_dict(setup_name)
    new_structure2 = create_new_level_structure(levels, levels[-1][0] + 3, levels[-1][1] + 3, 1)
    print("\nCalling reset('{}', {}, new_shares={}):".format(setup_name, old_shares, new_structure2))
    shares = reset(setup_name, old_shares, new_shares=new_structure2, print_statements=print_statements)
    print("New shares after reset are:")
    for each_share in shares:
        print(each_share, ":", shares[each_share])
    print("Reset successful.")
    return old_shares


# create a new level structure to reset the setup on
def create_new_level_structure(levels, people_in_last_level, threshold_in_last_level, structure):
    new_structure = levels.copy()
    new_structure[-1] = ([people_in_last_level, threshold_in_last_level])
    new_structure2 = levels.copy()
    new_structure2.append([1, levels[-1][1] + 1])
    if structure is 1:
        return new_structure
    else:
        return new_structure2


def test_renew(random_message, setup_name):
    print("\nCalling renew('{}', {}):"
          .format(setup_name, "{'shares': 'all'}"))
    resulting_shares, renew_result = renew(setup_name, {'shares': 'all'}, print_statements=print_statements)
    print("Resulting shares after renew are:")
    for each_share in resulting_shares:
        print("{} : {}".format(each_share, resulting_shares[each_share]))
    if renew_result == random_message:
        print("New Result ({}) is the same as the original message, renew successful.".format(renew_result))
    else:
        print("WTF?! {} != {} (in renew)".format(renew_result, random_message))


def test_reconstruct(original_function, original_shares, random_message, setup_name, thresholds):
    print("\nCalling reconstruct('{}', number_of_people={}, "
          "random_subset=True, subset={{}}, print_statements=False):"
          .format(setup_name, thresholds[-1]))
    try:
        secret, resulting_function, original_determinant, other_determinants, matrix \
            = reconstruct(setup_name, thresholds[-1], print_statements=print_statements)
    except TypeError as e:
        print("Could not reconstruct to a valid integer-result (test_setups): {}".format(e))
        sys.exit(1)
    if not secret == random_message:
        print("Reconstruction in setup {} calculated an incorrect result (should be {} but was {})"
              .format(setup_name, random_message, secret))
        sys.exit(1)
    else:
        print("The reconstructed function is\t{}, the message is\t{}\n\t"
              "(Original function was\t{} with secret\t{})"
              .format(print_function(resulting_function, printed=False), secret,
                      print_function(original_function, printed=False), random_message))
    print("\nOriginal shares were:")
    for each_share in original_shares:
        print(each_share, ":", original_shares[each_share])
    return original_determinant, other_determinants


def test_share(random_message, setup_name):
    print("\nCalling share('{}', {}, prime_number={}, print_statements=False):"
          .format(setup_name, random_message, prime))
    original_function, original_shares = share(setup_name, random_message, field_size=prime,
                                               print_statements=print_statements)
    return original_function, original_shares


def test_setup(levels, setup_name):
    delete_setup(setup_name)
    print("\nCalling setup('{}', {}):".format(setup_name, levels))
    setup(setup_name, levels, field_size=prime)


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
