from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from app.services.analytics import get_financial_summary, get_all_time_stats, get_current_month_year

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    summary = get_financial_summary(current_user.id, month=month, year=year)
    lifetime = get_all_time_stats(current_user.id)
    
    cur_m, cur_y = get_current_month_year()
    available_years = [cur_y - 2, cur_y - 1, cur_y, cur_y + 1]

    return render_template(
        'dashboard.html',
        summary=summary,
        lifetime=lifetime,
        selected_month=summary['month'],
        selected_year=summary['year'],
        available_years=available_years
    )


@main_bp.route('/api/dashboard-charts')
@login_required
def dashboard_charts():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    summary = get_financial_summary(current_user.id, month=month, year=year)
    
    # 1. Expense by category for Doughnut chart
    cat_labels = [item['category'] for item in summary['category_breakdown']]
    cat_data = [item['total'] for item in summary['category_breakdown']]

    # 2. Income by source
    src_labels = [item['source'] for item in summary['income_sources']]
    src_data = [item['total'] for item in summary['income_sources']]

    # 3. Monthly trends (6-months bar/line chart)
    trend_labels = [t['label'] for t in summary['monthly_trends']]
    trend_income = [t['income'] for t in summary['monthly_trends']]
    trend_expenses = [t['expense'] for t in summary['monthly_trends']]
    trend_savings = [t['savings'] for t in summary['monthly_trends']]

    # 4. Budget compliance
    budget_labels = [b['category'] for b in summary['budget_status']]
    budget_allocated = [b['budget_amount'] for b in summary['budget_status']]
    budget_spent = [b['spent_amount'] for b in summary['budget_status']]

    return jsonify({
        'category_chart': {
            'labels': cat_labels,
            'data': cat_data
        },
        'source_chart': {
            'labels': src_labels,
            'data': src_data
        },
        'trend_chart': {
            'labels': trend_labels,
            'income': trend_income,
            'expenses': trend_expenses,
            'savings': trend_savings
        },
        'budget_chart': {
            'labels': budget_labels,
            'budget': budget_allocated,
            'spent': budget_spent
        }
    })
