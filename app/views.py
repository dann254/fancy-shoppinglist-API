from flask import make_response, request, jsonify, Blueprint, abort

from app.models import User, Shoppinglist

# Define the blueprints
auth_bp = Blueprint('auth', __name__)
shoppinglist_bp = Blueprint('shoppinglist',__name__)

#route only takes post method and handles register
@auth_bp.route('/auth/register', methods = ['POST'])
def register():
    # check if the user already exists
    user = User.query.filter_by(username=request.data['username']).first()
    if not user:
        #the user doesnt exist so try to register them
        try:
            post_data = request.data
            username = post_data['username']
            password = post_data['password']
            user = User(username=username, password=password)
            user.save()

            response = {
                'message': 'You registered successfully. you can now login'
            }
            #return a response for a successful register with code 201 - created
            return make_response(jsonify(response)), 201

        except Exception as e:
            #return error message if an exception occurs while trying to register user
            response = {
                'message': str(e)
            }
            #include the code 500-server error
            return make_response(jsonify(response)), 500

    else:
        #the user already exists
        response = {
            'message': 'username already exists'
        }
        # return message with code 409 - conflict
        return make_response(jsonify(response)), 409

#handle login
@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        #find the user using their username
        user = User.query.filter_by(username=request.data['username']).first()

        if user and user.validate_password(request.data['password']):
            #generate the access token for auth header
            access_token = user.generate_token(user.id)
            if access_token:
                response = {
                    'message': 'login success',
                    'access_token': access_token.decode()
                }
                #return with status code 200 - OK
                return make_response(jsonify(response)), 200
        else:
            #authentication failed, return error.
            response = {
                'message': 'Invalid username or password'
            }
            return make_response(jsonify(response)), 401

    except Exception as e:
        # Create a response containing error message
        response = {
            'message': str(e)
        }
        #return using code 500 internal server error
        return make_response(jsonify(response)), 500
