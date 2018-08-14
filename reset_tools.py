import random
import os
from share_tools import read_level_stats
import re
import pandas as pd
import numpy as np

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")

np.random.seed(42)


def create_new_shares(number_of_shares, number_of_levels):
    shares = []
    for index in range(number_of_shares):
        shares.append("s_{}_{}".format(index, random.randint(0, number_of_levels)))
    shares = sorted(shares, key=lambda x: int(re.search(r'\d+$', x).group()))
    return shares


def shareholders_valid(data, shares):
    tuples = [tuple(x) for x in data.values[2:]]
    for share in shares:
        if share not in tuples:
            print(share, tuples)
            return False
    return True

