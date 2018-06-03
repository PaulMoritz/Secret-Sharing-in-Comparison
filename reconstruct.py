import os
from tools import *
import pandas as pd

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")


# reconstruct([["s1_2", 4], ["s3_2", 3]])
# alternative formats: "s1,2" ; "1,2" ; "1_2"
def reconstruct(setup, share_list):
    shares = []
    coordinates = []
    filepath = os.path.join(datapath, setup, 'shares.csv')
    data = pd.read_csv(filepath, skiprows=1, header=None, delimiter=',', )
    for i, shareholder in enumerate(share_list):
        if not len(shareholder) is 2:
            print("Invalid input: " + str(len(shareholder)) + " arguments given in shareholder-list [" + str(i) +"]")
            return
        shares.append(shareholder[1])
        # TODO more cases?
        if '_' in shareholder[0]:
            if 's_' in shareholder[0] or 'S_' in shareholder[0]:
                shareholder[0] = shareholder[0][2:]
            name = shareholder[0].split('_')
        elif ',' in shareholder[0]:
            name = shareholder[0].split(',')
        else:
            print("Can't read format for shareholder {}, you need a separator like '_'/','; eg. S1_0".format(i))
            return
        name[0] = name[0].strip('s')
        name[0] = name[0].strip('S')

        coordinates.append((name[0], name[1]))
    print(coordinates)
    matrix, highest_derivative = interpolation_matrix(coordinates)
    if requirement_1(matrix, highest_derivative, len(share_list)):
        print("Requirement 1 'Unique Solution' is satisfied.")
    else:
        print("Requirement 1 'Unique Solution' not satisfied with given subset.")
        return


reconstruct("another_example", [["3_1", 4], ["S_2_1", 3], ["s1,0", 5], ["4,1", 4]])
