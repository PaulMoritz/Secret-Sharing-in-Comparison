# Secret Sharing in Comparison
This repository provides code for Shamir secret sharing and hierarchical secret sharing as proposed by Tassa.


> **NOTE** The provided code was shortened for the evaluation of the runtimes, as many assertions are simply provided to get a more robust system.


> *To get links to the references
> I strongly suggest viewing with a markdown reader or reader/browser with .md extension.*


## Structure

The code is split up between Shamir secret sharing and hierarchical secret sharing.  
The instructions for both can be found in  [HSS](./Description_Hierarchical.md) for **h**ierarchical **s**ecret **s**haring and [SSS](./Description_Shamir.md) for **S**hamir **s**ecret **s**haring.  
A general test of all functionality for some provided test setups can be done by running [test_setups.py](./code_tested/code/hss/test_setups.py) for hierarchical and [shamir_test_setups.py](./code_tested/code/sss/shamir_test_setups.py) for Shamir secret sharing directly from the console.  
The example setups tested upon can be found in [tassa_setups.yaml](./code_tested/code/hss/tassa_setups.yaml) for hierarchical and [shamir_setups.yaml](./code_tested/code/sss/shamir_setups.yaml) respectively.
Results of the example setups in regards to saved information such as the shares can be found in the _code_tested/DATA_ directory.