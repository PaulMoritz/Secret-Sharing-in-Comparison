# HSS
Hierarchical Secret Sharing

> **NOTE** This project is inspired by [Dynamic and Verifiable Hierarchical Secret Sharing](https://eprint.iacr.org/2017/724.pdf)  
> from Giulia Traverso, Denise Demirel, Johannes Buchmann and part of an internship for Giulia Traverso at TU Darmstadt.

## Requirements

To use the framework, Python 3.6.x is required. All other required libraries are listed
in [requirements.txt](./requirements.txt).  
To install requirements via pip just run  
```pip install -r requirements.txt```  
from the main (HSS) directory.

## Usage:
To create a new setup, use the methods described in [Setup](#setup).
After a setup is created, you can create share values for a given secret message for the Shareholders with the methods from [Share](#share).  
If you want to reconstruct the message from a subset of shareholders, use [Reconstruct](#reconstruct).
  
## Functionality:

---

### Setup

use [setup.py](./setup.py) to create a new setup for a scenario to test.

```setup(name, lvl_list, conjunctive):```  
sets up a new scenario
- name (string): a unique name for each setup, to use it in the other functions. Meaningful names can be helpful (e.g. "CompanyName"_levelstructure)
- lvl_list (list of integer) : a list with a list of one Integervalue for the number of persons in each level and
	one Integervalue for the threshold of the level.
	e.g: [[2,1],[5,3],[9,6]]
- conjunctive (boolean): wheter the hierarchy is conjunctive or not (--> disjunctive)



```delete_setup(name):```  
deletes a given directory
- name (string): the name of the directory to delete


```list_setups():```  
lists all setups currently created in the DATA-folder

```get_info(name):```  
prints all info about the setup
- name (string): info of the named setup is displayed

  
**Example calls:**

```
setup("Big_Company", [[1,0],[3,2],[7,4],[35,10]], True)
delete_setup("Big_Company")
```
---
### Share
Use [share.py](./share.py) to generate a function and create shares for a given secret message.

```share(message, setup, prime_number):```  
creates shares for all Shareholders in one setup
- message (Integer): the message/secret you want to share
- setup (String): The Name of a created setup to use.  
Note that the setup needs to be created first.
- prime_number (Integer): Prime number to build a finite field, default value = 31  
  
  
All used subfunctions are explained in [subfunctions.md](./subfunctions.md)

**Example Call:**  

```share(42, "Big_Company", 71)```


---

### Reconstruct

Use [reconsruct.py](./reconstruct.py) to reconstruct the secret message from a subset of shareholders.

```reconstruct(setup, number_of_people)```  
reconstructs the secret and the whole generated equation from [Share](#share) using a system of linear equations.
- setup (String): The name of the setup we want to reconstruct the message from
- number_of_people (positive Integer): Number of people involved in the reconstruction.  
*Please note that a random subset of the created shareholders is used, this might not lead into a solution of the problem as Birkhoff Interpolation is not always well posed.*

**Example Call:**  

```reconstruct("Big_Company", 17)```
