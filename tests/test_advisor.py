import unittest
from datetime import date
from app import create_app
from app.config import TestingConfig
from app.models import db, User, Income, Expense, AIChatMessage
from app.services.ai_advisor import generate_ai_response

class AdvisorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(username='finuser', email='finuser@test.com', full_name='Fin User')
        self.user.set_password('pass123')
        db.session.add(self.user)
        db.session.commit()

        # Add sample data
        today = date.today()
        inc = Income(user_id=self.user.id, title='Salary', amount=60000.0, source='Salary', date=today)
        exp = Expense(user_id=self.user.id, title='Groceries', amount=10000.0, category='Groceries', date=today)
        db.session.add_all([inc, exp])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_ai_response_fallback_and_grounding(self):
        # Fallback analysis without live API key
        response_text = generate_ai_response(self.user, "Analyze my monthly spending")
        self.assertIn('₹', response_text)
        self.assertIn('FinBot', response_text)
        self.assertIn('Fin User', response_text)

    def test_chat_api_endpoint(self):
        self.client.post('/login', data={'login_identifier': 'finuser', 'password': 'pass123'}, follow_redirects=True)
        
        res = self.client.post('/advisor/chat', json={
            'message': 'How can I save more money?'
        })
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertEqual(json_data['status'], 'success')
        self.assertIn('assistant_message', json_data)
        self.assertIn('₹', json_data['assistant_message']['message'])

        # Verify chat history is stored
        messages = AIChatMessage.query.filter_by(user_id=self.user.id).all()
        self.assertEqual(len(messages), 2) # 1 user + 1 assistant

if __name__ == '__main__':
    unittest.main()
