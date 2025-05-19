from app import create_app
import csv
import os
from datetime import datetime
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from app.models import db, Transaction, Group, GroupBalance
from app.api import update_add_transaction, is_income
from app.api import create_new_group
from app.config import ProductionConfig

def delete_all_transactions():
    transactions = Transaction.query.all()
    for transaction in transactions:
        db.session.delete(transaction)
    db.session.commit()

def delete_all_groups():
    groups = Group.query.all()
    for group in groups:
        db.session.delete(group)
    db.session.commit()

def delete_all_group_balances():
    group_balances = GroupBalance.query.all()
    for group_balance in group_balances:
        db.session.delete(group_balance)
    db.session.commit()

def import_groups(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            add_group_name = row['groupname']
            add_group_type = row['group_type']
            create_new_group(add_group_name, add_group_type, 0.00)

def import_transactions(csv_file):
    
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            add_user_id = int(row['user_id'])
            add_group_id = int(row['group_id'])
            add_amount = float(row['amount'])
            add_income = is_income(row['income'])
            add_cat_id = int(row['category'])
            add_date = datetime.strptime(row['date'],  '%Y-%m-%d %H:%M:%S').date()
            add_note = row['notes']

            update_add_transaction(add_user_id, add_group_id, add_amount, add_income, add_cat_id, add_date, add_note)

def main():
    app = create_app(ProductionConfig)

    with app.app_context():
        delete_all_transactions()
        delete_all_groups()
        delete_all_group_balances()
        import_groups('mock_groups_2.csv')
        import_transactions('mock_transaction_2.csv')

if __name__ == '__main__':
    main()