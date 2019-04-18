# SSS
Shamir Secret Sharing by Paul Moritz Ranly 

> *To view this document properly and get links to the references
> I strongly suggest viewing with a markdown reader or reader/browser with .md extension.*


## Requirements

To use the framework, Python 3.6.x is recommended as I didn't test on other distributions. All other required libraries are listed
in [requirements.txt](./requirements.txt).  
To install requirements via pip just run  
`pip install -r requirements.txt`  
from the main directory.

## Usage:
You can create share values for a given secret message for the Shareholders with the methods from [Share](#share).  
If you want to reconstruct the message from a subset of shareholders, use [Reconstruct](#reconstruct).  
Last, to renew the share values for an authorised set (or all) of shareholders, use [Renew](#renew).


## Functionality:



### Share
Use [shamir_share.py](./code_tested/code/sss/shamir_share.py) to generate a function and create shares for a given secret message.

`make_random_shares(minimum_number_of_shares, number_of_people, message, field_size):`  
creates shares for all Shareholders in one setup
- minimum_number_of_shares (Integer): value _t_, the threshold of the setup
- number_of_people (Integer): value _n_, the number of participating people 
- message (Integer): the message/secret you want to share
- prime_number (Integer): Prime number to build a finite field  
  
  

**Example Calls:**  

`shamir_share(minimum_number_of_shares=3, number_of_people=7, message=42, field_size=71)`  

---

### Reconstruct

Use [lagrange_interpolation.py](./code_tested/code/sss/lagrange_interpolation.py) to reconstruct the secret message from a subset of shareholders.

`reconstruct(setup, shares, field_size, print_statements=True):`  
reconstructs the secret or the whole generated equation from [Share](#share) using a system of linear equations.
- setup (Pair _(t,n)_): The setup, where t= threshold and n= number of people
- shares: (dict of _i:share_): the known shares in dictionary format
- field_size (Integer): The size of the finite field
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console. Used internally to disable the print while calling `reconstruct` in `renew`, to check if subset is authorized.  
> _All errors or unexpected behaviours that lead to an early termination are printed to the screen anyhow!_ 

**Example Calls:**  

`reconstruct((3,8), shares={1: 23, 2: 10, 3: 29, 4: 40, 5: 40}, field_size=71)  
`

---

### Renew

Use [shamir_renew.py](./code_tested/code/sss/shamir_renew.py) to renew the shares of a given set of Shareholders. The Shareholders must be able to retrieve the result from the original setup.  

`shamir_renew(setup, reset_version_number=None, print_statements=True):
`  
renews the shares of the `old_shares` and saves new share values that can also reconstruct the secret message.
- setup (Pair _(t,n)_): The setup, where t= threshold and n= number of people
- reset_version_number=None (Integer): if provided, this is the number appended to the saved file to not override the original shares
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console. Used internally to disable the print while calling `reconstruct` in `renew`, to check if subset is authorized.  
  
  

**Example Calls:**  

`renew("Big_Company", reset_version_number=1)
`  

`renew("Big_Company")  
`

---

### Reset

Use [shamir_reset.py](./code_tested/code/sss/shamir_reset.py) to reset the structure, i.e. the thresholds and shareholders per level. The Shareholders must be able to retrieve the result from the original setup.  

`shamir_reset(setup, new_structure, reset_version_number=None, print_statements=True)`  
resets the structure of the `old_shares` and saves new shares that can also reconstruct the secret message.
- setup (Pair _(t,n)_): The setup, where t= threshold and n= number of people
- new_structure (Pair _(t,n)_): The new structure to build with the reset, _t_ is the threshold and _n_ the number of participating people
- reset_version_number=None (Integer): if provided, this is the number appended to the saved file to not override the original shares
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console. Used internally to disable the print while calling `reconstruct` in `reset`, to check if subset is authorized.  

  
  

**Example Calls:**  

`reset((3,7),(3,8))` [for simply adding a shareholder, see also [add](#add)]

`reset((4,9),(3,6))`


---

### Add

Use [add.py](./code_tested/code/sss/shamir_add.py) to add a new shareholder. The Shareholders participating must be able to retrieve the result from the original setup.  

`shamir_add(setup, old_shares, new_shareholder_id, print_statements=True)`  
adds a new shareholder to the given structure without changing the threshold, efficiently making it a _(k, n+1)_ setup. The _old_shares_ participating in the process need to be authorized to reconstruct the secret (which they don't do here)
- setup (Pair _(t,n)_): The setup, where t= threshold and n= number of people
- old_shares (Dict of _(Shareholder, Share)_ pairs): the subset of old shares (Authorized on the setup) participating in the process  
- new_shareholder_id (Integer): The ID for the new shareholder with _i_as the person number
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console. Used internally to disable the print while calling `reconstruct` in `add`, to check if subset is authorized.  
  
  

**Example Calls:**  

`add("(3,5), old_shares={1: 23, 2: 29, 3: 70}, new_shareholder_id=4)
`
___


### Linear
>This is the same as in [sss/shamir_](./Description_Hierarchical.md)!
Use [linear.py](./code_tested/code/sss/shamir_/linear.py)  perform linear operations on messages.

`linear(list_of_tuples, field_size, print_result=False)`
calculates the linear combination of the provided tuples, eg for (3, 4) and (5,6) it produces 3\*4 + 5\*6 = 42
- list_of_tuples (list of Integerpairs): each tuple represents _(lambda_l, sigma_i,j (m_l))_, the algorithm iteartes over all tuples
- field_size (Integer): The size of the finite field we're working on
- print_result (Boolean, _Default_ `False`): wheter the result shall be printed after execution (needed because `linear` is used internally)

**Example Calls:**

`linear([[3,4],[5,6]], field_size=997)`

---

### RandShares

Use [shamir_multiply_tools.py](./code_tested/code/sss/shamir_multiply_tools.py) to create random shares for a chosen secret value.
>**NOTE** that this algorithm only computes the shares for one of alpha/beta/r/r\* and not all. For this, the algorithms have to be called multiple times

`rand_shares_calculation(field_size, shareholders, polynomial)`
calculates the shares for one shareholder and returns a list of those shares
- field_size (Integer): the finite field we work in
- shareholders (list of IDs): list of IDs of the participating shareholders
- polynomial (list of lists): the polynomial to share the values on (randomly chosen before)

`rand_shares_summation(computed_shares, field_size, r)`
takes all shares from all shareholders calculated in `rand_shares_calculation` and sums them up to get exactly one share per shareholder
- computed_shares (list of lists of Integers): all shares calculated (from and for each shareholder), to be summed up. Each list corresponds to one call of `rand_shares_calculation`, where the shares for one shareholder are calculated
- field_size (Integer): The size of the finite field we're working on
- r (Integer): number of shareholders participating

---

### PreMult

Use [shamir_multiply_tools.py](./code_tested/code/sss/shamir_multiply_tools.py) to create a share of gamma for each shareholder (and thus the triple alpha, beta, gamma needed for multiply), the algorithm is using the calculation of shares for alpha and beta from randShares.

`pre_mult(setup, print_statements=True)`
calculates a triple  of shares for_(alpha, beta, gamma)_ from known alpha, beta values for each shareholder, needed in multilpy
- setup (String): The name of the setup we want to work on, to know about the shareholders
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console.

**Example Calls:**

`pre_mult("Big_Company")`

---

### Multiply

Use [shamir_multiply.py](./code_tested/code/sss/shamir_multiply.py) to multiply shares of two messages m_1, m_2 and return the share of m, where m=m_1\*m_2.

`multiply(setup, messages, print_statements=True)`
multiplies two  shares ofmessages and returns the share of the product of the two messages without reconstructing them. multiply makes use of preMult, which uses randShares.
- setup (String): The name of the setup we want to work on (needed for the structure and metadata of shareholders)
- messages (dict of _(shareholder,: messages)_ pairs, where messages are the share of m_1 and m_2 of this shareholder respectively (in a list)): a dict of the shares of the two messages for each shareholder
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console.