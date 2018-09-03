"""
Main module that can be used to call functionality directly from the console.

Examples:
    # Setup
        new setup:
            python main.py setup CMD_test [[1,1],[3,2],[4,4]]
        delete setup:
            python main.py setup CMD_test delete
        get setup information:
            python main.py setup CMD_test get
        list all created setups:
            python main.py setup CMD_test list

    # Share
        python main.py share CMD_test 5

    # Reconstruct
        random people:
            python main.py reconstruct CMD_test 6
        specific subset:
            python main.py reconstruct CMD_test False {'s_1_0':'6','s_1_1':'14','s_2_1':'7','s_3_1':'10','s_1_2':'19'}

    # Renew
        python main.py renew CMD_test {'s_1_0':'6','s_1_1':'14','s_2_1':'7','s_3_1':'10','s_1_2':'19'}
"""
import sys
import ast
from setup import setup, get_info, delete_setup, list_setups, str2bool
from share import share
from reconstruct import reconstruct
from renew import renew

# save arguments from the console-input
arguments = sys.argv


# direct call of main.py executes the following code to set up and call the corresponding methods
if __name__ == "__main__":
    # create modes of different execution possibilities (from the input parameters)
    MODE_SETUP = "setup"
    MODE_SHARE = "share"
    MODE_RECONSTRUCT = "reconstruct"
    MODE_RENEW = "renew"
    VALID_MODES = [MODE_SETUP, MODE_SHARE, MODE_RECONSTRUCT, MODE_RENEW]

    # additional modes for the different functionality in setup
    SETUP_DELETE = "delete"
    SETUP_LIST = "list"
    SETUP_GET = "get"
    SETUP_DEFAULT = "_"
    VALID_SETUP = [SETUP_DELETE, SETUP_LIST, SETUP_GET]

    if arguments is None or len(arguments) < 3:
        sys.stderr.write("Please specify a mode and at least the setup name. ")
        sys.stderr.write("For example: python main.py setup ExampleName [[1,1],[3,2],[4,4]]")
        sys.exit(1)

    mode = arguments[1]

    if mode not in VALID_MODES:
        sys.stderr.write("Please select a mode which is one of %s" % VALID_MODES)
        sys.exit(1)

    print("Running in mode '%s'" % mode)

    if mode == MODE_SETUP:
        if len(arguments) is 3:
            if arguments[2] == SETUP_LIST:
                print("Calling list_setups():\n")
                list_setups()
            else:
                print("Error in reading setup mode; Input was '{}' but needs to be '{}' with only 3 arguments given."
                      "For other uses 4 arguments are needed"
                      .format(arguments[2], SETUP_LIST))
        elif len(arguments) is 4:
            setup_name = arguments[2]
            setup_function = str(arguments[3])
            if setup_function == SETUP_DELETE:
                print("Calling setup_delete({}):\n".format(setup_name))
                delete_setup(setup_name)
            elif setup_function == SETUP_LIST:
                print("Calling list_setups():\n")
                list_setups()
            elif setup_function == SETUP_GET:
                print("Calling get_info({}):\n".format(setup_name))
                get_info(setup_name)
            else:
                try:
                    structure = ast.literal_eval(arguments[3])
                    print("Calling setup({},{}):\n".format(setup_name, structure))
                    setup(setup_name, structure)
                except ValueError:
                    print("Error in reading setup mode; Input was '{}', needs to be either one of {} "
                          "or a valid level structure."
                          .format(setup_function, VALID_SETUP))
        else:
            print("Wrong number of arguments ({}) in {}".format(len(arguments), MODE_SETUP))
            sys.exit(1)

    elif mode == MODE_SHARE:
        if not (len(arguments) is 3 or len(arguments) is 4):
            print("Wrong number of arguments ({}) in {}".format(len(arguments), MODE_SHARE))
            sys.exit(1)
        prime_number = 31
        setup_name = arguments[2]
        secret_message = int(arguments[3])
        if len(arguments) is 5:
            prime_number = int(arguments[4])
        print("Calling share({}, {}, prime_number={}):\n".format(setup_name, secret_message, prime_number))
        share(setup_name, secret_message, prime_number)

    elif mode == MODE_RECONSTRUCT:
        setup_name = arguments[2]
        if len(arguments) is 4:
            number_of_random_people = int(arguments[3])
            print("Calling reconstruct({}, number_of_people={}, random_subset=True, subset={{}}):\n"
                  .format(setup_name, number_of_random_people))
            reconstruct(setup_name, number_of_people=number_of_random_people)
        elif len(arguments) is 5:
            random_subset = arguments[3]
            print(random_subset)
            random_subset = str2bool(random_subset)
            assert random_subset is False
            subset = ast.literal_eval(arguments[4])
            print("Calling reconstruct({}, number_of_people=0, random_subset=False, subset={}):\n"
                  .format(setup_name, subset))
            reconstruct(setup_name, random_subset=random_subset, subset=subset)
        else:
            print("Wrong number of arguments ({}) in {}:\n{}".format(len(arguments), MODE_RECONSTRUCT, arguments))

    elif mode == MODE_RENEW:
        if not len(arguments) is 4:
            print("Wrong number of arguments ({}) in {}, format should be\n"
                  "['main.py', 'renew', 'setup_name', 'old_shares'] but is\n{}"
                  .format(len(arguments), MODE_RENEW, arguments))
            sys.exit(1)
        setup_name = arguments[2]
        old_shares = ast.literal_eval(arguments[3])
        print("Calling renew({}, {}):\n"
              .format(setup_name, old_shares))
        renew(setup_name, old_shares)
