import unittest
from datetime import date, timedelta
from app import create_app
from app.config import TestingConfig
from app.models import db, User, Income, Expense, Budget, SavingsGoal
from app.services.analytics import get_financial_summary

class FinanceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create two test users to verify strict data isolation
        self.user1 = User(username='user1', email='user1@test.com')
        self.user1.set_password('pass123')
        self.user2 = User(username='user2', email='user2@test.com')
        self.user2.set_password('pass123')
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_user1(self):
        self.client.get('/logout')
        return self.client.post('/login', data={'login_identifier': 'user1', 'password': 'pass123'}, follow_redirects=True)

    def login_user2(self):
        self.client.get('/logout')
        return self.client.post('/login', data={'login_identifier': 'user2', 'password': 'pass123'}, follow_redirects=True)

    def test_income_crud_and_isolation(self):
        self.login_user1()
        
        # 1. Add Income for User 1
        res = self.client.post('/income/add', data={
            'title': 'Tech Consulting',
            'amount': '50000',
            'source': 'Freelance',
            'date': str(date.today()),
            'notes': 'Website project',
            'is_recurring': 'y'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        inc = Income.query.filter_by(user_id=self.user1.id).first()
        self.assertIsNotNone(inc)
        self.assertEqual(inc.amount, 50000.0)

        # 2. Verify User 2 cannot see User 1's income
        self.login_user2()
        res_u2 = self.client.get('/income/')
        self.assertNotIn(b'Tech Consulting', res_u2.data)

        # 3. Edit Income by User 1
        self.login_user1()
        res_edit = self.client.post(f'/income/edit/{inc.id}', data={
            'title': 'Tech Consulting Updated',
            'amount': '55000',
            'source': 'Freelance',
            'date': str(date.today()),
            'notes': 'Updated notes'
        }, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)
        db.session.refresh(inc)
        self.assertEqual(inc.amount, 55000.0)
        self.assertEqual(inc.title, 'Tech Consulting Updated')

        # 4. Delete Income
        res_del = self.client.post(f'/income/delete/{inc.id}', follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(Income.query.filter_by(id=inc.id).first(), None)

    def test_expense_crud_and_budget_calculation(self):
        self.login_user1()

        today = date.today()
        # Set Budget of 5000 for Food & Dining
        self.client.post('/budgets/set', data={
            'category': 'Food & Dining',
            'amount': '5000',
            'month': today.month,
            'year': today.year
        }, follow_redirects=True)

        # Add Expense of 6000 (Over budget by 1000)
        self.client.post('/expenses/add', data={
            'title': 'Family Dinner',
            'amount': '6000',
            'category': 'Food & Dining',
            'payment_method': 'UPI (GooglePay/PhonePe/Paytm)',
            'date': str(today)
        }, follow_redirects=True)

        summary = get_financial_summary(self.user1.id, month=today.month, year=today.year)
        self.assertEqual(summary['total_expenses'], 6000.0)
        self.assertEqual(summary['over_budget_count'], 1)
        self.assertTrue(summary['budget_status'][0]['is_over_budget'])
        self.assertEqual(summary['budget_status'][0]['spent_amount'], 6000.0)

    def test_savings_goals_and_monthly_required_calc(self):
        self.login_user1()
        
        deadline = date.today() + timedelta(days=90) # ~3 months
        self.client.post('/goals/add', data={
            'title': 'New Laptop',
            'target_amount': '60000',
            'current_amount': '15000',
            'category': 'Electronics / Gadget',
            'deadline': str(deadline)
        }, follow_redirects=True)

        goal = SavingsGoal.query.filter_by(user_id=self.user1.id).first()
        self.assertIsNotNone(goal)
        self.assertEqual(goal.progress_percentage, 25.0)
        self.assertEqual(goal.remaining_amount, 45000.0)
        self.assertGreater(goal.required_monthly_savings, 0)

        # Contribute funds
        self.client.post(f'/goals/contribute/{goal.id}', data={
            'amount': '45000'
        }, follow_redirects=True)
        db.session.refresh(goal)
        self.assertEqual(goal.current_amount, 60000.0)
        self.assertEqual(goal.progress_percentage, 100.0)
        self.assertTrue(goal.is_completed)

if __name__ == '__main__':
    unittest.main()
