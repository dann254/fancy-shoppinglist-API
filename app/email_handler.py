
import jwt
from datetime import datetime, timedelta
from flask import current_app
from app import mail
from flask_mail import Message

def generate_token(email):
    """ Generating confirm mail token"""

    try:
        # set up a payload with an expiration time of 300 minutes in UTC
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=300),
            'iat': datetime.utcnow(),
            'sub': email
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

def handler(email):
    token = generate_token(email)
    url = str(current_app.config.get('APP_URL')) + "/verify/" + str(token)
    message = "<p>Dear " + '{}'.format(str(email)) +",</p><p>You will need to confirm your email to start using <b>Fancy Shoppinglist</b></p><p>If you initiated this confirmation, please click on the link below:<br/>&nbsp;&nbsp;&nbsp;&nbsp;"+ '{}'.format(str(url)) +" </p><p>If you did not initiate this confirmation, you may safely ignore this email</p><p>Sincerely,<br/>Fancy Shoppinglist</p>"
    mbdy="Dear User \nYou will need to confirm your email to start using Fancy Shoppin\nIf you initiated this confirmation, please click on the link be\n&nbsp;&nbsp;&nbsp;&nbsp;%s </p>If you did not initiate this confirmation, you may safely ignore this \nSincerely,\nFancy Shoppin\n" %url
    subject = "Confirm email"
    msg= Message(recipients=[email], html=message, body=mbdy, subject=subject)
    mail.send(msg)
    return url;
