import os
import pandas as pd
from share_tools import read_level_stats

# path to DATA directory
cwd = os.getcwd()
main_directory = os.path.abspath(os.path.join(cwd, os.pardir))
data_path = os.path.join(main_directory, "DATA")


# read all possible data from a given setup
def read_data(setup):
    # read level stats
    threshold_path = os.path.join(data_path, setup, 'level_stats.csv')
    # read shareholders and values
    file_path = os.path.join(data_path, setup, 'shares.csv')
    data = pd.read_csv(file_path, skiprows=0, header=None, delimiter=',', )
    levels, thresholds = read_level_stats(threshold_path)
    return data, levels, thresholds
