import unittest
import json
from app import create_app, db

class ShoppinglistTest(unittest.TestCase):
    """This class is a test case for shoppinglist"""

    def setUp(self):
        """Initialize app and define variables"""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.register_route = '/auth/register'
        self.login_route = '/auth/login'
        self.user_route = '/user/'


        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self, username="thisuser", password="userpassword"):
        user_data = {
            'username': username,
            'password': password
        }
        return self.client().post(self.register_route, data=user_data)

    def login_user(self, username="thisuser", password="userpassword"):
        user_data = {
            'username': username,
            'password': password
        }
        return self.client().post(self.login_route, data=user_data)


    def test_user_by_id(self):
        """Test if a user can view their account details."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        result = self.client().get(
            self.user_route,
            headers=dict(Auth=access_token))
        # assert that the user is returned
        self.assertEqual(result.status_code, 200)
        self.assertIn('thisuser', str(result.data))

    def test_user_can_be_edited_or_deleted(self):
        """Test user can edit or delete account"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        result = self.client().get(
            self.user_route,
            headers=dict(Auth=access_token))
        # assert that the user is returned
        self.assertEqual(result.status_code, 200)
        self.assertIn('thisuser', str(result.data))

        # edit the user
        edit_reqst = self.client().put(self.user_route,
            headers=dict(Auth=access_token),
            data={
                "username": "ouruser"
            })

        self.assertEqual(edit_reqst.status_code, 200)

        # return account and confirm edit.
        edit_results = self.client().get(self.user_route,
            headers=dict(Auth=access_token))
        self.assertIn('ouruser', str(edit_results.data))

        # delete the user
        delete_reqst = self.client().delete(self.user_route, headers=dict(Auth=access_token))
        self.assertEqual(delete_reqst.status_code, 200)

if __name__ == "__main__":
    unittest.main()
