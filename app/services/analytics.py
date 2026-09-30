from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
from app.models import db, Income, Expense, Budget, SavingsGoal, FinancialReport
import calendar

def get_current_month_year():
    today = date.today()
    return today.month, today.year

def get_month_name(month_num):
    return calendar.month_name[month_num]

def get_financial_summary(user_id, month=None, year=None):
    """
    Computes a comprehensive financial snapshot for a user for a given month and year.
    If month/year is None, defaults to the current month & year.
    """
    if month is None or year is None:
        month, year = get_current_month_year()
    
    # 1. Total Income for the month
    income_q = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
        Income.user_id == user_id,
        extract('month', Income.date) == month,
        extract('year', Income.date) == year
    ).scalar()
    total_income = round(float(income_q), 2)

    # 2. Total Expenses for the month
    expense_q = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
        Expense.user_id == user_id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).scalar()
    total_expenses = round(float(expense_q), 2)

    # 3. Net Savings and Savings Rate
    net_savings = round(total_income - total_expenses, 2)
    if total_income > 0:
        savings_rate = round((net_savings / total_income) * 100.0, 1)
    else:
        savings_rate = 0.0 if total_expenses == 0 else -100.0

    # 4. Expense Breakdown by Category
    category_rows = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total'),
        func.count(Expense.id).label('count')
    ).filter(
        Expense.user_id == user_id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).all()

    category_breakdown = []
    for cat, total, count in category_rows:
        tot = round(float(total), 2)
        pct = round((tot / total_expenses * 100.0), 1) if total_expenses > 0 else 0.0
        category_breakdown.append({
            'category': cat,
            'total': tot,
            'percentage': pct,
            'count': count
        })

    # 5. Income Breakdown by Source
    source_rows = db.session.query(
        Income.source,
        func.sum(Income.amount).label('total'),
        func.count(Income.id).label('count')
    ).filter(
        Income.user_id == user_id,
        extract('month', Income.date) == month,
        extract('year', Income.date) == year
    ).group_by(Income.source).order_by(func.sum(Income.amount).desc()).all()

    income_sources = []
    for src, total, count in source_rows:
        tot = round(float(total), 2)
        pct = round((tot / total_income * 100.0), 1) if total_income > 0 else 0.0
        income_sources.append({
            'source': src,
            'total': tot,
            'percentage': pct,
            'count': count
        })

    # 6. Budget Status & Compliance for this month
    budgets = Budget.query.filter_by(user_id=user_id, month=month, year=year).all()
    budget_status = []
    total_budgeted = 0.0
    total_budget_spent = 0.0
    over_budget_count = 0

    # Map actual expenses by category for easy lookup
    cat_expense_map = {item['category']: item['total'] for item in category_breakdown}

    for b in budgets:
        spent = cat_expense_map.get(b.category, 0.0)
        remaining = round(b.amount - spent, 2)
        pct_used = round((spent / b.amount * 100.0), 1) if b.amount > 0 else 100.0
        is_over = spent > b.amount
        if is_over:
            over_budget_count += 1
        
        total_budgeted += b.amount
        total_budget_spent += spent

        budget_status.append({
            'id': b.id,
            'category': b.category,
            'budget_amount': b.amount,
            'spent_amount': spent,
            'remaining_amount': remaining,
            'percentage_used': pct_used,
            'is_over_budget': is_over
        })

    total_budgeted = round(total_budgeted, 2)
    total_budget_spent = round(total_budget_spent, 2)

    # 7. Savings Goals
    goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.deadline.asc()).all()
    goals_data = [g.to_dict() for g in goals]

    # 8. Recent Transactions (last 8 combined)
    recent_incomes = Income.query.filter_by(user_id=user_id).order_by(Income.date.desc(), Income.id.desc()).limit(10).all()
    recent_expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc(), Expense.id.desc()).limit(10).all()

    tx_list = []
    for inc in recent_incomes:
        tx_list.append({
            'id': inc.id,
            'type': 'income',
            'title': inc.title,
            'amount': inc.amount,
            'category_or_source': inc.source,
            'date': inc.date,
            'date_str': inc.date.strftime('%d %b %Y'),
            'notes': inc.notes
        })
    for exp in recent_expenses:
        tx_list.append({
            'id': exp.id,
            'type': 'expense',
            'title': exp.title,
            'amount': exp.amount,
            'category_or_source': exp.category,
            'payment_method': exp.payment_method,
            'date': exp.date,
            'date_str': exp.date.strftime('%d %b %Y'),
            'notes': exp.notes
        })
    
    # Sort combined transactions by date desc
    tx_list.sort(key=lambda x: (x['date'], x['id']), reverse=True)
    recent_transactions = tx_list[:8]

    # 9. Monthly Trends (Last 6 Months)
    monthly_trends = get_six_months_trend(user_id, month, year)

    return {
        'month': month,
        'year': year,
        'month_name': get_month_name(month),
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': net_savings,
        'savings_rate': savings_rate,
        'category_breakdown': category_breakdown,
        'income_sources': income_sources,
        'budget_status': budget_status,
        'total_budgeted': total_budgeted,
        'total_budget_spent': total_budget_spent,
        'over_budget_count': over_budget_count,
        'goals': goals_data,
        'recent_transactions': recent_transactions,
        'monthly_trends': monthly_trends
    }

def get_six_months_trend(user_id, current_month, current_year):
    """Calculates income vs expense for the past 6 calendar months."""
    trend = []
    m = current_month
    y = current_year

    for _ in range(6):
        inc = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
            Income.user_id == user_id,
            extract('month', Income.date) == m,
            extract('year', Income.date) == y
        ).scalar()

        exp = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
            Expense.user_id == user_id,
            extract('month', Expense.date) == m,
            extract('year', Expense.date) == y
        ).scalar()

        inc_val = round(float(inc), 2)
        exp_val = round(float(exp), 2)
        sav_val = round(inc_val - exp_val, 2)

        trend.append({
            'month': m,
            'year': y,
            'label': f"{calendar.month_abbr[m]} {str(y)[-2:]}",
            'income': inc_val,
            'expense': exp_val,
            'savings': sav_val
        })

        # Step back 1 month
        m -= 1
        if m == 0:
            m = 12
            y -= 1

    trend.reverse()
    return trend

def get_all_time_stats(user_id):
    """Returns lifetime income, expense, and transaction count."""
    total_income = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(Income.user_id == user_id).scalar()
    total_expenses = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(Expense.user_id == user_id).scalar()
    income_count = Income.query.filter_by(user_id=user_id).count()
    expense_count = Expense.query.filter_by(user_id=user_id).count()
    
    inc = round(float(total_income), 2)
    exp = round(float(total_expenses), 2)
    sav = round(inc - exp, 2)

    return {
        'total_income': inc,
        'total_expenses': exp,
        'total_savings': sav,
        'transaction_count': income_count + expense_count
    }
