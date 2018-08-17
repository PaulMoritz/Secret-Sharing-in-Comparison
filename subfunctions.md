## All implemented functions:

---
### [`function_tools.py`](./function_tools.py)

`generate_function(in_degree, message, prime-number)`  
generates coefficients for the function
in Format: [[a_0, 0], [a_1, 1, [a_2, 2] ...] for f(x) = a_0 *x^0 + a_1 *x^1 + a_2 *x^2 ....
with a_0 = message

- in_degree(Integer): degree of the function (max # threshold)
- message (Integer): the message/secret you want to share
- prime_number (Integer): Prime number to build the finite field
- _returns_ a list of coefficients (like stated above) to 



`derivate_function(function_to_derivate, prime_number)`  
derivates the given function in place (modulo the prime)
for each pair of coefficients the normal derivation rules apply
(factor = factor * exponent,
exponent = exponent -1)
- function_to_derivate (list of lists): list of [factor,exponent] pairs
- prime_number (Integer): Prime number to build the finite field
- _returns_ the derivative of the given function



`calc_function(coeff_list, x, prime_number)`  
calculate the y-values for each shareholder with their given x. 
- coeff_list(list of lists): list of coefficients to reconstruct the function
- x (Integer): The x-value of the shareholder (for each shareholder s_level_x)
- prime_number (Integer): Prime number to build the finite field
- _returns_ the calculated y-value for the given parameters


`print_function(coefficients)`  
prints the list of coefficients into a readable function on screen
- coefficients(list of lists): the coefficients of the function stored as `[[factor_0, exponent_0],[factor_1, exponent_1],...]`

`is_prime(number)`  
returns True is given number is prime, False if not
- number (Integer): number to be checked if it is prime
- _returns_ `True` if number is prime, else returns `False`

---

### [`read_data_from_files.py`](./read_data_from_files.py)

`read_data(setup)`  
reads the date from a given setup and returns it  
- setup (String): the setup to read the data from
- _returns_ data (Pandas.DataFrame): contains the data of all shareholders and their according share values  
- _returns_ levels, thresholds (Lists): Two lists with the persons_per_level/threshold structure for each level (thresholds starts with a leading `0` representing `t_-1`)

---

### [`reset_tools.py`](./reset_tools.py)  

`create_new_shares(number_of_shares, number_of_levels)`  
 creates new shares for the reset randomly
 - number_of_shares(Integer): number of shares to be created  
 - number_of_levels (Integer): maximal number of levels in which the shares are to be created
 >**NOTE** currently not used due to the problems with reset


`shareholders_valid(data, shares)`  
check if all given shareholders also exist in the given data  
- data (Pandas.DataFrame): contains the data of all shareholders and their according share values 
- shares (list ofshareholder/share pairs): the Shareholders to verify
- _returns_ `True` if all shares are valid, `False` otherwise

`level_structure_to_id(structure)`  
makes a list of all shareholders by a given level structure
- structure(list of lists): The level structure; just as in [setup](./ReadMe.md#setup)
- _returns_ this list and the maximum degree of the functions used later (biggest threshold -1)

`def get_all_shares_from_setup(setup)`  
get **all** shareholder/share pairs from a given setup  
- setup (String): the setup to get all shareholders from
- _returns_ a dictionary of the pairs


`

---

### [`share_tools.py`](./share_tools.py)

`read_level_stats(filepath)`  
reads the number of persons and thresholds from a created setup and returns a list of persons in each level and the according thresholds  
- filepath(Path): relative path to the 'level_stats.csv' file of the given setup

---

### [`preconditions.py`](./preconditions.py)

`requirement_1(matrix, highest_derivative, number_of_points`  
Requirement 1 from the Appendix (Theorem 3 in [Paper](./Dynamic_Birkhoff.pdf)) which is necessary for a unique solution  
- matrix (numpy.matrix): interpolation matrix to check for a unique interpolation solution  
- highest_derivative (Integer): parameter _d_ in the formula used  
- number_of_points (Integer): parameter _r_ ( := |A|) in the formula
- _returns_ `True` if requirement_1 stands, else returns `False`



`supported_sequence(matrix)`  
checks for a supported 1-sequence of odd length;
 is used for the first requirement as stated in Theorem 3.
- matrix (numpy.matrix): the matrix to check for supported 1-sequences
- _returns_ `True` if there are supported 1-sequences, else returns `False`


`check_supported(matrix, j, i)`  
checks for a found 1-sequence if it is supported (Definition 6)  
called from `supported_sequence`  
- matrix(numpy.matrix): matrix to check for supported 1-sequence  
- j,i (Integer): indices for which the 1-sequence is to be checked if it is supported. Here, _i_ is the row and _j_ is the column index of the matrix 
- _returns_ `True` if the given 1-sequence is supported, else returns `False`


`requirement_2(d, q, max_pers_num)`  
Requirement 2 from the Appendix (Theorem 4 in [Paper](./Dynamic_Birkhoff.pdf))
- d, q, max_pers_num (Integer): the according parameters for the formula where _max_pers_num_ is equal to x_r  
>> **NOTE** that `requirement_2` is not checked in the current implementation due to the unclear assignment of _x_r_  
- _returns_ `True` if requirement_2 stands, else returns `False`


`thresholds_fulfilled(setup, person_IDs, print_statements)`
checks for each given threshold from the setup if it is satisfied by the subset of shareholders  
- setup(String): name of the setup to check the tresholds for  
- person_IDs (List of Shareholder IDs [aka Tuples _(i, j)_ ]): The Shareholders selected for reconstruction; for whose we check if they fulfill all threshold requirements  
- print_statements(Boolean): Internal variable to determine if the result of each check shall be printed to the screen  
- _returns_ `True` if all thresholds stand, else returns `False`

---