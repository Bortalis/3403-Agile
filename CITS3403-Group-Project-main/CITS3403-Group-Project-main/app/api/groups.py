from app.models import db, Transaction, Group, GroupBalance, Note

def create_new_group(gr_name, gr_type, starting_bal):
    new_gr = Group(grname=gr_name, grtype=gr_type, balance=starting_bal)
    db.session.add(new_gr)
    db.session.commit()

# to be added
# funciton to update group balance hist
# update group membership
# add group members and roles
# group creator is owner

def update_edit_group(gr_id, gr_name, gr_type):
    ed_group = Group.query.get(gr_id)

    ed_group.grname = gr_name
    ed_group.grtype = gr_type

    db.session.commit()