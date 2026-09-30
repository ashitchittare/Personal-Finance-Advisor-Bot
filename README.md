# 💰 Personal Finance Advisor Bot (FinBot)

A production-ready full-stack web application for personal wealth management, intelligent cashflow tracking, category budgeting, savings goals planning, monthly statements, and AI-powered financial advising using Google Gemini API.

All currency denominations throughout the application are formatted in **₹ Indian Rupees (INR)**.

---

## 🌟 Key Features

### 1. 🔐 Authentication & Multi-User Security
- User registration, login, and secure session management via **Flask-Login**.
- Strong password hashing with **Werkzeug** security (`generate_password_hash` / `check_password_hash`).
- **Strict Data Isolation**: Every financial transaction, budget cap, savings milestone, and AI chat history is scoped to `user_id`.

### 2. 📊 Dynamic Financial Dashboard
- Live KPI cards: **Total Income**, **Total Expenses**, **Net Savings**, and **Savings Rate %**.
- Interactive **Chart.js** visualizations:
  - 6-Month Income vs Expenses vs Net Savings trend chart.
  - Monthly Category Expense Distribution (Doughnut Chart).
- Category budget compliance status with color-coded warning progress bars.
- Savings goals progress meters.
- Consolidated recent transactions feed with quick filters.

### 3. 💵 Income Management
- Add, edit, and delete income entries.
- Multi-source classification (*Salary, Freelance, Investments / Dividends, Business, Rental, Bonus, Stipend, etc.*).
- Mark recurring monthly inflows vs one-time earnings.
- Real-time search and multi-parameter filters (by source, month, year).

### 4. 💳 Expense Management
- Add, edit, and delete expense records.
- Categorization across 13 major heads (*Food & Dining, Groceries, Rent & Housing, Transport & Fuel, Utilities & Bills, Education, Shopping, Entertainment, Healthcare, Fitness, SIP Investments, etc.*).
- Tag payment modes (*UPI - GPay/PhonePe/Paytm, Credit Card, Debit Card, Net Banking, Cash*).
- Search, filter by category/month/year, and compute dynamic averages.

### 5. 🎯 Monthly Category Budget Planner
- Set monthly budget limits per expense category for any target month & year.
- Compare budgeted allocations against actual live spending.
- Visual progress bars with automated color coding:
  - 🟢 **< 80%**: On Track
  - 🟡 **80% - 100%**: Nearing Limit
  - 🔴 **> 100%**: Over-Budget Alert
- Displays remaining budget buffers and highlights unbudgeted spending.

### 6. 🏆 Financial Goals & Savings Milestones
- Create goal milestones (*Emergency Fund, Laptop Upgrade, Vacation, Vehicle, Higher Education*).
- Define target amount, current saved amount, and target deadline.
- Automated monthly deposit calculation: computes exact **₹/month** needed to achieve each goal on time.
- Direct **"Add Funds / Deposit"** modal to increment goal savings.

### 7. 📑 Monthly Financial Reports & Audits
- Deep monthly financial health statements.
- Income vs Expense breakdown tables with share percentages.
- **AI Financial Audit Generator**: Prompts Google Gemini to perform a 360-degree audit of the selected statement.
- **One-Click CSV Export**: Download all transactions for any month as a formatted CSV file.

### 8. 🤖 FinBot AI Financial Advisor (Google Gemini API)
- Real-time chat interface connected to **Google Gemini API** (`gemini-2.5-flash`).
- Dynamic prompt injection providing FinBot with the logged-in user's actual financial context (inflows, outflows, overspent categories, active goals).
- Quick suggestion chips:
  - *Analyze spending patterns*
  - *Identify budget leakages*
  - *How to save ₹10,000 more*
  - *50/30/20 budget recommendation*
  - *Savings goal feasibility check*
- Chat history persistence in SQLite per user with clear-history capability.
- Offline rule-based fallback if no API key is provided.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask 3.x
- **Database & ORM**: SQLite, SQLAlchemy, Flask-SQLAlchemy
- **Authentication**: Flask-Login, Werkzeug Security
- **Frontend**: HTML5, CSS3 (Modern Fintech Theme), JavaScript (ES6+)
- **UI Framework**: Bootstrap 5.3, Bootstrap Icons
- **Visualizations**: Chart.js 4.4
- **AI Integration**: Google Gemini API via `google-genai` SDK
- **Configuration**: `python-dotenv`

