# SSS
Shamir Secret Sharing by Paul Moritz Ranly 

> *To view this document properly and get links to the references
> I strongly suggest viewing with a markdown reader or reader/browser with .md extension.*


## Requirements

To use the framework, Python 3.6.x is recommended as I didn't test on other distributions. All other required libraries are listed
in [requirements.txt](./requirements.txt).  
To install requirements via pip just run  
`pip install -r requirements.txt`  
from the main (HSS) directory.

## Usage:
You can create share values for a given secret message for the Shareholders with the methods from [Share](#share).  
If you want to reconstruct the message from a subset of shareholders, use [Reconstruct](#reconstruct).  
Last, to renew the share values for an authorised set (or all) of shareholders, use [Renew](#renew).


## Functionality:

---


### Share
Use [shamir_share.py](./code_tested/code/sss/shamir_share.py) to generate a function and create shares for a given secret message.

`share(setup, message, prime_number):`  
creates shares for all Shareholders in one setup
- minimum_number_of_shares (Integer): value _t_, the threshold of the setup
- number_of_people (Integer): value _n_, the number of participating people 
- message (Integer): the message/secret you want to share
- prime_number (Integer): Prime number to build a finite field  
  
  

**Example Calls:**  

`shamir_share(3, 7, 42, 71)`  

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
