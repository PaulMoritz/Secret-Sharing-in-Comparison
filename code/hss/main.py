"""
Main module that can be used to call functionality directly from the console.

Examples (Not yet created):
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
import test_setups

# save arguments from the console-input
arguments = sys.argv


# direct call of main.py executes the following code to set up and call the corresponding methods
if __name__ == "__main__":
    # create modes of different execution possibilities (from the input parameters)
    MODE_SETUP = "setup"
    MODE_SHARE = "share"
    MODE_RECONSTRUCT = "reconstruct"
    MODE_RENEW = "renew"
    MODE_TEST = "test"
    VALID_MODES = [MODE_SETUP, MODE_SHARE, MODE_RECONSTRUCT, MODE_RENEW, MODE_TEST]

    # additional modes for the different functionality in setup
    SETUP_DELETE = "delete"
    SETUP_LIST = "list"
    SETUP_INFO = "info"
    SETUP_DEFAULT = "_"
    VALID_SETUP = [SETUP_DELETE, SETUP_LIST, SETUP_INFO]

    # catch case of to few arguments given
    if arguments is None or len(arguments) < 2 or (len(arguments) < 3 and not arguments[1] == MODE_TEST):
        sys.stderr.write("Please specify a mode and at least the setup name. ")
        sys.stderr.write("For example: python main.py setup ExampleName [[1,1],[3,2],[4,4]]")
        sys.exit(1)

    # save current mode
    mode = arguments[1]

    if mode not in VALID_MODES:
        sys.stderr.write("Please select a mode which is one of {}, currently mode is {}".format(VALID_MODES, mode))
        sys.exit(1)

    print("Running in mode '%s'" % mode)

    # case of 'setup'
    if mode == MODE_SETUP:
        if len(arguments) is 3:
            # only list_setups() needs no additional parameters, check if it shall be called
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
            # choose correct call from the given arguments, print the called method with all used parameters
            if setup_function == SETUP_DELETE:
                print("Calling setup_delete('{}'):\n".format(setup_name))
                delete_setup(setup_name)
            elif setup_function == SETUP_LIST:
                print("Calling list_setups():\n")
                list_setups()
            elif setup_function == SETUP_INFO:
                print("Calling get_info('{}'):\n".format(setup_name))
                get_info(setup_name)
            # else case is creating a new setup
            else:
                try:
                    # convert string of a list to list
                    structure = ast.literal_eval(arguments[3])
                    print("Calling setup('{}', {}):\n".format(setup_name, structure))
                    setup(setup_name, structure)
                except ValueError:
                    print("Error in reading setup mode; Input was '{}', needs to be either one of {} "
                          "or a valid level structure."
                          .format(setup_function, VALID_SETUP))
        else:
            print("Wrong number of arguments ({}) in {}".format(len(arguments), MODE_SETUP))
            sys.exit(1)

    # case of 'share'
    elif mode == MODE_SHARE:
        # check for correct number of arguments
        if len(arguments) <= 3 or len(arguments) > 6:
            print("Wrong number of arguments ({}) in {}".format(len(arguments), MODE_SHARE))
            sys.exit(1)
        # default value
        prime_number = 997
        name = ''
        setup_name = arguments[2]
        print(arguments)
        try:
            secret_message = int(arguments[3])
        except ValueError:
            print("Secret needs to be an integer value, not '{}'".format(arguments[3]))
            sys.exit(1)

        # set prime number only if given (default possible)
        if len(arguments) >= 5:
            try:
                prime_number = int(arguments[4])
            except ValueError:
                print("Prime number needs to be an integer value, but is {}.".format(arguments[4]))
                sys.exit(1)
        # for multiple generations of share values pick a unique name and
        # create share values for this name (under the given structure)
        if len(arguments) is 6:
            try:
                name = arguments[5]
                print("Calling share('{}', {}, prime_number={}, name={}):\n"
                      .format(setup_name, secret_message, prime_number, name))
            except ValueError:
                print("Damn son.")
                sys.exit(1)
        else:
            print("Calling share('{}', {}, prime_number={}):\n".format(setup_name, secret_message, prime_number))
        share(setup_name, secret_message, prime_number, name)

    # case 'reconstruct':
    elif mode == MODE_RECONSTRUCT:
        setup_name = arguments[2]
        # decision between random and given subset, here: random, only number of people needed
        if len(arguments) is 4:
            number_of_random_people = int(arguments[3])
            print("Calling reconstruct('{}', number_of_people={}, random_subset=True, subset={{}}):\n"
                  .format(setup_name, number_of_random_people))
            reconstruct(setup_name, number_of_people=number_of_random_people)
        # specific subset case, the 4. argument needs to be 'False' to be handled correctly
        elif len(arguments) is 5:
            random_subset = arguments[3]
            print(random_subset)
            random_subset = str2bool(random_subset)
            # error handling
            assert (random_subset is False), "If a specific subset is chosen, 'False' needs to be set, for example\n" \
                                             "python main.py reconstruct CMD_test False" \
                                             "{'s_1_0':'6','s_1_1':'14','s_2_1':'7','s_3_1':'10','s_1_2':'19'}"
            # convert string of list to list
            subset = ast.literal_eval(arguments[4])
            print("Calling reconstruct('{}', number_of_people=0, random_subset=False, subset={}):\n"
                  .format(setup_name, subset))
            reconstruct(setup_name, random_subset=random_subset, subset=subset)
        else:
            # check for correct number of arguments
            print("Wrong number of arguments ({}) in {}:\n{}".format(len(arguments), MODE_RECONSTRUCT, arguments))

    # case 'renew'
    elif mode == MODE_RENEW:
        # check for correct number of arguments
        if not len(arguments) is 4:
            print("Wrong number of arguments ({}) in {}, format should be\n"
                  "['main.py', 'renew', 'setup_name', 'old_shares'] but is\n{}"
                  .format(len(arguments), MODE_RENEW, arguments))
            sys.exit(1)
        setup_name = arguments[2]
        try:
            old_shares = ast.literal_eval(arguments[3])
        except ValueError:
            print("Old_shares can't be parsed, please make sure to provide "
                  "a correct dictionary of shareholder:share pairs or the exact term {'shares':'all'}")
            sys.exit(1)
        except SyntaxError:
            print("Old_shares can't be parsed, please make sure you use the exact term "
                  "{'shares':'all'} for all shareholders, without 'old_shares=',"
                  "or a correct dictionary of shareholder:share pairs")
            sys.exit(1)
        print("Calling renew('{}', {}):\n"
              .format(setup_name, old_shares))
        renew(setup_name, old_shares)

    elif mode == MODE_TEST:
        if not len(arguments) == 2:
            print("Wrong number of arguments, Mode 'test' does not support further parameters.")
            sys.exit(1)
        else:
            test_setups.main()
