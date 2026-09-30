import unittest
from app import create_app
from app.config import TestingConfig
from app.models import db, User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration(self):
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'password': 'password123',
            'confirm_password': 'password123',
            'occupation': 'Analyst'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.check_password('wrongpassword'))

    def test_duplicate_registration_fails(self):
        user = User(username='existing', email='exist@example.com')
        user.set_password('pass123')
        db.session.add(user)
        db.session.commit()

        # Try registering same username
        response = self.client.post('/register', data={
            'username': 'existing',
            'email': 'different@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Username is already registered', response.data)

    def test_user_login_and_logout(self):
        user = User(username='loginuser', email='login@example.com')
        user.set_password('securepass')
        db.session.add(user)
        db.session.commit()

        # Correct login
        res = self.client.post('/login', data={
            'login_identifier': 'loginuser',
            'password': 'securepass'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Financial Dashboard', res.data)

        # Logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)
        self.assertIn(b'You have been logged out', res_logout.data)

    def test_unauthenticated_access_redirects(self):
        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

if __name__ == '__main__':
    unittest.main()
