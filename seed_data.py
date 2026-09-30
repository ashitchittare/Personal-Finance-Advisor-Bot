import os
from datetime import date, timedelta
from app import create_app
from app.models import db, User, Income, Expense, Budget, SavingsGoal, FinancialReport, AIChatMessage
from app.services.analytics import get_current_month_year

def seed_database():
    app = create_app()
    with app.app_context():
        print("[*] Seeding database...")
        # Clear existing tables
        db.drop_all()
        db.create_all()

        cur_m, cur_y = get_current_month_year()
        today = date.today()

        # 1. Create Demo User 1: Aarav Sharma
        aarav = User(
            username='aarav',
            email='aarav@financebot.ai',
            full_name='Aarav Sharma',
            occupation='Software Engineer',
            currency='INR'
        )
        aarav.set_password('password123')
        db.session.add(aarav)

        # 2. Create Demo User 2: Priya Patel (Demonstrates multi-user isolation)
        priya = User(
            username='priya',
            email='priya@financebot.ai',
            full_name='Priya Patel',
            occupation='Product Designer',
            currency='INR'
        )
        priya.set_password('password123')
        db.session.add(priya)

        db.session.commit()

        # ==========================================
        # SEED DATA FOR AARAV SHARMA (Primary Demo)
        # ==========================================

        # --- Incomes for Current Month & Past 2 Months ---
        incomes_data = [
            # Current Month
            (aarav.id, "Tech Corp Monthly Salary", 85000.0, "Salary", today.replace(day=1), "Primary software engineering salary", True),
            (aarav.id, "Freelance Web Development Project", 22500.0, "Freelance", today.replace(day=10), "Full-stack client portal dashboard", False),
            (aarav.id, "Mutual Fund Dividend", 3800.0, "Investments / Dividends", today.replace(day=15), "Nifty 50 Index Fund quarterly payout", False),
            (aarav.id, "Tech Mentorship Honorarium", 5000.0, "Bonus / Incentive", today.replace(day=18), "Weekend code review session", False),

            # Past Month (Month - 1)
            (aarav.id, "Tech Corp Monthly Salary", 85000.0, "Salary", (today.replace(day=1) - timedelta(days=20)).replace(day=1), "Monthly salary", True),
            (aarav.id, "Mobile App UI Consulting", 18000.0, "Freelance", (today.replace(day=1) - timedelta(days=20)).replace(day=12), "Consulting project", False),

            # 2 Months Ago (Month - 2)
            (aarav.id, "Tech Corp Monthly Salary", 85000.0, "Salary", (today.replace(day=1) - timedelta(days=55)).replace(day=1), "Monthly salary", True),
            (aarav.id, "Annual Performance Bonus", 35000.0, "Bonus / Incentive", (today.replace(day=1) - timedelta(days=55)).replace(day=15), "Q4 appraisal bonus", False),
        ]

        for uid, title, amount, source, dt, notes, recurring in incomes_data:
            inc = Income(
                user_id=uid,
                title=title,
                amount=amount,
                source=source,
                date=dt,
                notes=notes,
                is_recurring=recurring
            )
            db.session.add(inc)

        # --- Expenses for Current Month ---
        expenses_data = [
            (aarav.id, "Apartment Rent & Maintenance", 22000.0, "Rent & Housing", "Net Banking", today.replace(day=2), "2BHK Indiranagar, Bangalore"),
            (aarav.id, "Monthly Grocery Shopping", 6850.0, "Groceries", "UPI (GooglePay/PhonePe/Paytm)", today.replace(day=3), "BigBasket & Local Supermarket"),
            (aarav.id, "Weekend Dining & Swiggy/Zomato", 5400.0, "Food & Dining", "UPI (GooglePay/PhonePe/Paytm)", today.replace(day=5), "Dinner with colleagues + food delivery"),
            (aarav.id, "Electricity & High-Speed WiFi Bills", 3200.0, "Utilities & Bills", "UPI (GooglePay/PhonePe/Paytm)", today.replace(day=6), "BESCOM power bill & ACT Fibernet"),
            (aarav.id, "Metro Card Recharge & Petrol", 3800.0, "Transport & Fuel", "Credit Card", today.replace(day=8), "Namma Metro card + Two-wheeler fuel"),
            (aarav.id, "Mechanical Keyboard & Desk Mat", 4500.0, "Shopping & Electronics", "Credit Card", today.replace(day=11), "Keychron mechanical keyboard on Amazon"),
            (aarav.id, "Netflix, Spotify & Prime Subscriptions", 1199.0, "Entertainment & OTT", "Credit Card", today.replace(day=12), "Monthly digital subscriptions"),
            (aarav.id, "Cult.fit Gym Membership", 2000.0, "Personal Care & Fitness", "UPI (GooglePay/PhonePe/Paytm)", today.replace(day=14), "Monthly fitness pack"),
            (aarav.id, "Dental Checkup & Medicines", 1500.0, "Healthcare & Medical", "Debit Card", today.replace(day=16), "Routine scaling and vitamin supplements"),
            (aarav.id, "Mutual Fund Systematic Investment (SIP)", 15000.0, "Investments & SIP", "Net Banking", today.replace(day=10), "Parag Parikh Flexi Cap & UTI Nifty 50"),
            (aarav.id, "System Design & AI Course", 2999.0, "Education & Books", "Credit Card", today.replace(day=17), "System design interview masterclass"),

            # Past Month Expenses
            (aarav.id, "Apartment Rent", 22000.0, "Rent & Housing", "Net Banking", (today.replace(day=1) - timedelta(days=20)).replace(day=2), "Rent payment"),
            (aarav.id, "Groceries & Vegetables", 6400.0, "Groceries", "UPI (GooglePay/PhonePe/Paytm)", (today.replace(day=1) - timedelta(days=20)).replace(day=4), "Supermarket"),
            (aarav.id, "Dining & Cafes", 4800.0, "Food & Dining", "UPI (GooglePay/PhonePe/Paytm)", (today.replace(day=1) - timedelta(days=20)).replace(day=8), "Social dinners"),
            (aarav.id, "Mutual Fund SIP", 15000.0, "Investments & SIP", "Net Banking", (today.replace(day=1) - timedelta(days=20)).replace(day=10), "Monthly SIP"),
            (aarav.id, "Weekend Trip Fuel & Tolls", 4200.0, "Transport & Fuel", "Credit Card", (today.replace(day=1) - timedelta(days=20)).replace(day=14), "Nandi hills drive"),
        ]

        for uid, title, amount, category, pmethod, dt, notes in expenses_data:
            exp = Expense(
                user_id=uid,
                title=title,
                amount=amount,
                category=category,
                payment_method=pmethod,
                date=dt,
                notes=notes
            )
            db.session.add(exp)

        # --- Category Budgets for Current Month ---
        budgets_data = [
            (aarav.id, "Food & Dining", 5000.0, cur_m, cur_y),          # Actual: 5400 (Over budget warning!)
            (aarav.id, "Rent & Housing", 22000.0, cur_m, cur_y),        # Actual: 22000 (100%)
            (aarav.id, "Groceries", 7000.0, cur_m, cur_y),             # Actual: 6850 (97.9%)
            (aarav.id, "Transport & Fuel", 4500.0, cur_m, cur_y),       # Actual: 3800 (84.4%)
            (aarav.id, "Shopping & Electronics", 6000.0, cur_m, cur_y), # Actual: 4500 (75%)
            (aarav.id, "Entertainment & OTT", 2000.0, cur_m, cur_y),    # Actual: 1199 (60%)
            (aarav.id, "Utilities & Bills", 3500.0, cur_m, cur_y),      # Actual: 3200 (91.4%)
            (aarav.id, "Healthcare & Medical", 3000.0, cur_m, cur_y),   # Actual: 1500 (50%)
        ]

        for uid, cat, amount, m, y in budgets_data:
            b = Budget(
                user_id=uid,
                category=cat,
                amount=amount,
                month=m,
                year=y
            )
            db.session.add(b)

        # --- Savings Goals ---
        goals_data = [
            (aarav.id, "Emergency Fund (6 Months Living)", 250000.0, 175000.0, today + timedelta(days=180), "Emergency Fund", "Safety cushion in high-interest liquid fund", False),
            (aarav.id, "Apple MacBook Pro M3 Upgrade", 140000.0, 95000.0, today + timedelta(days=90), "Electronics / Gadget", "Work laptop upgrade", False),
            (aarav.id, "Goa Year-End Beach Vacation", 35000.0, 28000.0, today + timedelta(days=60), "Vacation / Travel", "Flight tickets + Resort booking", False),
            (aarav.id, "AWS Cloud Architect Certification", 25000.0, 25000.0, today - timedelta(days=10), "Higher Education", "Certification completed & exam passed!", True),
        ]

        for uid, title, target, curr, dline, cat, notes, completed in goals_data:
            g = SavingsGoal(
                user_id=uid,
                title=title,
                target_amount=target,
                current_amount=curr,
                deadline=dline,
                category=cat,
                notes=notes,
                is_completed=completed
            )
            db.session.add(g)

        # --- Sample AI Chat History ---
        chat_data = [
            (aarav.id, "user", "Hi FinBot! Can you give me a quick summary of where my money went this month?"),
            (aarav.id, "assistant", "Hello Aarav! 📊 Here is your financial snapshot for this month:\n\n- **Total Inflow:** ₹1,16,300.00\n- **Total Expenses:** ₹68,449.00\n- **Net Savings:** ₹47,851.00 (**41.1%** savings rate 🌟)\n\n⚠️ **Budget Alert:** You've spent **₹5,400.00** on *Food & Dining*, exceeding your ₹5,000.00 budget by **₹400.00**.\n\n🎯 **Goal Update:** You are at **70%** for your *Emergency Fund* and **67.9%** for your *MacBook Pro* goal. Keep it up!"),
            (aarav.id, "user", "How can I optimize my food spending for the rest of the month?"),
            (aarav.id, "assistant", "Great question! Since you have already hit your ₹5,000 dining cap:\n\n1. **Meal Prep at Home:** Prepare 4-5 dinners during weekdays to avoid frequent Zomato/Swiggy orders.\n2. **Cap Social Dining:** Limit weekend restaurant visits to ₹1,000 total for the remainder of this cycle.\n3. **Use Cashback Cards/UPI Offers:** For grocery essentials, take advantage of cashback on UPI or credit cards.")
        ]

        for uid, role, msg in chat_data:
            chat = AIChatMessage(
                user_id=uid,
                role=role,
                message=msg
            )
            db.session.add(chat)

        # ==========================================
        # SEED DATA FOR PRIYA PATEL (Isolation test)
        # ==========================================
        inc_priya = Income(
            user_id=priya.id,
            title="Design Studio Salary",
            amount=70000.0,
            source="Salary",
            date=today.replace(day=1),
            notes="Product designer salary",
            is_recurring=True
        )
        exp_priya = Expense(
            user_id=priya.id,
            title="Art Supplies & Tablet Pen",
            amount=6500.0,
            category="Shopping & Electronics",
            payment_method="UPI (GooglePay/PhonePe/Paytm)",
            date=today.replace(day=5),
            notes="Digital illustration pen"
        )
        goal_priya = SavingsGoal(
            user_id=priya.id,
            title="Wacom Cintiq Pro Display",
            target_amount=120000.0,
            current_amount=45000.0,
            deadline=today + timedelta(days=120),
            category="Electronics / Gadget",
            notes="Display monitor for UI design"
        )
        db.session.add_all([inc_priya, exp_priya, goal_priya])

        db.session.commit()
        print("[+] Database seeded successfully!")
        print("\nDemo User Credentials:")
        print("---------------------------------------------")
        print("1. Primary User:")
        print("   Username: aarav")
        print("   Email:    aarav@financebot.ai")
        print("   Password: password123")
        print("---------------------------------------------")
        print("2. Secondary User (Data Isolation Testing):")
        print("   Username: priya")
        print("   Email:    priya@financebot.ai")
        print("   Password: password123")
        print("---------------------------------------------")

if __name__ == '__main__':
    seed_database()
