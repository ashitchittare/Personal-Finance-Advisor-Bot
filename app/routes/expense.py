from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Expense
from datetime import datetime, date
from sqlalchemy import extract, func

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')

EXPENSE_CATEGORIES = [
    'Food & Dining',
    'Transport & Fuel',
    'Rent & Housing',
    'Utilities & Bills',
    'Education & Books',
    'Shopping & Electronics',
    'Entertainment & OTT',
    'Healthcare & Medical',
    'Personal Care & Fitness',
    'Travel & Vacation',
    'Investments & SIP',
    'Groceries',
    'Miscellaneous'
]

PAYMENT_METHODS = [
    'UPI (GooglePay/PhonePe/Paytm)',
    'Credit Card',
    'Debit Card',
    'Net Banking',
    'Cash'
]

@expense_bp.route('/', methods=['GET'])
@login_required
def index():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    category_filter = request.args.get('category', '').strip()
    payment_filter = request.args.get('payment_method', '').strip()
    search_query = request.args.get('q', '').strip()

    query = Expense.query.filter_by(user_id=current_user.id)

    if month:
        query = query.filter(extract('month', Expense.date) == month)
    if year:
        query = query.filter(extract('year', Expense.date) == year)
    if category_filter:
        query = query.filter(Expense.category == category_filter)
    if payment_filter:
        query = query.filter(Expense.payment_method == payment_filter)
    if search_query:
        query = query.filter(Expense.title.ilike(f'%{search_query}%'))

    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).all()

    total_expense = sum(item.amount for item in expenses)
    expense_count = len(expenses)
    avg_expense = (total_expense / expense_count) if expense_count > 0 else 0.0

    today = date.today()
    cur_year = today.year
    available_years = [cur_year - 2, cur_year - 1, cur_year, cur_year + 1]

    return render_template(
        'expense/index.html',
        expenses=expenses,
        total_expense=round(total_expense, 2),
        expense_count=expense_count,
        avg_expense=round(avg_expense, 2),
        categories=EXPENSE_CATEGORIES,
        payment_methods=PAYMENT_METHODS,
        selected_month=month,
        selected_year=year,
        selected_category=category_filter,
        selected_payment=payment_filter,
        search_query=search_query,
        available_years=available_years,
        today=today.strftime('%Y-%m-%d')
    )


@expense_bp.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    category = request.form.get('category', 'Miscellaneous').strip()
    payment_method = request.form.get('payment_method', 'UPI').strip()
    date_str = request.form.get('date', '').strip()
    notes = request.form.get('notes', '').strip()

    if not title:
        flash('Please provide an expense title / description.', 'danger')
        return redirect(url_for('expense.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Expense amount must be greater than 0.', 'danger')
            return redirect(url_for('expense.index'))
    except ValueError:
        flash('Invalid expense amount entered.', 'danger')
        return redirect(url_for('expense.index'))

    try:
        exp_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    except ValueError:
        exp_date = date.today()

    new_expense = Expense(
        user_id=current_user.id,
        title=title,
        amount=amount,
        category=category,
        payment_method=payment_method,
        date=exp_date,
        notes=notes
    )

    db.session.add(new_expense)
    db.session.commit()
    flash(f'Expense "₹{amount:,.2f} - {title}" added successfully!', 'success')
    return redirect(url_for('expense.index'))


@expense_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    title = request.form.get('title', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    category = request.form.get('category', 'Miscellaneous').strip()
    payment_method = request.form.get('payment_method', 'UPI').strip()
    date_str = request.form.get('date', '').strip()
    notes = request.form.get('notes', '').strip()

    if not title:
        flash('Expense title cannot be empty.', 'danger')
        return redirect(url_for('expense.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Expense amount must be greater than 0.', 'danger')
            return redirect(url_for('expense.index'))
    except ValueError:
        flash('Invalid amount entered.', 'danger')
        return redirect(url_for('expense.index'))

    try:
        exp_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else expense.date
    except ValueError:
        exp_date = expense.date

    expense.title = title
    expense.amount = amount
    expense.category = category
    expense.payment_method = payment_method
    expense.date = exp_date
    expense.notes = notes

    db.session.commit()
    flash('Expense updated successfully.', 'success')
    return redirect(url_for('expense.index'))


@expense_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    title = expense.title
    amount = expense.amount
    db.session.delete(expense)
    db.session.commit()
    flash(f'Deleted expense entry "{title}" (₹{amount:,.2f}).', 'info')
    return redirect(url_for('expense.index'))
