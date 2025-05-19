"""This script is used to test the balance change functions in the app. Only run this script if you are sure that the database is empty.
   It will create test data in the database and then run the tests."""

from app import create_app
import csv
import os
from datetime import datetime
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from app.models import db, User, Transaction, Group, GroupMembership, Note, Category, GroupType, GroupRole, GroupBalance, add_group_balance, delete_group_balance, update_group_balance

def test_balance_change():
   
    test_groups = [
        {'grid': 1, 'groupname': 'Test Group 1', 'balance': 50.00, 'group_type': 1},
        {'grid': 2, 'groupname': 'Test Group 2', 'balance': 300.00, 'group_type': 1},
        {'grid': 3, 'groupname': 'Test Group 3', 'balance': 25.00, 'group_type': 1}
    ]

    for rows in test_groups:
        test_group = Group(
            grid=rows['grid'],
            grname=rows['groupname'],
            balance=rows['balance'],
            grtype=rows['group_type']
        )
        db.session.add(test_group)
        db.session.commit()

    test_balances = [
        {'grid': 2, 'balanceid': 2, 'amount': 200.00, 'date': '2025-05-08','income': True},
        {'grid': 3, 'balanceid': 3, 'amount': 50.00, 'date': '2025-05-08','income': True}
    ]
   
    for rows in test_balances:
        test_balance = GroupBalance(
            grid=rows['grid'],
            balanceid=rows['balanceid'],
            date=datetime.strptime(rows['date'],  '%Y-%m-%d').date(),
            up_balance=rows['amount']
        )
        db.session.add(test_balance)
        db.session.commit()

def test_balance_add():

    add_group_balance(1, 1, 50.00, datetime.strptime('2025-05-08', '%Y-%m-%d').date(), True)

def test_balance_delete():
    
    delete_group_balance(2, 100.00, 2, True)

def test_balance_update():

    update_group_balance(3, 25.00, 75.00, datetime.strptime('2025-05-08', '%Y-%m-%d').date(), False, 3)


def main():
    app = create_app()

    with app.app_context():

        # Test the balance change functions
        test_balance_change() 
        test_balance_add()
        test_balance_delete()
        test_balance_update()

if __name__ == '__main__':
    main()

