from app import db
from datetime import datetime
from sqlalchemy.orm import relationship
from flask_login import UserMixin

class Project:
    def __init__(self, users):
        self.users = users

# User Table
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    usid     = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    fname    = db.Column(db.String(20), nullable=False)
    lname    = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def get_id(self):
        # Flask-Login expects this method to return a unicode ID
        return str(self.usid)

    def __repr__(self):
        return f'<User {self.usid}>'
    
# Transaction Table
class Transaction(db.Model):
    __tablename__ = 'transactions'

    trid    = db.Column(db.Integer, primary_key=True)
    usid    = db.Column(db.Integer, db.ForeignKey('users.usid'), nullable=False)
    grid    = db.Column(db.Integer, db.ForeignKey('groups.grid'), nullable=False)
    amount  = db.Column(db.Float, nullable=False)
    income  = db.Column(db.Boolean, nullable=False)  # False = expense, True = income
    catId   = db.Column(db.Integer, db.ForeignKey('categories.catid'), nullable=False)
    date    = db.Column(db.Date, nullable=False)
    noteid  = db.Column(db.Integer, db.ForeignKey('notes.noteid'), nullable=True)

    # link to category record
    category_rel = relationship('Category', foreign_keys=[catId])

    @property
    def type(self) -> str:
        """Return 'income' or 'expense' for existing code that does t.type."""
        return 'income' if self.income else 'expense'

    @property
    def category(self) -> str:
        """Return the category name for existing code that does t.category."""
        return self.category_rel.name

    def __repr__(self):
        return f'<Transaction {self.trid}>'

# Category Dimension Table
class Category(db.Model):
    __tablename__ = 'categories'

    catid = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Category {self.catid}>'

# Notes Dimension Table
class Note(db.Model):
    __tablename__ = 'notes'

    noteid  = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Note {self.noteid}>'

# Group Table 
class Group(db.Model):  
    __tablename__ = 'groups'

    grid    = db.Column(db.Integer, primary_key=True)
    grname  = db.Column(db.String(50), nullable=False)
    grtype  = db.Column(db.Integer, db.ForeignKey('group_types.grtype'), nullable=False)
    balance = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Group {self.grid}>'

# Group Type Dimension Table
class GroupType(db.Model):
    __tablename__ = 'group_types'

    grtype      = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<GroupType {self.grtype}>'

# Group Membership Table
class GroupMembership(db.Model):
    __tablename__ = 'group_memberships'

    usid   = db.Column(db.Integer, db.ForeignKey('users.usid'),   primary_key=True)
    grid   = db.Column(db.Integer, db.ForeignKey('groups.grid'), primary_key=True)
    roleid = db.Column(db.Integer, db.ForeignKey('group_roles.roleid'), nullable=False)

    def __repr__(self):
        return f'<GroupMembership {self.usid}:{self.grid}>'
    
# Group Role Dimension Table
class GroupRole(db.Model):
    __tablename__ = 'group_roles'

    roleid = db.Column(db.Integer, primary_key=True)
    title  = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<GroupRole {self.roleid}>'

# Past Group Balance Table

class GroupBalance(db.Model):

    __tablename__ = 'past_group_balances'

    balanceid = db.Column(db.Integer, primary_key=True)  # Primary key for the balance record
    grid = db.Column(db.Integer, db.ForeignKey('groups.grid'))
    date = db.Column(db.Date, nullable=True)  # Date of the balance
    up_balance = db.Column(db.Float, nullable=False)  # Balance of the group on that date

    def __repr__(self):
        return f'<PastGroupBalance {self.grid}:{self.date}>'