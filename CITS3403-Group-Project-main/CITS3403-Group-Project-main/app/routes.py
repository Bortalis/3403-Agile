# app/routes.py

from flask_login import current_user
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Transaction, GroupMembership, Group, Category
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict
import json
from datetime import datetime
from io import BytesIO, StringIO
import csv

# importing api links
from app.api import update_add_transaction, update_delete_transaction, update_edit_transaction

# Imports for charting & PDF
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import hashlib
from .api import update_add_transaction
from .api import create_new_group, update_edit_group

main = Blueprint('main', __name__)


# Route: Home page
@main.route('/')
def landing():
    return render_template('home.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['username']
        raw_pw = request.form['password']

        # Werkzeug will salt & hash
        hashed_pw = generate_password_hash(raw_pw)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.')
            return redirect(url_for('main.signup'))

        new_user = User(
            email=email,
            fname=fname,
            lname=lname,
            password=hashed_pw
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful. Please login.')
        return redirect(url_for('main.login'))

    return render_template('signUp.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        raw_pw = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user:
            # 1) Try the new Werkzeug check
            if check_password_hash(user.password, raw_pw):
                login_user(user)
                return redirect(url_for('main.dashboard'))

            # 2) Fallback: old SHA-256
            legacy = hashlib.sha256(raw_pw.encode()).hexdigest()
            if user.password == legacy:
                # upgrade to salted hash
                user.password = generate_password_hash(raw_pw)
                db.session.commit()
                login_user(user)
                return redirect(url_for('main.dashboard'))

        flash('Invalid credentials.')
        return redirect(url_for('main.login'))

    return render_template('logIn.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    transactions = Transaction.query.filter_by(
        usid=user.usid).order_by(Transaction.date).all()

    total_income = sum(
        t.amount for t in transactions if t.type.lower() == 'income')
    total_expense = sum(
        t.amount for t in transactions if t.type.lower() == 'expense')
    net_balance = total_income - total_expense
    recent_txns = transactions[-10:][::-1]

    # chart data for template
    monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0})
    category_data = defaultdict(float)
    for t in transactions:
        month = t.date.replace(day=1)
        if t.type.lower() == 'income':
            monthly_data[month]['income'] += t.amount
        else:
            monthly_data[month]['expense'] += t.amount
            category_data[t.category] += t.amount

    sorted_months = sorted(monthly_data)
    chart_labels = [m.strftime('%b %Y') for m in sorted_months]
    income_series = [monthly_data[m]['income'] for m in sorted_months]
    expense_series = [monthly_data[m]['expense'] for m in sorted_months]
    category_labels = list(category_data.keys())
    category_values = list(category_data.values())

    return render_template(
        'userData.html',
        user=user,
        transactions=recent_txns,
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
        chart_labels=chart_labels,
        income_series=income_series,
        expense_series=expense_series,
        category_labels=category_labels,
        category_values=category_values
    )


@main.route('/upload')
@login_required
def upload():
    return render_template('uploadData.html')


@main.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    # 1) Find the user's group
    membership = GroupMembership.query.filter_by(
        usid=current_user.usid).first()
    if not membership:
        flash('No group found for your account.')
        return redirect(url_for('main.dashboard'))
    grid_id = membership.grid

    # 2) Parse & validate date and amount
    try:
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        amount = float(request.form['amount'])
    except (ValueError, KeyError):
        flash('Invalid date or amount format.')
        return redirect(url_for('main.dashboard'))

    # 3) Convert type → boolean
    tx_type = request.form.get('type', '').lower()
    if tx_type not in ('income', 'expense'):
        flash('Please choose either Income or Expense.')
        return redirect(url_for('main.dashboard'))
    income_flag = (tx_type == 'income')

    # 4) Look up the category
    cat_name = request.form.get('category', '')
    category = Category.query.filter_by(name=cat_name).first()
    if not category:
        flash(f'Unknown category: {cat_name}')
        return redirect(url_for('main.dashboard'))

    # 5) Create & save, now including grid=…
    update_add_transaction(current_user.usid, grid_id, amount, income_flag, category.catid, date, "")

    flash('Transaction added!')
    return redirect(url_for('main.dashboard'))


@main.route('/upload_csv', methods=['POST'])
@login_required
def upload_csv():
    membership = GroupMembership.query.filter_by(
        usid=current_user.usid).first()
    if not membership:
        flash('No group found for your account.')
        return redirect(url_for('main.upload'))
    grid_id = membership.grid

    file = request.files.get('file')
    if not file:
        flash('Please choose a CSV file.')
        return redirect(url_for('main.upload'))

    reader = csv.DictReader(StringIO(file.stream.read().decode('utf-8')))
    for row in reader:
        # parse/validate each row
        date = datetime.strptime(row['date'], '%Y-%m-%d')
        amount = float(row['amount'])
        income_flag = (row['type'].lower() == 'income')
        cat = Category.query.filter_by(name=row['category']).first()
        if not cat:
            # skip or flash—your choice
            continue

        txn = Transaction(
            usid=current_user.usid,
            grid=grid_id,
            date=date,
            amount=amount,
            income=income_flag,
            catId=cat.catid
        )
        db.session.add(txn)

    db.session.commit()
    flash('CSV imported successfully!')
    return redirect(url_for('main.dashboard'))


@main.route('/group/<int:group_id>')
@login_required
def group_dashboard(group_id):
    # 1) Fetch the group
    group = Group.query.get_or_404(group_id)

    # 2) Find all member IDs in this group
    memberships = GroupMembership.query.filter_by(grid=group_id).all()
    member_ids = [gm.usid for gm in memberships]

    # 3) Compute overall group totals
    txns = Transaction.query.filter(Transaction.usid.in_(member_ids)) \
                             .order_by(Transaction.date.desc()).all()
    total_income   = sum(t.amount for t in txns if t.type.lower() == 'income')
    total_expenses = sum(t.amount for t in txns if t.type.lower() == 'expense')
    net_balance    = total_income - total_expenses

    # 4) Per-member aggregation
    from collections import defaultdict
    per_member = defaultdict(lambda: {'income': 0, 'expense': 0})
    for t in txns:
        if t.type.lower() == 'income':
            per_member[t.usid]['income'] += t.amount
        else:
            per_member[t.usid]['expense'] += t.amount

    member_labels   = [User.query.get(uid).email for uid in member_ids]
    member_incomes  = [per_member[uid]['income'] for uid in member_ids]
    member_expenses = [per_member[uid]['expense'] for uid in member_ids]

    # 5) Group-wide monthly trend & category breakdown
    all_txns = Transaction.query.filter(Transaction.usid.in_(member_ids)) \
                                 .order_by(Transaction.date).all()

    monthly = defaultdict(lambda: {'income': 0, 'expense': 0})
    by_cat  = defaultdict(float)
    for t in all_txns:
        month_key = t.date.replace(day=1)
        if t.type.lower() == 'income':
            monthly[month_key]['income'] += t.amount
        else:
            monthly[month_key]['expense'] += t.amount
            by_cat[t.category] += t.amount

    months = sorted(monthly.keys())
    monthly_labels    = [m.strftime('%b %Y') for m in months]
    monthly_incomes   = [monthly[m]['income'] for m in months]
    monthly_expenses  = [monthly[m]['expense'] for m in months]

    category_labels   = list(by_cat.keys())
    category_expenses = list(by_cat.values())

    # 6) Fetch last 10 for the “Recent Transactions” table
    recent_transactions = (
        Transaction.query
        .filter(Transaction.usid.in_(member_ids))
        .order_by(Transaction.date.desc())
        .limit(10)
        .all()
    )

    for t in recent_transactions:
        t.fname = User.query.get(t.usid).fname

    # 7) Render the template with all datasets + recent_transactions
    return render_template(
        'groupedData.html',
        group=group,
        group_income=total_income,
        group_expenses=total_expenses,
        group_net_balance=net_balance,
        member_labels=member_labels,
        member_incomes=member_incomes,
        member_expenses=member_expenses,
        monthly_labels=monthly_labels,
        monthly_incomes=monthly_incomes,
        monthly_expenses=monthly_expenses,
        category_labels=category_labels,
        category_expenses=category_expenses,
        recent_transactions=recent_transactions
    )



@main.route('/my-groups')
@login_required
def my_groups():
    # Get all groups where the current user is a member
    group_ids = [gm.grid for gm in GroupMembership.query.filter_by(
        usid=current_user.usid).all()]
    groups = Group.query.filter(Group.grid.in_(group_ids)).all()

    return render_template('groupedData.html', groups=groups)


@main.context_processor
def inject_user_groups():
    if current_user.is_authenticated:
        # pull the group‐IDs your user belongs to
        group_ids = [
            gm.grid
            for gm in GroupMembership.query.filter_by(usid=current_user.usid).all()
        ]
        # query by the real PK column `grid`
        user_groups = Group.query.filter(Group.grid.in_(group_ids)).all()
    else:
        user_groups = []
    return dict(user_groups=user_groups)

@main.route('/groups', methods=['GET'])
@login_required
def new_group():
    return render_template('createGroup.html')

@main.route('/groups/new', methods=['POST'])
@login_required
def create_group():
    create_new_group(request.form['name'], int(request.form['type']), float(request.form['amount']))
    return redirect(url_for('main.dashboard'))

@main.route('/groups/edit/<group_id>', methods=['GET'])
def edit_group(group_id):
    #e_group = Group.query.get(group_id)
    return render_template('editGroup.html', groupinfo=group_id)

@main.route('/groups/<int:group_id>/edit', methods=['POST'])
@login_required
def up_edit_group(group_id):
    update_edit_group(group_id, request.form['name'], int(request.form['type']))
    return redirect(url_for('main.dashboard'))


@main.route('/export_pdf')
@login_required
def export_pdf():
    user = current_user
    txns = Transaction.query.filter_by(usid=user.usid).order_by(
        Transaction.date.desc()).limit(10).all()

    total_income = sum(t.amount for t in txns if t.type.lower() == 'income')
    total_expense = sum(t.amount for t in txns if t.type.lower() == 'expense')
    net_balance = total_income - total_expense

    # full series for charting
    all_txns = Transaction.query.filter_by(
        usid=user.usid).order_by(Transaction.date).all()
    md = defaultdict(lambda: {'income': 0, 'expense': 0})
    cd = defaultdict(float)
    for t in all_txns:
        m = t.date.replace(day=1)
        if t.type.lower() == 'income':
            md[m]['income'] += t.amount
        else:
            md[m]['expense'] += t.amount
            cd[t.category] += t.amount

    months = sorted(md)
    labels = [m.strftime('%b %Y') for m in months]
    incs = [md[m]['income'] for m in months]
    exps = [md[m]['expense'] for m in months]

    # --- generate line chart ---
    buf_line = BytesIO()
    plt.figure(figsize=(4, 2.5), dpi=100)
    plt.plot(labels, incs, marker='o', label='Income')
    plt.plot(labels, exps, marker='o', label='Expense')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig(buf_line, format='PNG')
    plt.close()
    buf_line.seek(0)

    # --- generate pie chart ---
    buf_pie = BytesIO()
    plt.figure(figsize=(4, 2.5), dpi=100)
    plt.pie(list(cd.values()), labels=list(cd.keys()), autopct='%1.1f%%')
    plt.tight_layout()
    plt.savefig(buf_pie, format='PNG')
    plt.close()
    buf_pie.seek(0)

    buf_pdf = BytesIO()
    pdf = canvas.Canvas(buf_pdf, pagesize=letter)
    w, h = letter

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(w / 2, h - 50, "My Financial Dashboard")
    pdf.setFont("Helvetica", 12)
    y = h - 80
    pdf.drawString(50, y, f"Total Income:  ${total_income:.2f}")
    y -= 20
    pdf.drawString(50, y, f"Total Expenses: ${total_expense:.2f}")
    y -= 20
    pdf.drawString(50, y, f"Net Balance:    ${net_balance:.2f}")
    y -= 40

    pdf.drawImage(ImageReader(buf_line), 50, y - 200, width=260, height=160)
    pdf.drawImage(ImageReader(buf_pie), 300, y - 200, width=260, height=160)
    y -= 220

    pdf.setFont("Helvetica-Bold", 12)
    for x, lbl in zip((50, 150, 260, 400), ("Date", "Type", "Category", "Amount")):
        pdf.drawString(x, y, lbl)
    y -= 20

    pdf.setFont("Helvetica", 12)
    for t in txns:
        pdf.drawString(50, y, t.date.strftime("%Y-%m-%d"))
        pdf.drawString(150, y, t.type.title())
        pdf.drawString(260, y, t.category.title())
        amt = f"-${t.amount:.2f}" if t.type.lower() == "expense" else f"+${t.amount:.2f}"
        pdf.drawRightString(500, y, amt)
        y -= 20
        if y < 100:
            pdf.showPage()
            y = h - 50

    pdf.showPage()
    pdf.save()
    buf_pdf.seek(0)

    return Response(
        buf_pdf,
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment;filename=dashboard.pdf'}
    )


@main.route('/group/<int:group_id>/export_pdf')
@login_required
def export_group_pdf(group_id):
    # 1) Fetch group & member IDs
    group = Group.query.get_or_404(group_id)
    member_ids = [gm.usid for gm in GroupMembership.query.filter_by(grid=group_id).all()]

    # 2) All transactions for summary & aggregation
    all_txns = (
        Transaction.query
        .filter(Transaction.usid.in_(member_ids))
        .order_by(Transaction.date)
        .all()
    )

    # 3) Summary over all_txns
    total_income   = sum(t.amount for t in all_txns if t.type == 'income')
    total_expenses = sum(t.amount for t in all_txns if t.type == 'expense')
    net_balance    = total_income - total_expenses

    # 4) Last 10 for detail table
    recent = all_txns[-10:][::-1]

    # 5) Monthly trend & category breakdown
    monthly = defaultdict(lambda: {'income': 0, 'expense': 0})
    by_cat  = defaultdict(float)
    for t in all_txns:
        m = t.date.replace(day=1)
        if t.type == 'income':
            monthly[m]['income'] += t.amount
        else:
            monthly[m]['expense'] += t.amount
            by_cat[t.category] += t.amount

    months     = sorted(monthly.keys())
    labels     = [m.strftime('%b %Y') for m in months]
    incs       = [monthly[m]['income'] for m in months]
    exps       = [monthly[m]['expense'] for m in months]
    cat_labels = list(by_cat.keys())
    cat_vals   = list(by_cat.values())

    # 6) Build charts into buffers
    # Line chart
    buf_line = BytesIO()
    plt.figure(figsize=(4,2.5), dpi=100)
    plt.plot(labels, incs, marker='o', label='Income')
    plt.plot(labels, exps, marker='o', label='Expense')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig(buf_line, format='PNG')
    plt.close()
    buf_line.seek(0)

    # Pie chart
    buf_pie = BytesIO()
    plt.figure(figsize=(4,2.5), dpi=100)
    plt.pie(cat_vals, labels=cat_labels, autopct='%1.1f%%')
    plt.tight_layout()
    plt.savefig(buf_pie, format='PNG')
    plt.close()
    buf_pie.seek(0)

    # 7) Create PDF
    buf_pdf = BytesIO()
    pdf = canvas.Canvas(buf_pdf, pagesize=letter)
    w, h = letter

    # Title & summary
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(w/2, h-50, f"{group.grname} Financial Overview")
    pdf.setFont("Helvetica", 12)
    y = h - 80
    pdf.drawString(50, y, f"Total Group Income:   ${total_income:.2f}")
    y -= 20
    pdf.drawString(50, y, f"Total Group Expenses: ${total_expenses:.2f}")
    y -= 20
    pdf.drawString(50, y, f"Net Balance:          ${net_balance:.2f}")
    y -= 40

    # Insert charts
    pdf.drawImage(ImageReader(buf_line), 50, y-200, width=260, height=160)
    pdf.drawImage(ImageReader(buf_pie), 300, y-200, width=260, height=160)
    y -= 220

    # Table header (First Name instead of User)
    pdf.setFont("Helvetica-Bold", 12)
    cols = ("First Name", "Date", "Type", "Category", "Amount")
    xs   = (50,           120,    220,     310,        410)
    for x, lbl in zip(xs, cols):
        pdf.drawString(x, y, lbl)
    y -= 20
    pdf.setFont("Helvetica", 12)

    # Table rows (recent 10) with first names
    for t in recent:
        first_name = User.query.get(t.usid).fname
        pdf.drawString(50, y, first_name)
        pdf.drawString(120, y, t.date.strftime("%Y-%m-%d"))
        pdf.drawString(220, y, t.type.title())
        pdf.drawString(310, y, t.category.title())
        amt = f"-${t.amount:.2f}" if t.type == 'expense' else f"+${t.amount:.2f}"
        pdf.drawRightString(500, y, amt)
        y -= 20
        if y < 100:
            pdf.showPage()
            y = h - 50

    pdf.showPage()
    pdf.save()
    buf_pdf.seek(0)

    return Response(
        buf_pdf,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment;filename={group.grname}_overview.pdf'}
    )

# functionality to delete row of called transaction
@main.route('/deletetransaction/<int:tr_id>', methods=['GET'])
@login_required
def delete_transaction(tr_id):
    update_delete_transaction(tr_id)

    flash('Transaction Deleted!')
    return redirect(url_for('main.dashboard'))

# Add functionality to update entry based on what parts of the transaction are edited
@main.route('/edit/<int:tr_id>', methods=['GET'])
@login_required
def edit_transaction(tr_id):
    e_transaction = Transaction.query.get(tr_id)
    return render_template('editTransaction.html', transaction=e_transaction)

# Add functionality to update entry based on what parts of the transaction are edited
@main.route('/edit/<int:tr_id>', methods=['POST'])
@login_required
def update_transaction(tr_id):
    update_edit_transaction(tr_id, 3, float(request.form['amount']),
                                request.form['type'], 1, datetime.strptime(request.form['date'], '%Y-%m-%d'),
                                "")

    flash('Transaction edited!')
    return redirect(url_for('main.dashboard'))