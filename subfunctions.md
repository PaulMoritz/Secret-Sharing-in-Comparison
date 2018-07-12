## All implemented functions:

---
### [```function_tools.py```](./function_tools.py):

```generate_function(in_degree, message, prime-number)```  
generates coefficients for the function
in Format: [[a_0, 0], [a_1, 1, [a_2, 2] ...] for f(x) = a_0 *x^0 + a_1 *x^1 + a_2 *x^2....
with a_0 = message

- in_degree(Integer): degree of the function (max # threshold)
- message (Integer): the message/secret you want to share
- prime_number (Integer): Prime number to build the finite field


```derivate_function(function_to_derivate, prime_number)```  
derivates the given function in place (modulo the prime)
for each pair of coefficients the normal derivation rules apply
(factor = factor * exponent,
exponent = exponent -1)
- function_to_derivate (list of lists): list of [factor,exponent] pairs
- prime_number (Integer): Prime number to build the finite field


```calc_function(coeff_list, x, prime_number)```  
calculate the y-values for each shareholder with their given x. 
- coeff_list(list of lists): list of coefficients to reconstruct the function
- x (Integer): The x-value of the shareholder (for each shareholder s_level_x)
- prime_number (Integer): Prime number to build the finite field

```print_function(coefficients)```  
prints the list of coefficients into a readable function on screen
- coefficients(list of lists): the coefficients of the function stored as ```[[factor_0, exponent_0],[factor_1, exponent_1],...]```

```is_prime(number)```  
returns True is given number is prime, False if not
- number (Integer): number to be checked if it is prime


---
### [```share_tools.py```](./share_tools.py):

```read_level_stats(filepath)```  
reads the number of persons and thresholds from a created setup and returns a list of persons in each level and the according thresholds  
- filepath(Path): relative path to the 'level_stats.csv' file of the given setup

---