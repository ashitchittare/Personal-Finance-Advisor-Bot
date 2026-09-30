from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        occupation = request.form.get('occupation', '').strip()

        if not username or not email or not password:
            flash('Username, email, and password are required.', 'danger')
            return render_template('auth/register.html', full_name=full_name, username=username, email=email, occupation=occupation)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html', full_name=full_name, username=username, email=email, occupation=occupation)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', full_name=full_name, username=username, email=email, occupation=occupation)

        if User.query.filter_by(username=username).first():
            flash('Username is already registered. Please pick another one.', 'danger')
            return render_template('auth/register.html', full_name=full_name, username=username, email=email, occupation=occupation)

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'danger')
            return render_template('auth/register.html', full_name=full_name, username=username, email=email, occupation=occupation)

        new_user = User(
            username=username,
            email=email,
            full_name=full_name or username,
            occupation=occupation or 'Professional',
            currency='INR'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Account created successfully! Welcome to Personal Finance Advisor Bot.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        login_identifier = request.form.get('login_identifier', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not login_identifier or not password:
            flash('Please provide both username/email and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter(
            (User.username == login_identifier) | (User.email == login_identifier.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        occupation = request.form.get('occupation', '').strip()
        new_password = request.form.get('new_password', '').strip()

        if full_name:
            current_user.full_name = full_name
        if occupation:
            current_user.occupation = occupation
        if new_password:
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
                return render_template('auth/profile.html')
            current_user.set_password(new_password)
            flash('Password updated successfully!', 'success')

        db.session.commit()
        flash('Profile details updated.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')
