from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Income
from datetime import datetime, date
from sqlalchemy import extract, func
import calendar

income_bp = Blueprint('income', __name__, url_prefix='/income')

INCOME_SOURCES = [
    'Salary',
    'Freelance',
    'Investments / Dividends',
    'Business / Sales',
    'Rental Income',
    'Bonus / Incentive',
    'Stipend / Internship',
    'Interest',
    'Gift / Allowance',
    'Other'
]

@income_bp.route('/', methods=['GET'])
@login_required
def index():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    source_filter = request.args.get('source', '').strip()
    search_query = request.args.get('q', '').strip()

    query = Income.query.filter_by(user_id=current_user.id)

    if month:
        query = query.filter(extract('month', Income.date) == month)
    if year:
        query = query.filter(extract('year', Income.date) == year)
    if source_filter:
        query = query.filter(Income.source == source_filter)
    if search_query:
        query = query.filter(Income.title.ilike(f'%{search_query}%'))

    incomes = query.order_by(Income.date.desc(), Income.id.desc()).all()

    # Calculate total for current filter
    total_income = sum(item.amount for item in incomes)
    
    # Calculate monthly recurring total
    recurring_total = sum(item.amount for item in incomes if item.is_recurring)

    today = date.today()
    cur_year = today.year
    available_years = [cur_year - 2, cur_year - 1, cur_year, cur_year + 1]

    return render_template(
        'income/index.html',
        incomes=incomes,
        total_income=round(total_income, 2),
        recurring_total=round(recurring_total, 2),
        income_sources=INCOME_SOURCES,
        selected_month=month,
        selected_year=year,
        selected_source=source_filter,
        search_query=search_query,
        available_years=available_years,
        today=today.strftime('%Y-%m-%d')
    )


@income_bp.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    source = request.form.get('source', 'Other').strip()
    date_str = request.form.get('date', '').strip()
    notes = request.form.get('notes', '').strip()
    is_recurring = bool(request.form.get('is_recurring'))

    if not title:
        flash('Please provide an income title / description.', 'danger')
        return redirect(url_for('income.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Income amount must be greater than 0.', 'danger')
            return redirect(url_for('income.index'))
    except ValueError:
        flash('Invalid amount entered.', 'danger')
        return redirect(url_for('income.index'))

    try:
        income_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    except ValueError:
        income_date = date.today()

    new_income = Income(
        user_id=current_user.id,
        title=title,
        amount=amount,
        source=source,
        date=income_date,
        notes=notes,
        is_recurring=is_recurring
    )

    db.session.add(new_income)
    db.session.commit()
    flash(f'Income "₹{amount:,.2f} - {title}" added successfully!', 'success')
    return redirect(url_for('income.index'))


@income_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    title = request.form.get('title', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    source = request.form.get('source', 'Other').strip()
    date_str = request.form.get('date', '').strip()
    notes = request.form.get('notes', '').strip()
    is_recurring = bool(request.form.get('is_recurring'))

    if not title:
        flash('Title cannot be empty.', 'danger')
        return redirect(url_for('income.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Amount must be greater than 0.', 'danger')
            return redirect(url_for('income.index'))
    except ValueError:
        flash('Invalid amount entered.', 'danger')
        return redirect(url_for('income.index'))

    try:
        income_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else income.date
    except ValueError:
        income_date = income.date

    income.title = title
    income.amount = amount
    income.source = source
    income.date = income_date
    income.notes = notes
    income.is_recurring = is_recurring

    db.session.commit()
    flash('Income updated successfully.', 'success')
    return redirect(url_for('income.index'))


@income_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    title = income.title
    amount = income.amount
    db.session.delete(income)
    db.session.commit()
    flash(f'Deleted income entry "{title}" (₹{amount:,.2f}).', 'info')
    return redirect(url_for('income.index'))
