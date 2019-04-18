# HSS
Hierarchical Secret Sharing by Paul Moritz Ranly 

> **NOTE** This project is inspired by [Dynamic and Verifiable Hierarchical Secret Sharing](./Dynamic_Birkhoff.pdf)  
> from Giulia Traverso, Denise Demirel, Johannes Buchmann and part of an internship for Giulia Traverso at TU Darmstadt.


> *To view this document properly and get links to the references
> I strongly suggest viewing with a markdown reader or reader/browser with .md extension.*


## Requirements

To use the framework, Python 3.6.x is recommended as I didn't test on other distributions. All other required libraries are listed
in [requirements.txt](./requirements.txt).  
To install requirements via pip just run  
`pip install -r requirements.txt`  
from the main (HSS) directory.

## Usage:
To create a new setup, use the methods described in [Setup](#setup).  
After a setup is created, you can create share values for a given secret message for the Shareholders with the methods from [Share](#share).  
If you want to reconstruct the message from a subset of shareholders, use [Reconstruct](#reconstruct).  
Last, to renew the share values for an authorised set (or all) of shareholders, use [Renew](#renew).
  
> **INFO** All used subfunctions are explained in detail in [subfunctions.md](./subfunctions.md)

> **Update** To make accessing the main functionality easier, calls from the command-line were added. They are specified in the _Update_ section of each paragraph.
 As this causes much input error-handling, not every input error will be caught. Please make sure you use the format provided, some example calls are included in [main.py](./code_tested/code/hss/main.py).


## Functionality:

---

### Setup

use [setup.py](./code_tested/code/hss/setup.py) to create a new setup for a scenario to test.

`setup(name, lvl_list, conjunctive):`  
sets up a new scenario
- name (string): a unique name for each setup, to use it in the other functions. Meaningful names can be helpful (e.g. "CompanyName"_levelstructure)
- lvl_list (list of integer) : a list with a list of one Integer for the number of persons in each level and
	one Integer for the threshold of the level representing the _setup structure_.  
e.g: [[2,1],[5,3],[9,6]]
- conjunctive (boolean): wheter the hierarchy is conjunctive or not (--> disjunctive)



`delete_setup(name):`  
deletes a given directory
- name (string): the name of the directory to delete


`list_setups():`  
lists all setups currently created in the DATA-folder

`get_info(name):`  
prints all info about the setup
- name (string): info of the named setup is displayed

  
**Example Calls:**  

`setup("Big_Company", [[1,0],[3,2],[7,4],[9,10]], True)`  
`delete_setup("Big_Company")`  



> **Update**: Setup can also be called _directly from the console_ by calling
>- For a new setup:  
> `python main.py setup *setup_name* *setup_structure*`  
>- To delete a setup:  
> `python main.py setup *setup_name* delete`  
>- To get setup information:  
> `python main.py setup *setup_name* get`  
>- To list all created setups:  
> `python main.py setup (*setup_name*) list`  
> where the setup name is optional (not necessary for execution).
>
> from the _code_tested/code/hss_ directory.
>
> You can find example calls in [main.py](./code_tested/code/hss/main.py)
---

### Share
Use [share.py](./code_tested/code/hss/share.py) to generate a function and create shares for a given secret message.

`share(setup, message, prime_number):`  
creates shares for all Shareholders in one setup
- setup (String): The Name of a created setup to use.  
- message (Integer): the message/secret you want to share
Note that the setup needs to be created first.
- prime_number (Integer): Prime number to build a finite field, default value = 997  
  
  

**Example Calls:**  

`share("Big_Company", 42, 71)`  



> **Update**: Share can also be called _directly from the console_ by calling
>- `python main.py share *setup_name* *secret_message*`  
>
> from the _code_tested/code/hss_ directory.
>
> You can find example calls in [main.py](./code_tested/code/hss/main.py)



---

### Reconstruct

Use [reconstruct.py](./code_tested/code/hss/reconstruct.py) to reconstruct the secret message from a subset of shareholders.

`reconstruct(setup, number_of_people, random_subset=True, subset=[], print_statements=True)`  
reconstructs the secret and the whole generated equation from [Share](#share) using a system of linear equations.
- setup (String): The name of the setup we want to reconstruct the message from
- number_of_people (positive Integer), _Default Value_ = `0`: Number of people involved in the reconstruction. 
>*Please note that a random subset of the created shareholders is used, this might not lead into a solution of the problem as Birkhoff Interpolation is not always well posed.*
- random_subset(Boolean), _Default Value_ = `True`: choose if the subset to reconstruct from is manually selected or a random subset (with _number_of_people_ many shareholders)  
- subset(Dict of _(Shareholder: Share)_ pairs) eg. `subset={"s_1_0": 13, "s_2_0": 11}`, _Default Value_ = {}: if `random_subset` is set to `False` you can provide your own subset of shareholders in the given Dictionary structure.
>*Please be careful to only use real shareholders while providing a subset as every shareholder is checked for existence and a correct share value internally.*  
> *Also, make sure that each entered shareholder is of String with format _"s_i_j"_ where _i_ determines the number of the shareholder (also: x-value; starting from 1) and _j_ is the number of the level the person is in (Levels start from 0).* 
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console. Used internally to disable the print while calling `reconstruct` in `renew`, to check if subset is authorized.  
> _All errors or unexpected behaviours that lead to an early termination are printed to the screen anyhow!_ 

**Example Calls:**  

`reconstruct("Big_Company", number_of_people=17)`  
`reconstruct("Big_Company", random_subset=False, subset={'s_1_0': 23, 's_9_4': 10, 's_3_0': 29, 's_2_2': 40, 's_6_2': 40, 's_8_4': 37, 's_1_2': 70, 's_6_4': 32, 's_4_4': 22, 's_2_4': 61, 's_5_4': 49, 's_4_2': 5, 's_7_4': 44, 's_7_2': 12, 's_3_4': 15, 's_2_0': 67, 's_1_4': 65}
)  
`


> **Update**: Reconstruct can also be called _directly from the console_ by calling
>- Reconstruct with random people:  
> `python main.py reconstruct *setup_name* *number_of_people*`  
>- Reconstruct with a specific subset:  
> `python main.py reconstruct *setup_name* False *subset*`  
> _When using this call, make sure that you don't leave any spaces in the subset itself. This would prevent parsing from being successful._
>
> from the _code_tested/code/hss_ directory.
>
> You can find example calls in [main.py](./code_tested/code/hss/main.py)
---

### Renew

Use [renew.py](./code_tested/code/hss/renew.py) to renew the shares of a given set of Shareholders. The Shareholders must be able to retrieve the result from the original setup.  

`renew(setup, old_shares, reset_version_number=None, print_statements=True)`  
renews the shares of the `old_shares` and saves new share values that can also reconstruct the secret message.
- setup (String): The name of the setup we want to work on
- old_shares (Dict of _(Shareholder, Share)_ pairs): the subset of old shares (Authorized on the setup) for which we want to renew the share values  
> *INFO: For convenience a shortcut was added, if you use the parameter* `old_shares={'shares': 'all'}` *, it will automatically take **all** shareholders from the setup as old shareholders and renew their values (similar to a reset but with the same general structure remaining)*
- reset_version_number=None (Integer): if provided, this is the number appended to the saved file to not override the original shares
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console.
  
  

**Example Calls:**  

`renew("Big_Company", old_shares={'s_1_0': 23, 's_3_0': 29, 's_1_2': 70, 's_2_2': 40, 
        's_3_2': 64, 's_4_2': 5, 's_5_2': 5, 's_7_2': 12, 's_1_4': 65, 's_2_4': 61, 
        's_4_4': 22, 's_8_4': 37, 's_9_4': 10})
`  

`renew("Big_Company", old_shares={'shares': 'all'})  
`



> **Update**: Renew can also be called _directly from the console_ by calling 
>- `python main.py renew *setup_name* *old_shares*`  
> _When using this call, make sure that you don't leave any spaces in the old_shares itself. This would prevent parsing from being successful._

>- To use _all_ old shares, it is important that `{'shares':'all'}` is written exactly like this (also the apostrophes) in the console so that it can be parsed correctly.
>
> from the _code_tested/code/hss_ directory.
>
> You can find example calls in [main.py](./code_tested/code/hss/main.py)
---

### Reset

Use [reset.py](./code_tested/code/hss/reset.py) to reset the structure, i.e. the thresholds and shareholders per level. The Shareholders must be able to retrieve the result from the original setup.  

`reset(setup, old_shares, new_shares=[], create_new_shares_randomly=False, number_of_random_shares=0, reset_version_number=None, print_statements=True)`  
resets the structure of the `old_shares` and saves new shares that can also reconstruct the secret message.
- setup (String): The name of the setup we want to work on
- old_shares (Dict of _(Shareholder, Share)_ pairs): the subset of old shares (Authorized on the setup) which want to reset the given structure
- new_shares(List of  _(people, threshold)_ pairs): list of structure of the new setup (see lvl_list in [Setup](#setup))
- create_new_shares_randomly (Boolean): wheter the new setup is to be chosen randomly
- number_of_random_shares (Integer): the number of people in the new setup
- reset_version_number=None (Integer): if provided, this is the number appended to the saved file to not override the original shares
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console.
  
  

**Example Calls:**  

`reset("Big_Company", old_shares={'s_1_0': 23, 's_3_0': 29, 's_1_2': 70, 's_2_2': 40, 
        's_3_2': 64, 's_4_2': 5, 's_5_2': 5, 's_7_2': 12, 's_1_4': 65, 's_2_4': 61, 
        's_4_4': 22, 's_8_4': 37, 's_9_4': 10}, new_shares=[[1,0],[3,2],[7,4],[9,10]])
`

---

### Add

Use [add.py](./code_tested/code/hss/add.py) to add a new shareholder. The Shareholders participating must be able to retrieve the result from the original setup.  

`add(setup, old_shares, new_shareholder_id=(0, 0), choose_id_randomly=False, reset_version_number=None, print_statements=True, function_f=[])`  
renews the shares of the `old_shares` and saves new share values that can also reconstruct the secret message.
- setup (String): The name of the setup we want to work on
- old_shares (Dict of _(Shareholder, Share)_ pairs): the subset of old shares (Authorized on the setup) participating in the process  
- new_shareholder_id (pair _(i,j)_ of integers): The ID for the new shareholder with _i_,_j_ as the person number and level respectively
- choose_id_randomly (Boolean, _Default_ `False`): _not yet implemented, chooses a random ID for the new shareholder_
- reset_version_number=None (Integer): if provided, this is the number appended to the saved file to not override the original shares
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console.
- function_f (list of lists, _default_ `empty`): if provided, a check is executed wheter the new share is on the given the polynomial
  
  

**Example Calls:**  

`add("Big_Company", old_shares={'s_1_0': 23, 's_3_0': 29, 's_1_2': 70, 's_2_2': 40, 
        's_3_2': 64, 's_4_2': 5, 's_5_2': 5, 's_7_2': 12, 's_1_4': 65, 's_2_4': 61, 
        's_4_4': 22, 's_8_4': 37, 's_9_4': 10}, new_shareholder_id=(10,4))
`

---

### Linear

Use [linear.py](./code_tested/code/hss/linear.py)  perform linear operations on messages.

`linear(list_of_tuples, field_size, print_result=False)`
calculates the linear combination of the provided tuples, eg for (3, 4) and (5,6) it produces 3\*4 + 5\*6 = 42
- list_of_tuples (list of Integerpairs): each tuple represents _(lambda_l, sigma_i,j (m_l))_, the algorithm iteartes over all tuples
- field_size (Integer): The size of the finite field we're working on
- print_result (Boolean, _Default_ `False`): wheter the result shall be printed after execution (needed because `linear` is used internally)

**Example Calls:**

`linear([[3,4],[5,6]], field_size=997)`

---

### RandShares

Use [multiply_tools.py](./code_tested/code/hss/multiply_tools.py) to create random shares for a chosen secret value.
>**NOTE** that this algorithm only computes the shares for one of alpha/beta and not both. For this, the algorithms have to be called multiple times

`rand_shares_calculation(field_size, shareholders, thresholds, conjunctive)`
calculates the shares for one shareholder and returns a list of those shares
- field_size (Integer): the finite field we work in
- shareholders (list of IDs): list of IDs of the participating shareholders
- thresholds (list of Integer): the threshold for each level in a list
- conjunctive (Boolean): whether or not we have a conjunctive setup

`rand_shares_summation(all_new_shares, field_size, r)`
takes all shares from all shareholders calculated in `rand_shares_calculation` and sums them up to get exactly one share per shareholder
- all_new_shares (list of lists of Integers): all shares calculated (from and for each shareholder), to be summed up. Each list corresponds to one call of `rand_shares_calculation`, where the shares for one shareholder are calculated
- field_size (Integer): The size of the finite field we're working on
- r (Integer): number of shareholders participating

---

### PreMult

Use [multiply_tools.py](./code_tested/code/hss/multiply_tools.py) to create a share of gamma for each shareholder (and thus the triple alpha, beta, gamma needed for multiply), the algorithm is using the calculation of shares for alpha and beta from randShares.

`pre_mult(setup)`
calculates a triple  of shares for_(alpha, beta, gamma)_ from known alpha, beta values for each shareholder, needed in multilpy
- setup (String): The name of the setup we want to work on, to know about the shareholders

**Example Calls:**

`pre_mult("Big_Company")`

---

### Multiply

Use [multiply.py](./code_tested/code/hss/multiply.py) to multiply shares of two messages m_1, m_2 and return the share of m, where m=m_1\*m_2.

`multiply(setup, messages, print_statements=True)`
multiplies two  shares ofmessages and returns the share of the product of the two messages without reconstructing them. multiply makes use of preMult, which uses randShares.
- setup (String): The name of the setup we want to work on (needed for the structure and metadata of shareholders)
- messages (dict of _(shareholder,: messages)_ pairs, where messages are the share of m_1 and m_2 of this shareholder respectively (in a list)): a dict of the shares of the two messages for each shareholder
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console.

**Example Calls:**

`multiply("1,2,3", {(1, 0): (7, 13), (2, 1): (14, 22), (3, 2): (6, 8)})`