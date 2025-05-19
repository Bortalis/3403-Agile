# Tests ReadMe

This directory contains the tests used for our project. As of 9/5/25 there is:
1. Directory named 'test_data' which contains csv files for all test data that has been used in developing this project. The data within these csv files was created using AI. 
2. Python script 'hash_existing_passwords.py' which was used to hash all the passwords in the database from the test data.
3. Python script 'import.csv' which was used to import the test data from the csv files into the database. It also set up the dimension tables in the database with dimensions set out in the script itself.
4. Python script 'test_balance_change.py' which was used to test that the functions which were added to update the Groups table balance attribute of a specified groupID when transactions were added, deleted or edited. It also tested the function which updated the GroupBalance table with the historical data of group balances.