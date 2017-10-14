import unittest
import json
from app import create_app, db
from app.email_handler import generate_token

class AuthTest(unittest.TestCase):
    """Test authentication: login and register"""

    def setUp(self):
        """set up of test variables"""
        #create app with testing config
        self.app = create_app(config_name="testing")
        #test client
        self.client = self.app.test_client
        # user test json with predifined variables
        self.user_data = {
            'username': 'thisuser',
            'password': 'mypassword',
            'email': 'email@mail.com'
        }

        #initialize endpoints
        self.register_route = '/auth/register'
        self.login_route = '/auth/login'
        self.confirm_route = '/verify/'

        with self.app.app_context():
            #create database tables
            db.session.close()
            db.drop_all()
            db.create_all()
            self.confirm_token=generate_token('email@mail.com')

    def test_registration(self):
        """Test if user registration works correctly and user is saved to db"""
        reqst = self.client().post(self.register_route, data=self.user_data)
        #check that the message result contains a 201 status code
        self.assertEqual(reqst.status_code, 201)

    def test_existing_user(self):
        """test user cannot register multiple times"""
        reqst = self.client().post(self.register_route, data=self.user_data)
        self.assertEqual(reqst.status_code, 201)
        second_reqst = self.client().post(self.register_route, data=self.user_data)
        self.assertEqual(second_reqst.status_code, 409)

    def test_user_login(self):
        """Test if the registered user can login"""
        reqst = self.client().post(self.register_route, data=self.user_data)
        self.assertEqual(reqst.status_code, 201)
        vr = self.client().get(self.confirm_route + '{}'.format(self.confirm_token))
        rst = json.loads(vr.data.decode())
        self.assertEqual(vr['message'], 'email@mail.com')
        login_reqst = self.client().post(self.login_route, data=self.user_data)
        #get jsonified result and test if it  returns 200 status
        result = json.loads(login_reqst.data.decode())
        self.assertEqual(login_reqst.status_code, 200)
        #check if it has an access token
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """Test that users that failed to authenticate and non registered users cannot login"""
        #create a dict to define an unregistered user
        non_user = {
            'username': 'non_user',
            'password': 'youdontbelong'
        }
        #try to login with the non_user
        reqst = self.client().post(self.login_route, data=non_user)
        # get jsonified result and check if it contains code 401-anauthorized
        result = json.loads(reqst.data.decode())
        self.assertEqual(reqst.status_code, 401)
