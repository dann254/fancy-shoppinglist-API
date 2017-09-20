import unittest
import json
from app import create_app, db
import urllib

class ShoppinglistTest(unittest.TestCase):
    """This class is a test case for shoppinglist"""

    def setUp(self):
        """Initialize app and define variables"""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.shoppinglist = {'name': 'clothes sl'}
        self.item = {'name':'shirt', 'price':'500', 'quantity':'5'}
        self.register_route = '/auth/register'
        self.login_route = '/auth/login'
        self.shoppinglist_route = '/shoppinglists/'
        self.share_route = '/shoppinglists/share/'
        self.search_route = '/shoppinglists/search'


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
    def create_shoppinglist(self,access_token):
        return self.client().post(self.shoppinglist_route,
            headers=dict(Auth="Bearer " + access_token),
            data=self.shoppinglist)

    def test_shoppinglist_creation(self):
        """Test if the API can create a shoppinglist (POST)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        # create a shoppinglist using post
        reqst = self.client().post(self.shoppinglist_route,
            headers=dict(Auth="Bearer " + str(access_token)),
            data=self.shoppinglist)
        self.assertEqual(reqst.status_code, 201)
        self.assertIn('clothes sl', str(reqst.data))

    def test_get_all_shoppinglists(self):
        """Test GET request for shoppinglists."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        reqst = self.client().post(self.shoppinglist_route,
            headers=dict(Auth="Bearer " + access_token),
            data=self.shoppinglist)
        self.assertEqual(reqst.status_code, 201)

        # get all the shoppinglists that belong to the test user
        reqst = self.client().get(self.shoppinglist_route,
            headers=dict(Auth="Bearer " + access_token),
        )
        self.assertEqual(reqst.status_code, 200)
        self.assertIn('clothes sl', str(reqst.data))

    def test_get_shoppinglist_by_id(self):
        """Test get a single shoppinglist by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        reqst = self.client().post(
            self.shoppinglist_route,
            headers=dict(Auth="Bearer " + access_token),
            data=self.shoppinglist)

        # check if the shoppinglist is created then get the result in json
        self.assertEqual(reqst.status_code, 201)
        results = json.loads(reqst.data.decode())

        result = self.client().get(
            self.shoppinglist_route + '{}'.format(results['id']),
            headers=dict(Auth="Bearer " + access_token))
        # assert that the shoppinglist is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('clothes sl', str(result.data))

    def test_shoppinglist_can_be_edited(self):
        """Test edit an existing shoppinglist. PUT"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create the shoppinglist
        reqst = self.client().post(
            self.shoppinglist_route,
            headers=dict(Auth="Bearer " + access_token),
            data=self.shoppinglist)
        self.assertEqual(reqst.status_code, 201)
        # get the json with the shoppinglist
        results = json.loads(reqst.data.decode())

        # edit the created shoppinglist
        reqst = self.client().put(self.shoppinglist_route + '{}'.format(results['id']),
            headers=dict(Auth="Bearer " + access_token),
            data={
                "name": "Clothes and Foodstuff"
            })
        self.assertEqual(reqst.status_code, 200)

        # return the edited list and confirm edit.
        results = self.client().get(self.shoppinglist_route + '{}'.format(results['id']),
            headers=dict(Auth="Bearer " + access_token))
        self.assertIn('Foodstuff', str(results.data))

    def test_shoppinglist_delete(self):
        """Test deletetion an existing shoppinglist."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        reqst = self.client().post(
            self.shoppinglist_route,
            headers=dict(Auth="Bearer " + access_token),
            data=self.shoppinglist)
        self.assertEqual(reqst.status_code, 201)
        results = json.loads(reqst.data.decode())

        # delete the shoppinglist just created
        reqst = self.client().delete(self.shoppinglist_route + '{}'.format(results['id']),
            headers=dict(Auth="Bearer " + access_token))
        self.assertEqual(reqst.status_code, 200)

        # Test to see if it still exists
        result = self.client().get(
            self.shoppinglist_route + '1',
            headers=dict(Auth="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def test_shoppinglist_share(self):
        """Test if a shoppinglist share status can be changed"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        reqst = self.client().post(
            self.shoppinglist_route,
            headers=dict(Auth="Bearer " + access_token),
            data=self.shoppinglist)
        self.assertEqual(reqst.status_code, 201)
        results = json.loads(reqst.data.decode())

        # share the shoppinglist just created
        req = self.client().put(self.share_route + '{}'.format(results['id']),
            headers=dict(Auth="Bearer " + access_token))
        self.assertEqual(req.status_code, 200)

        # check if share status can be reverted
        req2 = self.client().put(self.share_route + '{}'.format(results['id']),
            headers=dict(Auth="Bearer " + access_token))
        self.assertEqual(req2.status_code, 200)

    def test_shoppinglist_searching(self):
        """Test if one can search for a shoppinglist and limit result"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        reqst = self.client().post(
            self.shoppinglist_route,
            headers=dict(Auth="Bearer " + access_token),
            data=self.shoppinglist)
        self.assertEqual(reqst.status_code, 201)

        # search the shoppinglist just created
        req = self.client().get(self.search_route + '?{}'.format(urllib.parse.urlencode({"q":"clothes"})),
            headers=dict(Auth="Bearer " + access_token))
        self.assertEqual(req.status_code, 201)

        # limit a search to 1
        req2 = self.client().get(self.search_route + '?{}'.format(urllib.parse.urlencode({"limit":"1"})),
            headers=dict(Auth="Bearer " + access_token))
        self.assertEqual(req2.status_code, 201)

        # search using name and limit
        req = self.client().get(self.search_route + '?{}'.format(urllib.parse.urlencode({"q":"clothes", "limit":"1"})),
            headers=dict(Auth="Bearer " + access_token))
        self.assertEqual(req.status_code, 201)

    def test_item_creation(self):
        """Test if the API can create an item in a shoppinglist (POST)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        # create a shoppinglist using post
        reqst = self.create_shoppinglist(access_token)
        results = json.loads(reqst.data.decode())
        # create a item using post
        item_reqst = self.client().post(self.shoppinglist_route + '{}'.format(results['id'])+'/items/',
            headers=dict(Auth="Bearer " + str(access_token)),
            data=self.item)
        self.assertEqual(item_reqst.status_code, 201)
        self.assertIn('shirt', str(item_reqst.data))

    def test_get_all_items(self):
        """Test GET request for items in a shoppinglist."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a  request
        reqst = self.create_shoppinglist(access_token)
        self.assertEqual(reqst.status_code, 201)

        results = json.loads(reqst.data.decode())
        #create an item
        item_reqst = self.client().post(self.shoppinglist_route + '{}'.format(results['id'])+'/items/',
            headers=dict(Auth="Bearer " + str(access_token)),
            data=self.item)
        self.assertEqual(item_reqst.status_code, 201)
        self.assertIn('shirt', str(item_reqst.data))

        # get all the items that belong to the test shoppinglist
        reqst = self.client().get(self.shoppinglist_route + '{}'.format(results['id'])+'/items/' + '{}'.format(results['id']),
            headers=dict(Auth="Bearer " + access_token),
        )
        self.assertEqual(reqst.status_code, 200)
        self.assertIn('shirt', str(reqst.data))

    def test_get_item_by_id(self):
        """Test get a single item in a shoppinglist by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        reqst = self.create_shoppinglist(access_token)

        results = json.loads(reqst.data.decode())
        result = self.client().get(
            self.shoppinglist_route + '{}'.format(results['id']),
            headers=dict(Auth="Bearer " + access_token))
        # assert that the shoppinglist is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('clothes sl', str(result.data))

        #create an item
        item_reqst = self.client().post(self.shoppinglist_route + '{}'.format(results['id'])+'/items/' ,
            headers=dict(Auth="Bearer " + str(access_token)),
            data=self.item)
        self.assertEqual(item_reqst.status_code, 201)
        self.assertIn('shirt', str(item_reqst.data))
        item_results = json.loads(item_reqst.data.decode())
        #request item
        result = self.client().get(self.shoppinglist_route + '{}'.format(results['id'])+'/items/' + '{}'.format(item_results['id']),
            headers=dict(Auth="Bearer " + access_token))
        # assert that the item is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('shirt', str(result.data))

    def test_item_can_be_edited_or_deleted(self):
        """Test edit and delete on an existing item. PUT & DELETE"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create the shoppinglist
        reqst = self.create_shoppinglist(access_token)
        # get the json with the shoppinglist
        results = json.loads(reqst.data.decode())
        #create an item
        item_reqst = self.client().post(self.shoppinglist_route + '{}'.format(results['id'])+'/items/',
            headers=dict(Auth="Bearer " + str(access_token)),
            data=self.item)
        self.assertEqual(item_reqst.status_code, 201)
        self.assertIn('shirt', str(item_reqst.data))
        item_results = json.loads(item_reqst.data.decode())

        # edit the created item
        edit_reqst = self.client().put(self.shoppinglist_route + '{}'.format(results['id']) + '/items/' + '{}'.format(item_results['id']),
            headers=dict(Auth="Bearer " + access_token),
            data={
                "name": "sweater",
                "price": "10",
                "quantity": "1"
            })

        self.assertEqual(edit_reqst.status_code, 200)

        # return the edited list item and confirm edit.
        edit_results = self.client().get(self.shoppinglist_route + '{}'.format(results['id'])+'/items/',
            headers=dict(Auth="Bearer " + access_token))
        self.assertIn('sweater', str(edit_results.data))

        # delete the item
        delete_reqst = self.client().delete(self.shoppinglist_route + '{}'.format(results['id'])+'/items/' + '{}'.format(item_results['id']),headers=dict(Auth="Bearer " + access_token))
        self.assertEqual(delete_reqst.status_code, 200)

        # Test to see if item still exists
        result = self.client().get(
            self.shoppinglist_route + '{}'.format(results['id'])+'/items/' + '{}'.format(item_results['id']),
            headers=dict(Auth="Bearer " + access_token))

        self.assertEqual(result.status_code, 404)

if __name__ == "__main__":
    unittest.main()
