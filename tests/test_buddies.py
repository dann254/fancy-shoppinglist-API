import unittest
import json
from app import create_app, db

class BuddyTest(unittest.TestCase):
    """This class is a test case for buddies"""

    def setUp(self):
        """Initialize app and define variables"""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.shoppinglist = {'name': 'clothes-sl'}
        self.buddy = {'username': 'thisuser'}
        self.item = {'name':'shirt', 'price':'500', 'quantity':'5'}
        self.register_route = '/auth/register'
        self.login_route = '/auth/login'
        self.buddies_route = '/buddies/'
        self.buddies_list_route = '/buddies/shoppinglists/'
        self.shoppinglist_route = '/shoppinglists/'
        self.share_route = '/shoppinglists/share/'
        self.search_route = '/shoppinglists/'


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

    def register_user_two(self, username="thatuser", password="userpassword"):
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
    def login_user_two(self, username="thatuser", password="userpassword"):
        user_data = {
            'username': username,
            'password': password
        }
        return self.client().post(self.login_route, data=user_data)
    def create_shoppinglist(self,access_token):
        return self.client().post(self.shoppinglist_route,
            headers=dict(Auth=access_token),
            data=self.shoppinglist)

    def test_buddy_invite(self):
        """Test if a user can invite a friend """
        self.register_user()
        self.register_user_two()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        # create a shoppinglist using post
        reqst = self.client().post(self.shoppinglist_route,
            headers=dict(Auth=str(access_token)),
            data=self.shoppinglist)

        result_two = self.login_user_two()
        access_token = json.loads(result_two.data.decode())['access_token']

        # invite buddy using post
        buddy_reqst = self.client().post(self.buddies_route,
            headers=dict(Auth=str(access_token)),
            data=self.buddy)

        self.assertEqual(buddy_reqst.status_code, 201)
        self.assertIn('thisuser', str(buddy_reqst.data))

    def test_view_buddy_by_id(self):
        """Test if a user can view a buddy by id """
        self.register_user()
        self.register_user_two()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        result_two = self.login_user_two()
        access_token = json.loads(result_two.data.decode())['access_token']

        # invite buddy using post
        buddy_reqst = self.client().post(self.buddies_route,
            headers=dict(Auth=str(access_token)),
            data=self.buddy)

        self.assertEqual(buddy_reqst.status_code, 201)
        self.assertIn('thisuser', str(buddy_reqst.data))

        # get friend
        reqst = self.client().get(self.buddies_route + '1',
            headers=dict(Auth=access_token))
        self.assertEqual(reqst.status_code, 200)
        self.assertIn('thisuser', str(reqst.data))

    def test_buddy_unfriend(self):
        """Test if a user can unfriend a buddy """
        self.register_user()
        self.register_user_two()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        # create a shoppinglist using post
        reqst = self.client().post(self.shoppinglist_route,
            headers=dict(Auth=str(access_token)),
            data=self.shoppinglist)

        result_two = self.login_user_two()
        access_token = json.loads(result_two.data.decode())['access_token']

        # invite buddy using post
        buddy_reqst = self.client().post(self.buddies_route,
            headers=dict(Auth=str(access_token)),
            data=self.buddy)
        results = json.loads(buddy_reqst.data.decode())

        self.assertEqual(buddy_reqst.status_code, 201)
        self.assertIn('thisuser', str(buddy_reqst.data))

        # unfriend
        reqst = self.client().delete(self.buddies_route + '1',
            headers=dict(Auth=access_token))
        self.assertEqual(reqst.status_code, 200)

        # Test to see if friend still exists
        result = self.client().get(
            self.buddies_route + '1',
            headers=dict(Auth=access_token))
        self.assertEqual(result.status_code, 404)


    def test_view_shared_lists(self):
        """Test if a user can view shared lists of invited friends """
        self.register_user()
        self.register_user_two()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        # create a shoppinglist using post
        reqst = self.client().post(self.shoppinglist_route,
            headers=dict(Auth=str(access_token)),
            data=self.shoppinglist)
        results = json.loads(reqst.data.decode())

        req = self.client().put(self.share_route + '{}'.format(results['id']),
            headers=dict(Auth=access_token))
        self.assertEqual(req.status_code, 200)


        result_two = self.login_user_two()
        access_token = json.loads(result_two.data.decode())['access_token']

        # invite buddy using post
        buddy_reqst = self.client().post(self.buddies_route,
            headers=dict(Auth=str(access_token)),
            data=self.buddy)
        results = json.loads(buddy_reqst.data.decode())

        self.assertEqual(buddy_reqst.status_code, 201)
        self.assertIn('thisuser', str(buddy_reqst.data))

        # get all the shoppinglists shared by buddies
        reqst = self.client().get(self.buddies_list_route,
            headers=dict(Auth=access_token),
        )
        self.assertEqual(reqst.status_code, 200)
        self.assertIn('clothes-sl', str(reqst.data))

    def test_view_shared_lists_items(self):
        """Test if a user can view shared lists items of invited friends"""
        self.register_user()
        self.register_user_two()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        # create a shoppinglist using post
        reqst = self.client().post(self.shoppinglist_route,
            headers=dict(Auth=str(access_token)),
            data=self.shoppinglist)
        results = json.loads(reqst.data.decode())

        req = self.client().put(self.share_route + '{}'.format(results['id']),
            headers=dict(Auth=access_token))
        self.assertEqual(req.status_code, 200)

        # create a item using post
        item_reqst = self.client().post(self.shoppinglist_route + '{}'.format(results['id'])+'/items/',
            headers=dict(Auth=str(access_token)),
            data=self.item)
        self.assertEqual(item_reqst.status_code, 201)
        self.assertIn('shirt', str(item_reqst.data))

        result_two = self.login_user_two()
        access_token = json.loads(result_two.data.decode())['access_token']

        # invite buddy using post
        buddy_reqst = self.client().post(self.buddies_route,
            headers=dict(Auth=str(access_token)),
            data=self.buddy)

        self.assertEqual(buddy_reqst.status_code, 201)
        self.assertIn('thisuser', str(buddy_reqst.data))

        # get items the shoppinglists shared by buddies
        reqst = self.client().get(self.buddies_list_route + '{}'.format(results['id']),
            headers=dict(Auth=access_token),
        )
        self.assertEqual(reqst.status_code, 200)
        self.assertIn('shirt', str(reqst.data))

if __name__ == "__main__":
    unittest.main()
