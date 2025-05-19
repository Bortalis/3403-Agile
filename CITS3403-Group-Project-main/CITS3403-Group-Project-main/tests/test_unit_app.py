import unittest
from app import create_app, db
from app.config import TestConfig, basedir
from app.models import User, Transaction, Group, GroupBalance
from app import db
from datetime import datetime

class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    # test add group
    def test_add_group(self):
        from app.api.groups import create_new_group

        create_new_group("test", 1, 100.00)

        group = Group.query.filter_by(grid=1).first()
        self.assertIsNotNone(group)
        self.assertEqual(group.grname, "test")
        self.assertEqual(group.grtype, 1)
        self.assertEqual(group.balance, 100.00)
    
    # test edit group
    def test_edit_group(self):
        from app.api.groups import update_edit_group
        ed_group = Group(
            grid=2,
            grname='Test Group',
            grtype=1,
            balance=100.00
        )
        db.session.add(ed_group)
        db.session.commit()

        update_edit_group(2, 'Updated Group', 2)

        group = Group.query.filter_by(grid=2).first()
        self.assertIsNotNone(group)
        self.assertEqual(group.grname, 'Updated Group')
        self.assertEqual(group.grtype, 2)

    # test add user
    def test_add_user(self):

        ad_usr = User(
            fname="John",
            lname="Smith",
            password="crane64",
            email="testuser@example.com"
        )
        db.session.add(ad_usr)
        db.session.commit()

        user = User.query.filter_by(email='testuser@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.fname, 'John')
        self.assertEqual(user.lname, 'Smith')
        self.assertEqual(user.password, 'crane64')
        self.assertEqual(user.email, 'testuser@example.com')

    #test add transaction
    def test_add_transaction(self):
        from app.api.transactions import update_add_transaction

        group_balance = GroupBalance(
        balanceid=7,
        grid=7,
        up_balance=100.00,
        date=datetime.strptime('2025-05-06', '%Y-%m-%d').date())
        group = Group(
            grid=7,
            grname='Test Group',
            grtype=1,
            balance=100.00)
        db.session.add(group_balance)
        db.session.add(group)
        db.session.commit()

        transaction_date = datetime.strptime('2025-05-08', '%Y-%m-%d').date()
        update_add_transaction(1, 7, 100.00, True, 1, transaction_date, "")

        transaction = Transaction.query.filter_by(trid=1).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.usid, 1)
        self.assertEqual(transaction.grid, 7)
        self.assertTrue(transaction.income, True)
        self.assertEqual(transaction.amount, 100.00)
        self.assertEqual(transaction.catId, 1)
        self.assertEqual(transaction.date, transaction_date)
        self.assertEqual(transaction.noteid, 1)


    # test edit transaction
    def test_edit_transaction(self):
        from app.api.transactions import update_edit_transaction
        ed_trn = Transaction(
            trid=10,
            usid=1,
            grid=1,
            income=True,
            amount=100.00,
            catId=1,
            date=datetime.strptime('2025-05-06', '%Y-%m-%d').date(),
            noteid=1
        )
        db.session.add(ed_trn)
        db.session.commit()

        update_edit_transaction(10, 1, 200.00, False, 2, datetime.strptime('2025-05-06', '%Y-%m-%d').date(), "")

        transaction = Transaction.query.filter_by(trid=10).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.grid, 1)
        self.assertFalse(transaction.income, False)
        self.assertEqual(transaction.amount, 200.00)
        self.assertEqual(transaction.catId, 2)
        self.assertEqual(transaction.date, datetime.strptime('2025-05-06', '%Y-%m-%d').date())
        self.assertEqual(transaction.noteid, 1)

    #test delete transaction
    def test_delete_transaction(self):
        from app.api.transactions import update_delete_transaction
        transaction = Transaction(
            trid=5,
            usid=1,
            grid=3,
            income=True,
            amount=100.00,
            catId=1,
            date=datetime.strptime('2025-05-06', '%Y-%m-%d').date(),
            noteid=1
        )
        db.session.add(transaction)
        group_balance = GroupBalance(
        balanceid=5,
        grid=3,
        up_balance=100.00,
        date=datetime.strptime('2025-05-06', '%Y-%m-%d').date())
        db.session.add(group_balance)
        del_group = Group( 
            grid=3,
            grname='Test Group',
            grtype=1,
            balance=100.00
        )
        db.session.add(del_group)
        db.session.commit()

        # Check if the transaction exists before deletion        
        update_delete_transaction(5)

        transaction = Transaction.query.filter_by(trid=5).first()
        self.assertIsNone(transaction)

    
if __name__ == '__main__':
    unittest.main()
