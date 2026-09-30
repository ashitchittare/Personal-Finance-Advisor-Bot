from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Budget, Expense
from app.routes.expense import EXPENSE_CATEGORIES
from app.services.analytics import get_current_month_year, get_month_name
from sqlalchemy import extract, func

budget_bp = Blueprint('budget', __name__, url_prefix='/budgets')

@budget_bp.route('/', methods=['GET'])
@login_required
def index():
    cur_m, cur_y = get_current_month_year()
    month = request.args.get('month', type=int) or cur_m
    year = request.args.get('year', type=int) or cur_y

    budgets = Budget.query.filter_by(user_id=current_user.id, month=month, year=year).all()

    # Get actual spending for each category in this month/year
    expense_rows = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).group_by(Expense.category).all()

    spending_map = {cat: float(total) for cat, total in expense_rows}

    # Aggregate budget vs actual list
    budget_items = []
    total_budget = 0.0
    total_spent = 0.0
    over_budget_count = 0

    budgeted_categories = set()

    for b in budgets:
        budgeted_categories.add(b.category)
        spent = spending_map.get(b.category, 0.0)
        remaining = round(b.amount - spent, 2)
        pct = round((spent / b.amount * 100.0), 1) if b.amount > 0 else 100.0
        is_over = spent > b.amount
        if is_over:
            over_budget_count += 1

        total_budget += b.amount
        total_spent += spent

        budget_items.append({
            'id': b.id,
            'category': b.category,
            'budget_amount': b.amount,
            'spent_amount': spent,
            'remaining_amount': remaining,
            'percentage_used': pct,
            'is_over_budget': is_over
        })

    # Find unbudgeted categories that had spending this month
    unbudgeted_items = []
    for cat, spent in spending_map.items():
        if cat not in budgeted_categories:
            unbudgeted_items.append({
                'category': cat,
                'spent_amount': spent
            })
            total_spent += spent

    total_remaining = round(total_budget - total_spent, 2)
    overall_pct = round((total_spent / total_budget * 100.0), 1) if total_budget > 0 else 0.0

    available_years = [cur_y - 2, cur_y - 1, cur_y, cur_y + 1]

    return render_template(
        'budget/index.html',
        budget_items=budget_items,
        unbudgeted_items=unbudgeted_items,
        total_budget=round(total_budget, 2),
        total_spent=round(total_spent, 2),
        total_remaining=total_remaining,
        overall_pct=overall_pct,
        over_budget_count=over_budget_count,
        categories=EXPENSE_CATEGORIES,
        selected_month=month,
        selected_year=year,
        month_name=get_month_name(month),
        available_years=available_years
    )


@budget_bp.route('/set', methods=['POST'])
@login_required
def set_budget():
    category = request.form.get('category', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    month = request.form.get('month', type=int)
    year = request.form.get('year', type=int)

    if not category or not month or not year:
        flash('Category, month, and year are required.', 'danger')
        return redirect(url_for('budget.index', month=month, year=year))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Budget amount must be greater than 0.', 'danger')
            return redirect(url_for('budget.index', month=month, year=year))
    except ValueError:
        flash('Invalid budget amount.', 'danger')
        return redirect(url_for('budget.index', month=month, year=year))

    existing = Budget.query.filter_by(
        user_id=current_user.id,
        category=category,
        month=month,
        year=year
    ).first()

    if existing:
        existing.amount = amount
        flash(f'Budget for "{category}" updated to ₹{amount:,.2f} for {get_month_name(month)} {year}.', 'success')
    else:
        new_budget = Budget(
            user_id=current_user.id,
            category=category,
            amount=amount,
            month=month,
            year=year
        )
        db.session.add(new_budget)
        flash(f'Budget for "{category}" set to ₹{amount:,.2f} for {get_month_name(month)} {year}.', 'success')

    db.session.commit()
    return redirect(url_for('budget.index', month=month, year=year))


@budget_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    cat = budget.category
    m = budget.month
    y = budget.year
    db.session.delete(budget)
    db.session.commit()
    flash(f'Removed budget limit for "{cat}".', 'info')
    return redirect(url_for('budget.index', month=m, year=y))
