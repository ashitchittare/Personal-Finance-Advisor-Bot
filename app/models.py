from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    currency = db.Column(db.String(10), default='INR')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    incomes = db.relationship('Income', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    savings_goals = db.relationship('SavingsGoal', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('FinancialReport', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    chat_messages = db.relationship('AIChatMessage', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name or self.username,
            'occupation': self.occupation or 'Individual',
            'currency': self.currency,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Income(db.Model):
    __tablename__ = 'incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(64), nullable=False)  # Salary, Freelancing, Investments, Business, Rental, Bonus, Other
    date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    is_recurring = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'amount': self.amount,
            'source': self.source,
            'date': self.date.strftime('%Y-%m-%d'),
            'notes': self.notes or '',
            'is_recurring': self.is_recurring,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

    def __repr__(self):
        return f'<Income {self.title}: ₹{self.amount}>'


class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False)  # Food & Dining, Transport, Rent & Housing, Utilities, Education, Shopping, Entertainment, Healthcare, Personal Care, Travel, Investments, Miscellaneous
    payment_method = db.Column(db.String(64), default='UPI')  # UPI, Credit Card, Debit Card, Cash, Net Banking
    date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'amount': self.amount,
            'category': self.category,
            'payment_method': self.payment_method,
            'date': self.date.strftime('%Y-%m-%d'),
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

    def __repr__(self):
        return f'<Expense {self.title}: ₹{self.amount}>'


class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Budget limit for the month
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'category', 'month', 'year', name='uq_user_category_month_year'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'amount': self.amount,
            'month': self.month,
            'year': self.year,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

    def __repr__(self):
        return f'<Budget {self.category} ({self.month}/{self.year}): ₹{self.amount}>'


class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(64), default='General')  # Emergency Fund, Gadget, Vehicle, Education, Travel, House, Investment
    notes = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def progress_percentage(self):
        if self.target_amount <= 0:
            return 100.0
        pct = (self.current_amount / self.target_amount) * 100.0
        return min(round(pct, 1), 100.0)

    @property
    def remaining_amount(self):
        return max(0.0, round(self.target_amount - self.current_amount, 2))

    @property
    def days_remaining(self):
        delta = (self.deadline - date.today()).days
        return max(0, delta)

    @property
    def required_monthly_savings(self):
        """Calculates needed monthly contribution based on remaining months until deadline."""
        rem = self.remaining_amount
        if rem <= 0:
            return 0.0
        
        today = date.today()
        # Calculate months difference
        months = (self.deadline.year - today.year) * 12 + (self.deadline.month - today.month)
        if self.deadline.day > today.day:
            months += 1
        months = max(1, months)
        
        return round(rem / months, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'deadline': self.deadline.strftime('%Y-%m-%d'),
            'category': self.category,
            'notes': self.notes or '',
            'is_completed': self.is_completed or (self.current_amount >= self.target_amount),
            'progress_percentage': self.progress_percentage,
            'remaining_amount': self.remaining_amount,
            'days_remaining': self.days_remaining,
            'required_monthly_savings': self.required_monthly_savings,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

    def __repr__(self):
        return f'<SavingsGoal {self.title}: ₹{self.current_amount}/₹{self.target_amount}>'


class FinancialReport(db.Model):
    __tablename__ = 'financial_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_income = db.Column(db.Float, default=0.0)
    total_expenses = db.Column(db.Float, default=0.0)
    net_savings = db.Column(db.Float, default=0.0)
    savings_rate = db.Column(db.Float, default=0.0)
    summary_data = db.Column(db.Text, nullable=True)  # JSON string
    ai_analysis = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'month', 'year', name='uq_user_report_month_year'),
    )

    def get_summary_json(self):
        if self.summary_data:
            try:
                return json.loads(self.summary_data)
            except Exception:
                return {}
        return {}

    def set_summary_json(self, data):
        self.summary_data = json.dumps(data)

    def to_dict(self):
        return {
            'id': self.id,
            'month': self.month,
            'year': self.year,
            'total_income': self.total_income,
            'total_expenses': self.total_expenses,
            'net_savings': self.net_savings,
            'savings_rate': self.savings_rate,
            'summary_data': self.get_summary_json(),
            'ai_analysis': self.ai_analysis or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

    def __repr__(self):
        return f'<FinancialReport ({self.month}/{self.year}) User: {self.user_id}>'


class AIChatMessage(db.Model):
    __tablename__ = 'ai_chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'message': self.message,
            'created_at': self.created_at.strftime('%I:%M %p, %d %b %Y')
        }

    def __repr__(self):
        return f'<AIChatMessage {self.role}: {self.message[:30]}...>'
