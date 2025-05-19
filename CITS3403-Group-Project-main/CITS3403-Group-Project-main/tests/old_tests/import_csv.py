from app import create_app
import csv
import os
from datetime import datetime
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from app.models import db, User, Transaction, Group, GroupMembership, Note, Category, GroupType, GroupRole

def import_users(csv_file):
    
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            user = User(
                usid=row['user_id'],
                email=row['email'],
                fname=row['first_name'],
                lname=row['surname'],
                password=row['password']
            )
            db.session.add(user)
    db.session.commit()

def import_transactions(csv_file):
    
    with open(csv_file, 'r') as file:
        
        reader = csv.DictReader(file)
        
        for row in reader:

            transaction = Transaction(
                usid=row['user_id'],
                trid=row['transaction_id'],
                grid=row['group_id'],
                amount=row['amount'],
                catId=row['category'],
                date=datetime.strptime(row['date'],  '%Y-%m-%d %H:%M:%S').date(),
            )
            
            transaction.income = import_income(row['income'])

            if row['notes'] != "":
                add_noteid = import_notes(row['notes'])
                transaction.noteid = add_noteid
            else:
                transaction.noteid = 1

            db.session.add(transaction)
    db.session.commit()

def import_income(incstring):

    if incstring == 'True':
        return True
    else:
        return False
    
def import_notes(trnote):

    note = Note(
        content=trnote
    )
    db.session.add(note)
    db.session.commit()

    return note.noteid

def import_groups(csv_file):
    
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            group = Group(
                grid=row['group_id'],
                grname=row['groupname'],
                grtype=row['group_type'],
                balance=row['balance']
            )
            db.session.add(group)
        db.session.commit()

def import_group_memberships(csv_file):
    
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            group_membership = GroupMembership(
                usid=row['user_id'],
                grid=row['group_id'],
                roleid=row['role_id']
            )
            db.session.add(group_membership)
        db.session.commit()

def add_category():

    basecategories = [
        Category(name='Food'),
        Category(name='Transport'),
        Category(name='Entertainment'),
        Category(name='Health'),
        Category(name='Utilities'),
        Category(name='Rent'),
        Category(name='Groceries'),
        Category(name='Dining Out'),
        Category(name='Shopping'),
        Category(name='Travel'),
        Category(name='Other'),
        Category(name='Income')
    ]

    db.session.add_all(basecategories)
    db.session.commit()

def add_grtype():
    
    grouptypes = [
        GroupType(description='Family'),
        GroupType(description='Roommates'),
        GroupType(description='Work Group'),
        GroupType(description='Travel Group'),
        GroupType(description='Sports Club, Team, or Group'),
        GroupType(description='Charity Group'),
        GroupType(description='Social Group'),
        GroupType(description='Personal')
    ]

    db.session.add_all(grouptypes)
    db.session.commit()

def add_grrole():
    
    grouproles = [
        GroupRole(title='Owner'),
        GroupRole(title='Member'),
        GroupRole(title='Guest'),
        GroupRole(title='Personal')
    ]

    db.session.add_all(grouproles)
    db.session.commit()

def no_notes():

    note = Note(
        noteid=1,
        content=""
    )
    db.session.add(note)
    db.session.commit()

def main():
    app = create_app()

    with app.app_context():

        import_users('../test_data/mock_users.csv')
        no_notes()
        import_transactions('../test_data/mock_transaction_2.csv')
        import_groups('../test_data/mock_groups_2.csv')
        import_group_memberships('../test_data/mock_groupmembership.csv')
        add_category()
        add_grtype()
        add_grrole()

if __name__ == '__main__':
    main()