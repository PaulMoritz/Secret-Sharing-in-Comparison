# HSS
Hierarchical Secret Sharing

Functionality:

Setup

use setup.py to create a new setup for a scenario to test.

setup(name, lvl_list, conjunctive)
sets up a new scenario
params:
- name (string): a unique name for each setup, to use it in the other functions. Meaningful names can be helpful (e.g. "CompanyName"_levelstructure)
- lvl_list (list of integer) : a list with a list of one Integervalue for the number of persons in each level and
	one Integervalue for the threshold of the level.
	e.g: [[2,1],[5,3],[9,6]]
- conjunctive (boolean): wheter the hierarchy is conjunctive or not (--> disjunctive)



delete_setup(name)
deletes a given directory
params:
- name (string): the name of the directory to delete


list_setups()
lists all setups currently created in the DATA-folder


example calls:
setup("Big_Company", [[1,0],[3,2],[7,4],[35,10]], True)
delete_setup("Big_Company")