---

## 📁 Project Architecture

```
Personal-Finance-Advisor-Bot/
│
├── app/
│   ├── __init__.py           # Flask app factory, LoginManager, db init & jinja filters
│   ├── config.py             # Configuration classes (Dev, Prod, Test, API Keys)
│   ├── models.py             # SQLAlchemy Models (User, Income, Expense, Budget, SavingsGoal, etc.)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py           # Login, Register, Logout, Profile routes
│   │   ├── main.py           # Landing page, Dashboard, Chart API endpoints
│   │   ├── income.py         # Income CRUD and filters
│   │   ├── expense.py        # Expense CRUD and category tracking
│   │   ├── budget.py         # Budget Planner & compliance engine
│   │   ├── goals.py          # Savings goals & contribution math
│   │   ├── reports.py        # Statements, AI audit generation, CSV exports
│   │   └── advisor.py        # FinBot AI chat interface & API
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analytics.py      # Financial calculations & statistical aggregations
│   │   └── ai_advisor.py     # Gemini AI prompt orchestration & context injection
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html         # Fintech shell with sidebar, navbar, toasts
│   │   ├── landing.html      # Landing showcase
│   │   ├── dashboard.html    # KPI cards, trend charts, transactions
│   │   ├── auth/             # Login, Register, Profile
│   │   ├── income/           # Income tracker
│   │   ├── expense/          # Expense tracker
│   │   ├── budget/           # Budget planner
│   │   ├── goals/            # Savings milestones
│   │   ├── reports/          # Monthly statements
│   │   └── advisor/          # AI FinBot chat interface
│   └── static/
│       ├── css/style.css     # Fintech UI styling (Indigo/Emerald theme)
│       └── js/
│           ├── main.js       # UI interactions & modal pre-fills
│           ├── charts.js     # Chart.js configs & rendering
│           └── advisor.js    # AI chat client & markdown parser
│
├── instance/                 # SQLite database folder (auto-generated)
├── tests/                    # Automated test suite
│   ├── test_auth.py          # Auth & session security tests
│   ├── test_finance.py       # CRUD & budget calculation tests
│   └── test_advisor.py       # AI advisor & context grounding tests
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── seed_data.py              # Demo dataset seeder
├── run.py                    # Application entry point
└── README.md                 # Documentation
```

---

## 🚀 Quick Setup & Installation

### Step 1: Clone or Navigate to the Project Directory
```bash
cd Personal-Finance-Advisor-Bot
```

### Step 2: (Optional) Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env   # On Windows PowerShell: Copy-Item .env.example .env
```

Open `.env` and configure your settings:
```env
SECRET_KEY=your-secure-random-secret-key
DATABASE_URL=sqlite:///personal_finance.db

# (Optional) Add your Google Gemini API Key for live AI responses
# Obtain free from: https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
> *Note: If no Gemini API key is provided, FinBot automatically runs in intelligent local rule-based mode using your real financial data.*

---

## 🗄️ Database Initialization & Demo Data

Run the seeding script to initialize SQLite tables and populate realistic sample incomes, expenses, budgets, and savings goals:

```bash
python seed_data.py
```

### 🔑 Demo Accounts Available:
| Role | Username | Email | Password | Details |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Demo** | `aarav` | `aarav@financebot.ai` | `password123` | Loaded with ₹1.16L income, expenses, over-budget warnings & goals |
| **Secondary (Isolation)** | `priya` | `priya@financebot.ai` | `password123` | Demonstrates multi-user database isolation |

---

## 🏃 Running the Application

Start the Flask development server:
```bash
python run.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running the Test Suite

Execute the automated test suite to verify authentication, CRUD operations, budget calculations, and AI responses:
```bash
python -m unittest discover tests
```

---

## 🔒 Security & Best Practices

1. **Password Security**: Passwords are never stored in plain text; salted hashes are generated via `werkzeug.security`.
2. **User Isolation**: All queries enforce `user_id == current_user.id`.
3. **Safe API Key Handling**: Secrets are loaded from `.env` and excluded from git via `.gitignore`.
4. **Input Sanitization**: All numerical and date inputs are validated before database commits.
