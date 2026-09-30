from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, jsonify
from flask_login import login_required, current_user
from app.models import db, FinancialReport, Income, Expense
from app.services.analytics import get_financial_summary, get_current_month_year, get_month_name
from app.services.ai_advisor import generate_comprehensive_audit
from datetime import date
from sqlalchemy import extract
import csv
import io

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/', methods=['GET'])
@login_required
def index():
    cur_m, cur_y = get_current_month_year()
    month = request.args.get('month', type=int) or cur_m
    year = request.args.get('year', type=int) or cur_y

    summary = get_financial_summary(current_user.id, month=month, year=year)

    # Check if a saved report exists in the database
    saved_report = FinancialReport.query.filter_by(
        user_id=current_user.id,
        month=month,
        year=year
    ).first()

    available_years = [cur_y - 2, cur_y - 1, cur_y, cur_y + 1]

    return render_template(
        'reports/index.html',
        summary=summary,
        saved_report=saved_report,
        selected_month=month,
        selected_year=year,
        month_name=get_month_name(month),
        available_years=available_years
    )


@reports_bp.route('/generate-ai-audit', methods=['POST'])
@login_required
def generate_audit():
    month = request.form.get('month', type=int)
    year = request.form.get('year', type=int)
    
    summary = get_financial_summary(current_user.id, month=month, year=year)
    ai_text = generate_comprehensive_audit(current_user)

    # Save or update report in DB
    report = FinancialReport.query.filter_by(
        user_id=current_user.id,
        month=month,
        year=year
    ).first()

    if not report:
        report = FinancialReport(
            user_id=current_user.id,
            month=month,
            year=year,
            total_income=summary['total_income'],
            total_expenses=summary['total_expenses'],
            net_savings=summary['net_savings'],
            savings_rate=summary['savings_rate'],
            ai_analysis=ai_text
        )
        report.set_summary_json({
            'category_breakdown': summary['category_breakdown'],
            'budget_status': summary['budget_status'],
            'income_sources': summary['income_sources']
        })
        db.session.add(report)
    else:
        report.total_income = summary['total_income']
        report.total_expenses = summary['total_expenses']
        report.net_savings = summary['net_savings']
        report.savings_rate = summary['savings_rate']
        report.ai_analysis = ai_text
        report.set_summary_json({
            'category_breakdown': summary['category_breakdown'],
            'budget_status': summary['budget_status'],
            'income_sources': summary['income_sources']
        })

    db.session.commit()
    flash('AI Financial Audit generated and saved for this report!', 'success')
    return redirect(url_for('reports.index', month=month, year=year))


@reports_bp.route('/export-csv', methods=['GET'])
@login_required
def export_csv():
    cur_m, cur_y = get_current_month_year()
    month = request.args.get('month', type=int) or cur_m
    year = request.args.get('year', type=int) or cur_y

    incomes = Income.query.filter(
        Income.user_id == current_user.id,
        extract('month', Income.date) == month,
        extract('year', Income.date) == year
    ).order_by(Income.date.asc()).all()

    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).order_by(Expense.date.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write Header
    writer.writerow(['Date', 'Type', 'Title / Description', 'Category / Source', 'Payment Method', 'Amount (INR)', 'Notes'])

    for inc in incomes:
        writer.writerow([
            inc.date.strftime('%Y-%m-%d'),
            'Income',
            inc.title,
            inc.source,
            'N/A',
            f"{inc.amount:.2f}",
            inc.notes or ''
        ])

    for exp in expenses:
        writer.writerow([
            exp.date.strftime('%Y-%m-%d'),
            'Expense',
            exp.title,
            exp.category,
            exp.payment_method,
            f"-{exp.amount:.2f}",
            exp.notes or ''
        ])

    csv_data = output.getvalue()
    filename = f"financial_report_{year}_{month:02d}_{current_user.username}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )
