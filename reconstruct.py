from tools import derivate_function
from tools import print_function
from tools import calc_function
from tools import interpolation_matrix


# reconstruct([["s1_2", 4], ["s3_2", 3]])
# alternative formats: "s1,2" ; "1,2" ; "1_2"
def reconstruct(share_list):
    shares = []
    coordinates = []
    for i, shareholder in enumerate(share_list):
        if not len(shareholder) is 2:
            print("Invalid input: " + str(len(shareholder)) + " arguments given in shareholder-list [" + str(i) +"]")
            return
        shares.append(shareholder[1])
        # TODO more cases?
        if '_' in shareholder[0]:
            name = shareholder[0].split('_')
            name[0] = name[0].strip('s')
        elif ',' in shareholder[0]:
            name = shareholder[0].split(',')
            name[0] = name[0].strip('s')
            print(name)
        coordinates.append((name[0], name[1]))
        print(coordinates)
    interpolation_matrix(coordinates)


reconstruct([["2_1", 4], ["3_2", 3], ["s1,0", 5]])
