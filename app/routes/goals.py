from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, SavingsGoal
from datetime import datetime, date

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

GOAL_CATEGORIES = [
    'Emergency Fund',
    'Electronics / Gadget',
    'Vehicle / Bike / Car',
    'Vacation / Travel',
    'Higher Education',
    'Home / Real Estate',
    'Retirement / Long Term',
    'Wedding / Family',
    'General Savings'
]

@goals_bp.route('/', methods=['GET'])
@login_required
def index():
    goals = SavingsGoal.query.filter_by(user_id=current_user.id).order_by(SavingsGoal.is_completed.asc(), SavingsGoal.deadline.asc()).all()

    total_target = sum(g.target_amount for g in goals)
    total_saved = sum(g.current_amount for g in goals)
    overall_progress = round((total_saved / total_target * 100.0), 1) if total_target > 0 else 0.0
    active_goals_count = sum(1 for g in goals if not g.is_completed and g.current_amount < g.target_amount)
    completed_goals_count = len(goals) - active_goals_count

    today = date.today().strftime('%Y-%m-%d')

    return render_template(
        'goals/index.html',
        goals=goals,
        total_target=round(total_target, 2),
        total_saved=round(total_saved, 2),
        overall_progress=overall_progress,
        active_goals_count=active_goals_count,
        completed_goals_count=completed_goals_count,
        goal_categories=GOAL_CATEGORIES,
        today=today
    )


@goals_bp.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form.get('title', '').strip()
    target_str = request.form.get('target_amount', '0').strip()
    current_str = request.form.get('current_amount', '0').strip()
    category = request.form.get('category', 'General Savings').strip()
    deadline_str = request.form.get('deadline', '').strip()
    notes = request.form.get('notes', '').strip()

    if not title or not deadline_str:
        flash('Goal title and target deadline are required.', 'danger')
        return redirect(url_for('goals.index'))

    try:
        target_amount = float(target_str)
        current_amount = float(current_str) if current_str else 0.0
        if target_amount <= 0:
            flash('Target amount must be greater than 0.', 'danger')
            return redirect(url_for('goals.index'))
    except ValueError:
        flash('Invalid target or current amount entered.', 'danger')
        return redirect(url_for('goals.index'))

    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid deadline date.', 'danger')
        return redirect(url_for('goals.index'))

    is_completed = current_amount >= target_amount

    new_goal = SavingsGoal(
        user_id=current_user.id,
        title=title,
        target_amount=target_amount,
        current_amount=current_amount,
        category=category,
        deadline=deadline,
        notes=notes,
        is_completed=is_completed
    )

    db.session.add(new_goal)
    db.session.commit()
    flash(f'Financial goal "{title}" of ₹{target_amount:,.2f} created!', 'success')
    return redirect(url_for('goals.index'))


@goals_bp.route('/contribute/<int:id>', methods=['POST'])
@login_required
def contribute(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    amount_str = request.form.get('amount', '0').strip()

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Deposit amount must be greater than 0.', 'danger')
            return redirect(url_for('goals.index'))
    except ValueError:
        flash('Invalid contribution amount.', 'danger')
        return redirect(url_for('goals.index'))

    goal.current_amount = round(goal.current_amount + amount, 2)
    if goal.current_amount >= goal.target_amount:
        goal.is_completed = True
        flash(f'🎉 Congratulations! You reached your goal for "{goal.title}" (₹{goal.target_amount:,.2f})!', 'success')
    else:
        flash(f'Added ₹{amount:,.2f} to "{goal.title}". Current progress: ₹{goal.current_amount:,.2f} / ₹{goal.target_amount:,.2f} ({goal.progress_percentage}%).', 'success')

    db.session.commit()
    return redirect(url_for('goals.index'))


@goals_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    title = request.form.get('title', '').strip()
    target_str = request.form.get('target_amount', '0').strip()
    current_str = request.form.get('current_amount', '0').strip()
    category = request.form.get('category', 'General Savings').strip()
    deadline_str = request.form.get('deadline', '').strip()
    notes = request.form.get('notes', '').strip()

    if not title or not deadline_str:
        flash('Title and deadline are required.', 'danger')
        return redirect(url_for('goals.index'))

    try:
        target_amount = float(target_str)
        current_amount = float(current_str)
        if target_amount <= 0:
            flash('Target amount must be positive.', 'danger')
            return redirect(url_for('goals.index'))
    except ValueError:
        flash('Invalid amount entered.', 'danger')
        return redirect(url_for('goals.index'))

    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid deadline date.', 'danger')
        return redirect(url_for('goals.index'))

    goal.title = title
    goal.target_amount = target_amount
    goal.current_amount = current_amount
    goal.category = category
    goal.deadline = deadline
    goal.notes = notes
    goal.is_completed = current_amount >= target_amount

    db.session.commit()
    flash(f'Goal "{goal.title}" updated successfully.', 'success')
    return redirect(url_for('goals.index'))


@goals_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    title = goal.title
    db.session.delete(goal)
    db.session.commit()
    flash(f'Savings goal "{title}" deleted.', 'info')
    return redirect(url_for('goals.index'))
