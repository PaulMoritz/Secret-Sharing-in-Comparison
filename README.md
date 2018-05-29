# HSS
Hierarchical Secret Sharing


Functionality:

## Setup

use setup.py to create a new setup for a scenario to test.

setup(name, lvl_list, conjunctive):  
sets up a new scenario
- name (string): a unique name for each setup, to use it in the other functions. Meaningful names can be helpful (e.g. "CompanyName"_levelstructure)
- lvl_list (list of integer) : a list with a list of one Integervalue for the number of persons in each level and
	one Integervalue for the threshold of the level.
	e.g: [[2,1],[5,3],[9,6]]
- conjunctive (boolean): wheter the hierarchy is conjunctive or not (--> disjunctive)

---

delete_setup(name):  
deletes a given directory
- name (string): the name of the directory to delete

---

list_setups():  
lists all setups currently created in the DATA-folder

get_info(name):  
prints all info about the setup
- name (string): info of the named setup is displayed

  
  
example calls:

setup("Big_Company", [[1,0],[3,2],[7,4],[35,10]], True)
delete_setup("Big_Company")


## Share

share(message, setup, prime_number)  
creates shares for all Shareholders in one setup
- message (Integer): the message/secret you want to share
- setup (String): The Name of a created setup to use.  
Note that the setup needs to be created first.
- prime_number (Integer): Prime number to build a finite field, default value = 31

generate_function(in_degree, message, prime-number)  
generates coefficients for the function
in Format: [[a_0, 0], [a_1, 1, [a_2, 2] ...] for f(x) = a_0 *x^0 + a_1 *x^1 + a_2 *x^2....
with a_0 = message

- in_degree(Integer): degree of the function (max # threshold)
- message (Integer): the message/secret you want to share
- prime_number (Integer): Prime number to build the finite field


derivate_function(function_to_derivate, prime_number)  
derivates the given function in place (modulo the prime)
for each pair of coefficients the normal derivation rules apply
(factor = factor * exponent,
exponent = exponent -1)
- function_to_derivate (list of lists): list of [factor,exponent] pairs
- prime_number (Integer): Prime number to build the finite field


calc_function(coeff_list, x, prime_number):  
calculate the y-values for each shareholder with their given x. 
- coeff_list(list of lists): list of coefficients to reconstruct the function
- x (Integer): The x-value of the shareholder (for each shareholder s_level_x)
- prime_number (Integer): Prime number to build the finite field
