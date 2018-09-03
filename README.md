# HSS
Hierarchical Secret Sharing

> **NOTE** This project is inspired by [Dynamic and Verifiable Hierarchical Secret Sharing](https://eprint.iacr.org/2017/724.pdf)  
> from Giulia Traverso, Denise Demirel, Johannes Buchmann and part of an internship for Giulia Traverso at TU Darmstadt.


> *To view this document properly and get links to all important references
> I strongly suggest viewing with a markdown reader or reader/browser with .md extension.*


## Requirements

To use the framework, Python 3.6.x is required. All other required libraries are listed
in [requirements.txt](./requirements.txt).  
To install requirements via pip just run  
`pip install -r requirements.txt`  
from the main (HSS) directory.

## Usage:
To create a new setup, use the methods described in [Setup](#setup).  
After a setup is created, you can create share values for a given secret message for the Shareholders with the methods from [Share](#share).  
If you want to reconstruct the message from a subset of shareholders, use [Reconstruct](#reconstruct).
  
> **INFO** All used subfunctions are explained in detail in [subfunctions.md](./subfunctions.md)

## Functionality:

---

### Setup

use [setup.py](./setup.py) to create a new setup for a scenario to test.

`setup(name, lvl_list, conjunctive):`  
sets up a new scenario
- name (string): a unique name for each setup, to use it in the other functions. Meaningful names can be helpful (e.g. "CompanyName"_levelstructure)
- lvl_list (list of integer) : a list with a list of one Integervalue for the number of persons in each level and
	one Integervalue for the threshold of the level.
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

---

### Share
Use [share.py](./share.py) to generate a function and create shares for a given secret message.

`share(message, setup, prime_number):`  
creates shares for all Shareholders in one setup
- message (Integer): the message/secret you want to share
- setup (String): The Name of a created setup to use.  
Note that the setup needs to be created first.
- prime_number (Integer): Prime number to build a finite field, default value = 31  
  
  

**Example Calls:**  

`share(42, "Big_Company", 71)`


---

### Reconstruct

Use [reconstruct.py](./reconstruct.py) to reconstruct the secret message from a subset of shareholders.

`reconstruct(setup, number_of_people, random_subset=True, subset=[], print_statements=True)`  
reconstructs the secret and the whole generated equation from [Share](#share) using a system of linear equations.
- setup (String): The name of the setup we want to reconstruct the message from
- number_of_people (positive Integer), _Default Value_ = `0`: Number of people involved in the reconstruction. 
>*Please note that a random subset of the created shareholders is used, this might not lead into a solution of the problem as Birkhoff Interpolation is not always well posed.*
- random_subset(Boolean), _Default Value_ = `True`: choose if the subset to reconstruct from is manually selected or a random subset (with _number_of_people_ many shareholders)  
- subset(Dict of _(Shareholder: Share)_ pairs) eg. `subset={"s_1_0": 13, "s_2_0": 11}`, _Default Value_ = {}: if `random_subset` is set to `False` you can provide your own subset of shareholders in the given Dictionary structure.
>*Please be careful to only use real shareholders while providing a subset as every shareholder is checked for existence and a correct share value internally.*  
> *Also, make sure that each entered shareholder is of String with format _"s_i_j"_ where _i_ determines the number of the shareholder (also: x-value; starting from 1) and _j_ is the number of the level the person is in (Levels start from 0).* 
- print_statements(Boolean),  _Default Value_ = `True`: Determines if all taken steps are printed to the console. Used internally to disable the print while calling `reconstruct` in `reset`, to check if subset is authorized.  
> _All errors or unexpected behaviours that lead to an early termination are printed to the screen anyhow!_ 

**Example Calls:**  

`reconstruct("Big_Company", number_of_people=17)`  
`reconstruct("Big_Company", random_subset=False, subset={'s_1_0': 23, 's_9_4': 10, 's_3_0': 29, 's_2_2': 40, 's_6_2': 40, 's_8_4': 37, 's_1_2': 70, 's_6_4': 32, 's_4_4': 22, 's_2_4': 61, 's_5_4': 49, 's_4_2': 5, 's_7_4': 44, 's_7_2': 12, 's_3_4': 15, 's_2_0': 67, 's_1_4': 65}
)
`

---

### Renew

Use [renew.py](./renew.py) to renew the shares of a given set of Shareholders. The Shareholders must be able to retrieve the result from the original setup.  

`renew(setup, old_shares)`  
renews the shares of the `old_shares` and saves new share values that can also reconstruct the secret message.
- setup (String): The name of the setup we want to work on
- old_shares (Dict of _(Shareholder, Share)_ pairs): the subset of old shares (Authorized on the setup) for which we want to renew the share values  
> *INFO: For convenience a shortcut was added, if you use the parameter* `old_shares={'shares': 'all'}` *, it will automatically take **all** shareholders from the setup as old shareholders and renew their values (similar to a reset but with the same general structure remaining)*
  
  

**Example Calls:**  

`renew("Big_Company", old_shares={'s_1_0': 23, 's_3_0': 29, 's_1_2': 70, 's_2_2': 40, 
        's_3_2': 64, 's_4_2': 5, 's_5_2': 5, 's_7_2': 12, 's_1_4': 65, 's_2_4': 61, 
        's_4_4': 22, 's_8_4': 37, 's_9_4': 10})
`  

`renew("Big_Company", old_shares={'shares': 'all'})
`