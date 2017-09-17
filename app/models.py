from app import db
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
from flask import current_app

class User(db.Model):
    """This defines the users table and gives it a name users """

    __tablename__ = 'users'

    # table collumns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    buddy = db.relationship(
        'Buddy', order_by='Buddy.id', cascade="all, delete-orphan")
    shoppinglist = db.relationship(
        'Shoppinglist', order_by='Shoppinglist.id', cascade="all, delete-orphan")

    def __init__(self, username, password):
        """Initialize user's username and password."""
        self.username = username
        #encrypt password using Bcrypt
        self.password = Bcrypt().generate_password_hash(password).decode()

    def validate_password(self, password):
        """validates user password using Bcrypt"""
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database.(creating and editing)."""
        db.session.add(self)
        db.session.commit()

    def generate_token(self, user_id):
        """ Generating authorization token"""

        try:
            # set up a payload with an expiration time of 300 minutes in UTC
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=300),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create string token using the payload and the secret key provided in configuration
            jwt_string = jwt.encode(
                payload, current_app.config.get('SECRET'),
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)
    #staticmethod does not take self (the object instance) nor  cls (the class) and behaves like a function
    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Auth header."""
        try:
            # try to decode the token using our SECRET
            payload = jwt.decode(token, current_app.config.get('SECRET'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # if the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # if the token is invalid, return an error string
            return "Invalid token. Please register or login"

class Shoppinglist(db.Model):
    """This class defines the shoppinglist table with table name as shoppinglists."""

    __tablename__ = 'shoppinglists'

    # define the columns of the table, starting with its primary key
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    shared = db.Column(db.Boolean(), nullable=False, server_default='0')
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    owned_by = db.Column(db.Integer, db.ForeignKey(User.id))
    items = db.relationship(
        'Item', order_by='Item.id', cascade="all, delete-orphan")

    def __init__(self, name, owned_by, shared=None):
        """Initialize the shoppinglist."""
        self.name = name
        self.owned_by = owned_by
        self.shared = shared

    def save(self):
        """Save a shoppinglist.(update or save new)"""
        db.session.add(self)
        db.session.commit()

    #staticmethod does not take self (the object instance) nor  cls (the class) and behaves like a function
    @staticmethod
    def get_all(user_id):
        """gets all the shoppinglists for a given user."""
        return Shoppinglist.query.filter_by(owned_by=user_id)

    def delete(self):
        """Deletes a passed shoppinglist."""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """Return a representation of a shoppinglist instance."""
        return "<Shoppinglist: {}>".format(self.name, self.shared, self.zone)

class Item(db.Model):
    """ this class defines items for shopping lists """

    __tablename__ = 'items'
    #define collumns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    price = db.Column(db.Integer())
    quantity = db.Column(db.Integer())
    belongs_to = db.Column(db.Integer, db.ForeignKey(Shoppinglist.id))

    def __init__(self, name, price, quantity, belongs_to):
        """Initialize an item and its parent -shoppinglist"""
        self.name = name
        self.price = price
        self.quantity = quantity
        self.belongs_to = belongs_to
    def save(self):
        """Save an item.(update or save new)"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(shoppinglist_id):
        """gets all the items for a given Shoppinglist."""
        return Item.query.filter_by(belongs_to=shoppinglist_id)

    def delete(self):
        """Deletes a passed item."""
        db.session.delete(self)
        db.session.commit()


    def __repr__(self):
        """Return a representation of an item instance."""
        return "<Item: {}>".format(self.name, self.price, self.quantity)

class Buddy(db.Model):
    """ this class defines friends """

    __tablename__ = 'buddies'
    #define collumns
    id = db.Column(db.Integer, primary_key=True)
    friend_id = db.Column(db.Integer())
    parent = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, friend_id, parent):
        """Initialize buddies."""
        self.friend_id = friend_id
        self.parent = parent
    def save(self):
        """Save a buddies"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(user_id):
        """gets all the items for a given Shoppinglist."""
        return Buddy.query.filter_by(parent=user_id)

    def delete(self):
        """Deletes a passed buddy."""
        db.session.delete(self)
        db.session.commit()
