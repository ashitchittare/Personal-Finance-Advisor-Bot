import os
from flask import Flask
from flask_login import LoginManager
from app.config import Config, DevelopmentConfig
from app.models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def format_inr(value):
    """Formats a numeric value to Indian currency format with ₹ prefix."""
    try:
        if value is None:
            return "₹0.00"
        val = float(value)
        is_negative = val < 0
        val = abs(val)
        
        # Format as string with 2 decimals
        formatted_str = f"{val:,.2f}"
        
        # Standard formatting with Rupee symbol
        prefix = "-₹" if is_negative else "₹"
        return f"{prefix}{formatted_str}"
    except (ValueError, TypeError):
        return f"₹{value}"

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register template filters
    app.jinja_env.filters['inr'] = format_inr

    @app.context_processor
    def inject_globals():
        return {
            'currency_symbol': '₹',
            'app_name': 'Personal Finance Advisor'
        }

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.income import income_bp
    from app.routes.expense import expense_bp
    from app.routes.budget import budget_bp
    from app.routes.goals import goals_bp
    from app.routes.reports import reports_bp
    from app.routes.advisor import advisor_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(advisor_bp)

    # Ensure database tables exist
    with app.app_context():
        db.create_all()

    return app
