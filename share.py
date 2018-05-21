import os
import numpy as np
import pandas as pd
import csv
from math import pow


cwd = os.getcwd()
datapath = os.path.join(cwd, "DATA")


def share(message, setup, prime = 31):
    filepath = os.path.join(datapath, setup, 'info.csv')
    shareholder_list=[]
    data =pd.read_csv(filepath, delimiter=',',)
    #create list of number of people in each level
    num = list(data.iloc[4:,0])
    for level, number in enumerate(num):
        for i in range(1,int(number)+1):
            shareholder_list.append("s_{}_{}".format(i, level))
    share_main(message, setup, shareholder_list, prime)






def share_main(message, setup, shareholder_list, prime):
    number_of_shareholders = shareholder_list.__len__()
    coefficients = generate_function(number_of_shareholders, message, prime)
    share_list= {}
    print(coefficients)
    #change range for other x values
    x_values = list(range(1, number_of_shareholders + 1))
    for i, shareholder in enumerate(shareholder_list):
        x = x_values[i]
        value = calc_function(coefficients, x, prime, message, number_of_shareholders, shareholder_list)
        if value == -1:
            return
        share_list[shareholder]=value
    print(share_list)
    with open(os.path.join(datapath, setup, "shares.csv"), "w", newline ='', encoding="utf8") as shares:
        writer = csv.writer(shares)
        writer.writerows(share_list.items())
        print("New Shares in folder 'DATA/"+ setup + "/shares.csv' calculated.")





#generates coefficients for the function
# Format: [a_0, a_1, a_2,...] for f(x) = a_0 + a_1 *x + a_2 *x^2....
def generate_function(length, message, prime):
    coefficients = []
    coefficients.append(message)
    for i in range(1, length):
        a_i = np.random.randint(1, prime)
        coefficients.append(a_i)
    return coefficients




def calc_function(coeff_list, x, prime, message, length, shareholder_list):
    result = 0
    for i, coefficient in enumerate(coeff_list):
        result = (result + (coefficient * pow(x, i)) % prime) % prime
    if  (result % prime) == 0:
        print("""Error in calculation: Share with Value 0 detected!
Please try again,
consider changing your prime numbers.""")
        return -1
    else:
        return int((result % prime))




#share_main(3,["s11", "s21", "s22"])
#share(3,"Big_Company")
#get_x_values(["s11", "s21", "s22"])