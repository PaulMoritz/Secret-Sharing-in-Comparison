import os
import pandas as pd
from share_tools import read_level_stats

# get path to DATA directory
cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")


def read_data(setup):
    threshold_path = os.path.join(datapath, setup, 'level_stats.csv')
    filepath = os.path.join(datapath, setup, 'shares.csv')
    data = pd.read_csv(filepath, skiprows=0, header=None, delimiter=',', )
    levels, thresholds = read_level_stats(threshold_path)
    return data, levels, thresholds
