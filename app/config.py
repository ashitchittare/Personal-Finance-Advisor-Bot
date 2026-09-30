import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-secret-key-change-in-production')
    
    # SQLite Database configuration
    db_url = os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR / 'instance' / 'personal_finance.db'}")
    if db_url.startswith('sqlite:///') and not os.path.isabs(db_url.replace('sqlite:///', '')):
        # Ensure instance directory exists
        (BASE_DIR / 'instance').mkdir(exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'instance' / 'personal_finance.db'}"
    else:
        SQLALCHEMY_DATABASE_URI = db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google Gemini API configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    
    # Currency symbol
    CURRENCY_SYMBOL = '₹'
    CURRENCY_CODE = 'INR'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
