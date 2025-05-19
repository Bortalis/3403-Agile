""" This script is for testing the functionality of adding, removing and editing transactions """
from app.models import db, Transaction, Group, GroupBalance
from app.api import update_add_transaction, update_delete_transaction
from app import create_app
import csv
import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


"""
# test adding transaction 
# updating group balance and balance history tables 
# adding transaction with no note and with note 
"""

# adding transaction test

def add_trn_test():

    update_add_transaction(1, "1", "100", "True", "1", "2024-11-05 14:30:10", "")

    add_test = Transaction.query.get(1)

    return print(add_test)

def add_trn_bal():

    test_grp_bal = Group.query.get(1)

    return print(test_grp_bal)

def add_trn_hist():

    test_add_hist = GroupBalance.query.get(1)

    return print(test_add_hist)

def add_trn_nonote():

    add_trn_n1 = GroupBalance.query.get(1)

    return print(add_trn_n1)

def add_trn_newnote():
    update_add_transaction(1, "1", "100", "True", "1", "2024-12-05 14:30:10", "Test add note")

    add_newnote_test = Transaction.query.get(2)

    return print(add_newnote_test)

def add_trn_samenote():
    update_add_transaction(1, "1", "100", "True", "1", "2024-12-06 14:30:10", "Test add note")

    add_samenote_test = Transaction.query.get(3)

    return print(add_samenote_test)

"""
# test deleting transaction 
# updating group balance and history tables 
# deleting transaction with and without note
"""

def del_trn_test():
    update_delete_transaction(1)
    update_delete_transaction(2)
    update_delete_transaction(3)
    return True

#def del_trn_bal():
  #  return True

#def del_trn_hist():
   # return True

#def del_trn_nonote():
   # return True

#def del_trn_newnote():
   # return True

#def del_trn_samenote():
   # return True

"""
# edit transactions:
# changing groupid
# changing amount 
# changing cat id 
# changing date
# changing all
# changing none
# updating group balance and group history after
"""

def edit_trn_test():
    return True

def edit_trn_bal():
    return True

def edit_trn_hist():
    return True

"""
# editing note
# adding note when no note
# removing note when there was a note
# changing note
# no change to note
# no change to note when there was a note
"""

#def edit_trn_nonote():
   # return True

#def edit_trn_newnote():
   # return True

#def edit_trn_nochange(): # both when note is blank and note has contents
  #  return True

#def edit_trn_removenote():
   # return True

def main():
    app = create_app()

    with app.app_context():


        # Test the balance change functions
        add_trn_test()
        add_trn_bal()
        add_trn_hist()
        add_trn_nonote()
        add_trn_newnote()
        add_trn_samenote()

if __name__ == '__main__':
    main()