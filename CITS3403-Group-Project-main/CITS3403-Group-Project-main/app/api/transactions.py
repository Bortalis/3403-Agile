""" This python script is for storing functions that are used to
 interact with the transactions table """
from app.models import db, Transaction, Group, GroupBalance, Note
from datetime import datetime

# function to return true if string is True or false if it is not
def is_income(income):
    if income == "income":
        return True
    else:
        return False

# function to add transaction to the db
def update_add_transaction(add_user_id, add_group_id, add_amount, add_income, add_cat_id, add_date, add_note):
    new_trn = Transaction(
        usid=add_user_id,
        grid=add_group_id,
        income=add_income,
        amount=add_amount,
        catId=add_cat_id,
        date=add_date,
        noteid=new_note(add_note)
    )

    db.session.add(new_trn)
    db.session.flush()

    add_group_balance(new_trn.trid, new_trn.grid, new_trn.amount, new_trn.date, new_trn.income)
    db.session.commit()

# Function to add note
def new_note(add_note):
    if add_note == "":
        return 1
    else:
        n_note = Note(content=add_note)
        new_note_id = n_note.noteid
        db.session.add(n_note)
        db.session.commit()
        return new_note_id


# function to delete transaction
def update_delete_transaction(del_trn_id):
    del_trn = Transaction.query.get(del_trn_id)

    delete_group_balance(del_trn.grid, del_trn.amount, del_trn_id, del_trn.income)

    if del_trn.noteid != 1:
       delete_note(del_trn.noteid)

    db.session.delete(del_trn)
    db.session.commit()

def delete_note(del_noteid):
    del_note = Note.query.get(del_noteid)
    db.session.delete(del_note)
    db.session.commit()

# function to edit transaction
def update_edit_transaction(ed_tran_id, ed_group_id, ed_amount, ed_income, ed_cat_id, ed_date, ed_note):
    edit_trn = Transaction.query.get(ed_tran_id)
    
    edit_trn.grid = ed_group_id
    edit_trn.amount = ed_amount
    edit_trn.income = is_income(ed_income)
    edit_trn.date = ed_date
    edit_trn.catId = ed_cat_id
    edit_trn.noteid = edit_note(edit_trn.noteid, ed_note)

    db.session.commit()

# Function to edit note for transaction
def edit_note(old_noteid, ed_note):
    old_note = Note.query.get(old_noteid)
    if old_noteid == 1:
        return 1
    elif old_note.content == ed_note:
        return old_noteid
    elif old_noteid == 1 and ed_note != "":
        new_note_id = new_note(ed_note)
        return new_note_id
    elif old_noteid != 1 and ed_note == "":
        delete_note(old_noteid)
        return 1
    else:
        old_note.note  = ed_note
        db.session.commit()
        return old_noteid

# Function to update the group balance when a transaction is added
def add_group_balance(agb_trn_id, agb_group_id, agb_trn_amount, agb_date, agb_income):
    agb_group = Group.query.get(agb_group_id)
    current_balance = agb_group.balance

    if agb_income:
        new_balance = current_balance + agb_trn_amount
    else:
        new_balance = current_balance - agb_trn_amount

    balance_record = GroupBalance(balanceid=agb_trn_id, grid=agb_group_id, date=agb_date, up_balance=new_balance)

    agb_group.balance = new_balance
    db.session.add(balance_record)
    db.session.commit()

# Function to update the group balance when a transaction is deleted
def delete_group_balance(dgb_group_id, dgb_amount, dgb_id, dgb_income):
    dgb_group = Group.query.get(dgb_group_id)
    current_balance = dgb_group.balance

    if dgb_income:
        dgb_balance = current_balance - dgb_amount
    else:
        dgb_balance = current_balance + dgb_amount

    bl_history = GroupBalance.query.get(dgb_id)

    db.session.delete(bl_history)
    dgb_group.balance = dgb_balance
    db.session.commit()

# Function to update the group balance when a transaction is updated
def edit_group_balance(edg_trn_id, edg_grid, old_amount, new_amount, edg_date, old_income, new_income):
    edg_group = Group.query.get(edg_grid)
    gbl_history = GroupBalance.query.get(edg_trn_id)

    current_balance = edg_group.balance
    if old_income == True and new_income == True:
        new_balance = current_balance - old_amount + new_amount
    elif old_income == False and new_income == False:
        new_balance = current_balance + old_amount - new_amount
    elif old_income == True and new_income == False:
        new_balance = current_balance - old_amount - new_amount
    else:
        new_balance = current_balance + old_amount + new_amount

    edg_group.balance = new_balance

    gbl_history.date = datetime.strptime(edg_date, '%Y-%m-%d')
    gbl_history.balance = new_balance

    db.session.commit()
