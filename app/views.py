from flask import make_response, request, jsonify, Blueprint, abort

from flask_bcrypt import Bcrypt
from app.models import User, Shoppinglist, Item, Buddy
import re
from app.email_handler import handler, decode_token,reset_handler

# Define the blueprints
auth_bp = Blueprint('auth', __name__)
shoppinglist_bp = Blueprint('shoppinglist',__name__)

@auth_bp.route('/', methods = ['GET'])
def home():
    response = {
        'message': 'welcome to Fancy shoppinglist API'
    }
    return make_response(jsonify(response)), 200

#route only takes post method and handles register
@auth_bp.route('/auth/register', methods = ['POST'])
def register():
    post_data = request.data
    username = post_data['username'] if post_data['username'] else None
    password = post_data['password'] if post_data['password'] else None
    email = post_data['email'] if post_data['email'] else None
    if username and password and email:
        # check if the user already exists
        user = User.query.filter_by(username=username).first()
        useremail = User.query.filter_by(email=email).first()
        if not user and not useremail:
            #the user doesnt exist so try to register them
            try:

                username = username.lower()
                email = email.lower()
                if not re.match(r"^[a-z0-9_]*$", username):
                    response = {
                        'message': 'please enter a valid username'
                    }
                    return make_response(jsonify(response)), 401
                if not re.match(r"(^[a-zA-Z0-9_.]+@[a-zA-Z0-9-]+\.[a-z]+$)", email) and not re.match(r"(^[a-z0-9_.]+@[a-z0-9-]+\.[a-z]+\.[a-z]+$)", email):
                    response = {
                        'message': 'please enter a valid email address'
                    }
                    return make_response(jsonify(response)), 401
                if len(password)<6:
                    response = {
                        'message': 'password must be at least 6 characters long'
                    }
                    return make_response(jsonify(response)), 401
                email_sent=handler(email)
                if email_sent != "":
                    pass
                else:
                    emails = {
                        'message': 'email not sent'
                    }
                    return make_response(jsonify(emails)), 401
                user = User(username=username,email=email, password=password)
                user.save()

                response = {
                    'message': 'You registered successfully. Comfirm your account using the link sent to your email'
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
    else:
        #the user hasnt enteres all required fields
        response = {
            'message': 'please input all the required data.'
        }
        # return message with code 401
        return make_response(jsonify(response)), 401

#handle email verification
@auth_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    email = decode_token(token)

    if not re.match(r"(^[a-zA-Z0-9_.]+@[a-zA-Z0-9-]+\.[a-z]+$)", email) and not re.match(r"(^[a-z0-9_.]+@[a-z0-9-]+\.[a-z]+\.[a-z]+$)", email):
        message = email
        response = {
            'message': message
        }
        return make_response(jsonify(response)), 401

    else:
        user = User.query.filter_by(email=email).first()
        user.confirmed = True
        user.save()
        response = {
        'message': 'email confirmed. you can now login'
        }
        return make_response(jsonify(response)), 200

@auth_bp.route('/auth/resend_confirmation', methods=['POST'])
def resend_confirm():
    email = request.data['email'] if request.data['email'] else None
    if email:
        if not re.match(r"(^[a-zA-Z0-9_.]+@[a-zA-Z0-9-]+\.[a-z]+$)", email) and not re.match(r"(^[a-z0-9_.]+@[a-z0-9-]+\.[a-z]+\.[a-z]+$)", email):
            message = "please enter a valid email adress"
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401
        else:
            user = User.query.filter_by(email=email).first()
            if not user:
                response = {
                    'message': 'You do not have an account on fancy shoppinglist, Please register to continue'
                }
                return make_response(jsonify(response)), 401
            if user.confirmed == True:
                response = {
                    'message': 'Your account is already confirmed, please login'
                }
                return make_response(jsonify(response)), 401
            handler(email)
            response = {
                'message': 'Comfirm your account using the link sent to your email'
            }
            return make_response(jsonify(response)), 200
    else:
        #the user hasnt entered an email
        response = {
            'message': 'please enter an email.'
        }
        # return message with code 401
        return make_response(jsonify(response)), 401


@auth_bp.route('/auth/forgot_password', methods=['POST'])
def forgot_password():
    email = request.data['email'] if request.data['email'] else None
    if email:
        if not re.match(r"(^[a-zA-Z0-9_.]+@[a-zA-Z0-9-]+\.[a-z]+$)", email) and not re.match(r"(^[a-z0-9_.]+@[a-z0-9-]+\.[a-z]+\.[a-z]+$)", email):
            message = "please enter a valid email adress"
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401
        else:
            user = User.query.filter_by(email=email).first()
            if not user:
                response = {
                    'message': 'You do not have an account on fancy shoppinglist, Please register to continue'
                }
                return make_response(jsonify(response)), 401
            if user.confirmed == False:
                response = {
                    'message': 'please confirm your account',
                    'link': '/auth/resend_confirmation'
                }
                return make_response(jsonify(response)), 401
            reset_handler(email)
            response = {
                'message': 'A reset password link has been sent to your email adress'
            }
            return make_response(jsonify(response)), 200
    else:
        #the user hasnt entered an email
        response = {
            'message': 'please enter an email.'
        }
        # return message with code 401
        return make_response(jsonify(response)), 401

@auth_bp.route('/auth/reset_password/<token>', methods=['POST'])
def reset_password(token):
    email = decode_token(token)

    if not re.match(r"(^[a-zA-Z0-9_.]+@[a-zA-Z0-9-]+\.[a-z]+$)", email) and not re.match(r"(^[a-z0-9_.]+@[a-z0-9-]+\.[a-z]+\.[a-z]+$)", email):
        message = email
        response = {
            'message': message
        }
        return make_response(jsonify(response)), 401

    else:
        if request.method == 'POST':

            new_password = request.data['password'] if request.data['password'] else None
            if new_password:
                user = User.query.filter_by(email=email).first()
                if not user:
                    response = {
                        'message': 'You do not have an account on fancy shoppinglist, Please register to continue'
                    }
                    return make_response(jsonify(response)), 401
                user.password = Bcrypt().generate_password_hash(new_password).decode()
                user.save()
                response = {
                'message': 'password updated, you can now login'
                }
                return make_response(jsonify(response)), 200
            else:
                #the user hasnt entered a new password
                response = {
                    'message': 'please enter a new password.'
                }
                # return message with code 401
                return make_response(jsonify(response)), 401

#handle login
@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        #find the user using their username
        username= str(request.data['username']) if str(request.data['username']) else None
        password= str(request.data['password']) if str(request.data['password']) else None
        if not username or not password:
            response = {
                'message': 'please enter all the required fields',
            }
            return make_response(jsonify(response)), 401
        user = User.query.filter_by(username=username).first()

        if user and user.validate_password(password):
            #generate the access token for auth header
            if user.confirmed==False:
                response = {
                    'message': 'please verify your email before logging in',
                    'link': '/auth/resend_confirmation'
                }
                return make_response(jsonify(response)), 401
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

@auth_bp.route('/user/', methods=['GET', 'PUT', 'DELETE'])
def user_profile():
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header

    if access_token:
        # Get the user id in token
        user_id = User.decode_token(access_token)
        #check if token has an integer an doesnt creat an error
        if not isinstance(user_id, str):
            user=User.query.filter_by(id=user_id).first()
            if request.method == 'PUT':
                # obtain a username from data
                username = str(request.data.get('username', '')) if str(request.data.get('username', '')) and re.match(r"^[a-z0-9_]*$", str(request.data.get('username', ''))) else user.username
                password = str(request.data.get('password', '')) if str(request.data.get('password', '')) else None
                new_password = str(request.data.get('new_password', '')) if str(request.data.get('new_password', '')) else None
                email = str(request.data.get('email', '')) if str(request.data.get('email', '')) and re.match(r"(^[a-zA-Z0-9_.]+@[a-zA-Z0-9-]+\.[a-z]+$)", str(request.data.get('email', ''))) or re.match(r"(^[a-z0-9_.]+@[a-z0-9-]+\.[a-z]+\.[a-z]+$)", str(request.data.get('email', ''))) else user.email
                existing_user=User.query.all()
                em=0
                em2=0
                msgarray=[]
                for i in existing_user:
                    if username == i.username:
                        if not str(request.data.get('username', '')):
                            em2=1
                        elif i.id==user_id:
                            response={
                                'message': 'You are already using that username'
                            }
                            return make_response(jsonify(response)), 401
                        else:
                            response = {
                                'message': 'USERNAME NOT UPDATED: a user with that username already exists'
                            }
                            return make_response(jsonify(response)), 401
                    if email == i.email:
                        if not str(request.data.get('email', '')):
                            em=1
                        elif i.id==user_id:
                            response={
                                'message': 'You are already using that email'
                            }
                            return make_response(jsonify(response)), 401
                        else:
                            response = {
                                'message': 'EMAIL NOT UPDATED: a user with that email already exists'
                            }
                            return make_response(jsonify(response)), 401

                if password or new_password:
                    if password and new_password:
                        if user.validate_password(password):
                            if len(new_password)<6:
                                response = {
                                    'message': 'New password is too short'
                                }
                                return make_response(jsonify(response)), 401

                        else:
                            response = {
                                'message': 'Anouthorized: the current password you entered is invalid'
                            }
                            return make_response(jsonify(response)), 401
                    else:
                        response = {
                            'message': 'Please enter both your new and old password to change password'
                        }
                        return make_response(jsonify(response)), 401
                    user.password = Bcrypt().generate_password_hash(new_password).decode()
                    msgarray.append("Password updated")
                if em==0:
                    handler(email)
                    user.confirmed=False
                    user.email = email
                    msgarray.append("Email updated, You will need to confirm your email account")
                if em2==0:
                    user.username = username
                    msgarray.append("Username updated")
                user.save()

                response = {
                    'message':msgarray,
                    'id': user.id,
                    'confirmed': user.confirmed,
                    'username': user.username,
                    'email': user.email,
                    'date_created': user.date_created,
                    'date_modified': user.date_modified
                }
                return make_response(jsonify(response)), 200
            if request.method == 'DELETE':
                buddy = Buddy.query.filter_by(friend_id=user_id).all()
                for i in buddy:
                    i.delete()
                # delete the user
                user.delete()
                return {
                    "message": "user {} deleted".format(user.username)
                }, 200
            else:
                profile = jsonify({
                    'id': user.id,
                    'username': user.username,
                    'confirmed': user.confirmed,
                    'email': user.email,
                    'date_created': user.date_created,
                    'date_modified': user.date_modified
                })
                return make_response(profile), 200
        else:
            # user is not authenticated send error message
            message = user_id
            response = {
                'message': message
            }
            # reurn an anouthorized message
            return make_response(jsonify(response)), 401
@shoppinglist_bp.route('/shoppinglists/', methods=['POST', 'GET'])
def shoppinglists_view():
    # Get the access token from header
    auth_header = request.headers.get('Auth')
    access_token = auth_header

    if access_token:
     # decode the token and get the user_id
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            # handle requests after authentication
            if request.method == "POST":
                name = str(request.data.get('name', '')).strip()
                if name:
                    if not re.match(r"^[a-zA-Z0-9_ -]*$", name):
                        response = {
                            'message': 'please enter a valid shoppinglist name'
                        }
                        return make_response(jsonify(response)), 401
                    existing_list=Shoppinglist.query.filter_by(owned_by=user_id).all()
                    for i in existing_list:
                        if name.lower() == i.name.lower():
                            response = {
                                'message': 'shoppinglist already exists'
                            }
                            return make_response(jsonify(response)), 401
                    shoppinglist = Shoppinglist(name=name, owned_by=user_id)
                    shoppinglist.save()
                    response = jsonify({
                        'id': shoppinglist.id,
                        'name': shoppinglist.name,
                        'shared': shoppinglist.shared,
                        'date_created': shoppinglist.date_created,
                        'date_modified': shoppinglist.date_modified,
                        'owned_by': user_id
                    })

                    return make_response(response), 201
                else:
                    response = {
                        'message': 'please enter all the required fields'
                    }
                    return make_response(jsonify(response)), 401

            else:
                if not request.args.get('limit') and not request.args.get('q'):
                    # get all shoppinglists created by this user
                    shoppinglists = Shoppinglist.query.filter_by(owned_by=user_id).all()
                    results = []

                    for shoppinglist in shoppinglists:
                        obj = {
                            'id': shoppinglist.id,
                            'name': shoppinglist.name,
                            'shared': shoppinglist.shared,
                            'date_created': shoppinglist.date_created,
                            'date_modified': shoppinglist.date_modified,
                            'owned_by': shoppinglist.owned_by
                        }
                        results.append(obj)

                    return make_response(jsonify(results=results)), 200
                if not isinstance(user_id, str):
                    shoppinglist_content = Shoppinglist.query.filter_by(owned_by=user_id).all()
                    if not shoppinglist_content:
                        return make_response(jsonify({ 'message': 'you dont have any shoppinglists'})), 404
                if request.args.get('q'):
                    list_name = str(request.args.get('q'))
                    if list_name:
                        result_ids = []
                        res = []
                        try:
                            for slist in shoppinglist_content:
                               if list_name in slist.name:
                                    result_ids.append(slist.id)
                            results = Shoppinglist.query.filter(Shoppinglist.id.in_(result_ids)).all()
                            if not results:
                                return make_response(jsonify({ 'message': 'you dont have any shoppinglists with that name'})), 401
                            for shoppinglist in results:
                                obj = {
                                    'id': shoppinglist.id,
                                    'name': shoppinglist.name,
                                    'shared': shoppinglist.shared,
                                    'date_created': shoppinglist.date_created,
                                    'date_modified': shoppinglist.date_modified,
                                    'owned_by': shoppinglist.owned_by
                                }
                                res.append(obj)
                            return make_response(jsonify(result=res)), 200
                        except Exception as e:
                            return make_response(jsonify({ 'message': str(e)})), 401

                if request.args.get('limit') and request.args.get('start'):
                    try:
                        start=int(request.args.get('start'))
                        limit=int(request.args.get('limit'))
                    except Exception:
                        return make_response(jsonify({'info': 'Please enter limit or start as an integer'})), 401

                    if start <= 0 or limit <= 0:
                        return make_response(jsonify({'info': 'Start or Limit must be a number greater than or equal to 1'})), 401
                    if start and limit:
                        res = []
                        try:
                            results = Shoppinglist.query.order_by(Shoppinglist.id).filter_by(owned_by=user_id).paginate(start,limit,error_out=False)
                            if not results:
                                return make_response(jsonify({ 'message': 'error occured'})), 401
                            url = '/shoppinglists/'
                            previous = results.prev_num
                            nextint= results.next_num
                            if start<=1:links = {
                                'next': url + '?start=%d&limit=%d' % (nextint, limit)
                            }
                            elif len(results.items)<limit :
                                links = {
                                    'previous': url + '?start=%d&limit=%d' % (previous, limit)
                                }
                            else:
                                links = {
                                'next': url + '?start=%d&limit=%d' % (nextint, limit),
                                'previous': url + '?start=%d&limit=%d' % (previous, limit)
                                }

                            for shoppinglist in results.items:
                                obj = {
                                    'id': shoppinglist.id,
                                    'name': shoppinglist.name,
                                    'shared': shoppinglist.shared,
                                    'date_created': shoppinglist.date_created,
                                    'date_modified': shoppinglist.date_modified,
                                    'owned_by': shoppinglist.owned_by
                                }
                                res.append(obj)
                            return make_response(jsonify(links=links,result=res)), 200
                        except Exception as e:
                            return make_response(jsonify({ 'message': str(e)})), 401
                else:
                    # get all shoppinglists created by this user
                    shoppinglists = Shoppinglist.query.filter_by(owned_by=user_id).all()
                    results = []

                    for shoppinglist in shoppinglists:
                        obj = {
                            'id': shoppinglist.id,
                            'name': shoppinglist.name,
                            'shared': shoppinglist.shared,
                            'date_created': shoppinglist.date_created,
                            'date_modified': shoppinglist.date_modified,
                            'owned_by': shoppinglist.owned_by
                        }
                        results.append(obj)

                    return make_response(jsonify(results=results)), 200

        else:
            # user is not authorised return error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

@shoppinglist_bp.route('/shoppinglists/<int:list_id>', methods=['GET', 'PUT', 'DELETE'])
def shoppinglist_manipulation(list_id, **kwargs):
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header

    if access_token:
        # Get the user id in token
        user_id = User.decode_token(access_token)
        #check if token has an integer an doesnt creat an error
        if not isinstance(user_id, str):

            # Get the shoppinglist with the id specified
            shoppinglist = Shoppinglist.query.filter_by(id=list_id,owned_by=user_id).first()
            if not shoppinglist:
                # There is no shoppinglist with this id for this user so raise 404 error
                abort(404)

            if request.method == "DELETE":
                # delete the shoppinglist
                shoppinglist.delete()
                return {
                    "message": "shoppinglist {} deleted".format(shoppinglist.id)
                }, 200

            elif request.method == 'PUT':
                # obtain a name from data
                name = str(request.data.get('name', '')).strip() if str(request.data.get('name', '')) and re.match(r"^[a-zA-Z0-9_ -]*$", str(request.data.get('name', ''))) and str(request.data.get('name', '')).strip() !="" else shoppinglist.name
                existing_list=Shoppinglist.query.filter_by(owned_by=user_id).all()
                for i in existing_list:
                    if name == i.name:
                        response = {
                            'message': 'NOT UPDATED: shoppinglist with that name already exists or a blank input was submitted'
                        }
                        return make_response(jsonify(response)), 401
                shoppinglist.name = name
                shoppinglist.save()

                response = {
                    'id': shoppinglist.id,
                    'name': shoppinglist.name,
                    'shared': shoppinglist.shared,
                    'date_created': shoppinglist.date_created,
                    'date_modified': shoppinglist.date_modified,
                    'owned_by': shoppinglist.owned_by
                }
                return make_response(jsonify(response)), 200
            else:
                # send back the shoppinglist to the user if the request is GET
                response = {
                    'id': shoppinglist.id,
                    'name': shoppinglist.name,
                    'shared': shoppinglist.shared,
                    'date_created': shoppinglist.date_created,
                    'date_modified': shoppinglist.date_modified,
                    'owned_by': shoppinglist.owned_by
                }
                return make_response(jsonify(response)), 200
        else:
            # user is not authenticated send error message
            message = user_id
            response = {
                'message': message
            }
            # reurn an anouthorized message
            return make_response(jsonify(response)), 401

@shoppinglist_bp.route('/shoppinglists/share/<int:list_id>', methods=['GET', 'PUT'])
def shoppinglist_share(list_id, **kwargs):
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header

    if access_token:
        # Get the user id in token
        user_id = User.decode_token(access_token)
        #check if token has an integer an doesnt creat an error
        if not isinstance(user_id, str):

            # Get the shoppinglist with the id specified
            shoppinglist = Shoppinglist.query.filter_by(id=list_id).first()
            if not shoppinglist:
                # There is no shoppinglist with this id for this user so raise 404 error
                abort(404)

            elif request.method == 'PUT':
                if shoppinglist.shared == False:
                    shoppinglist.shared = True
                    shoppinglist.save()
                else:
                    shoppinglist.shared = False
                    shoppinglist.save()


                response = {
                    'id': shoppinglist.id,
                    'name': shoppinglist.name,
                    'shared': shoppinglist.shared,
                    'date_created': shoppinglist.date_created,
                    'date_modified': shoppinglist.date_modified,
                    'owned_by': shoppinglist.owned_by
                }
                return make_response(jsonify(response)), 200
            else:
                # send back the shoppinglist to the user if the request is GET
                response = {
                    'id': shoppinglist.id,
                    'name': shoppinglist.name,
                    'shared': shoppinglist.shared,
                    'date_created': shoppinglist.date_created,
                    'date_modified': shoppinglist.date_modified,
                    'owned_by': shoppinglist.owned_by
                }
                return make_response(jsonify(response)), 200
        else:
            # user is not authenticated send error message
            message = user_id
            response = {
                'message': message
            }
            # reurn an anouthorized message
            return make_response(jsonify(response)), 401


@shoppinglist_bp.route('/shoppinglists/<int:list_id>/items/', methods=['POST', 'GET'])
def items_view(list_id):
    # Get the access token from header
    auth_header = request.headers.get('Auth')
    access_token = auth_header

    if access_token:
     # decode the token and get the user_id
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            # handle requests after authentication
            shoppinglist = Shoppinglist.query.filter_by(id=list_id).first()
            if shoppinglist.owned_by == user_id:
                if request.method == "POST":
                    name = str(request.data.get('name', '')).strip()
                    price = request.data.get('price', '').strip('.') if re.match(r"^[0-9]+\.[0-9]*$", request.data.get('price', '')) or re.match(r"^[0-9]*$", request.data.get('price', '')) else None
                    quantity = request.data.get('quantity', '').strip('.') if re.match(r"^[0-9]+\.[0-9]*$", request.data.get('quantity', '')) or re.match(r"^[0-9]*$", request.data.get('quantity', '')) else None
                    if not re.match(r"^[0-9]*$", request.data.get('price', '')) and not re.match(r"^[0-9]+\.[0-9]*$", request.data.get('price', '')):
                        response = {
                            'message': 'please enter the correct value for price'
                        }
                        return make_response(jsonify(response)), 401
                    if not re.match(r"^[0-9]+\.[0-9]*$", request.data.get('quantity', '')) and not re.match(r"^[0-9]*$", request.data.get('quantity', '')):
                        response = {
                            'message': 'please enter the correct value for quantity'
                        }
                        return make_response(jsonify(response)), 401
                    if not name or not price or not quantity:
                        response = {
                            'message': 'please enter all the required fields'
                        }
                        return make_response(jsonify(response)), 401
                    else:
                        if not re.match(r"^[a-zA-Z0-9_ -]*$", name):
                            response = {
                                'message': 'please enter a valid item name'
                            }
                            return make_response(jsonify(response)), 401
                        existing_item=Item.query.filter_by(belongs_to=list_id).all()
                        for i in existing_item:
                            if name.lower() == i.name.lower():
                                response = {
                                    'message': 'item with that name already exists'
                                }
                                return make_response(jsonify(response)), 401
                        item = Item(name=name, price=price, quantity=quantity, belongs_to=list_id)
                        item.save()
                        response = jsonify({
                            'id': item.id,
                            'name': item.name,
                            'price': item.price,
                            'quantity': item.quantity,
                            'date_created': item.date_created,
                            'date_modified': item.date_modified,
                            'shoppinglist_id': item.belongs_to
                        })

                        return make_response(response), 201


                else:
                    if not request.args.get('limit') and not request.args.get('q'):
                        # get all items created for this shoppinglist
                        item_list = Item.get_all(list_id)
                        results = []
                        for item in item_list:
                            obj = {
                                'id': item.id,
                                'name': item.name,
                                'price': item.price,
                                'quantity': item.quantity,
                                'date_created': item.date_created,
                                'date_modified': item.date_modified,
                                'shoppinglist_id': item.belongs_to
                            }
                            results.append(obj)

                        return make_response(jsonify(results=results)), 200
                    if not isinstance(user_id, str):
                        item_content = Item.query.filter_by(belongs_to=list_id).all()
                        if not item_content:
                            return make_response(jsonify({ 'message': 'you dont have any items for this shoppinglists'})), 404
                    if request.args.get('q'):
                        item_name = str(request.args.get('q'))
                        if item_name:
                            result_ids = []
                            res = []
                            try:
                                for sitem in item_content:
                                   if item_name in sitem.name:
                                        result_ids.append(sitem.id)
                                results = Item.query.filter(Item.id.in_(result_ids)).all()
                                if not results:
                                    return make_response(jsonify({ 'message': 'you dont have any items with that name on this shoppinglist'})), 401
                                for item in results:
                                    obj = {
                                        'id': item.id,
                                        'name': item.name,
                                        'price': item.price,
                                        'quantity': item.quantity,
                                        'date_created': item.date_created,
                                        'date_modified': item.date_modified,
                                        'shoppinglist_id': item.belongs_to
                                    }
                                    res.append(obj)
                                return make_response(jsonify(result=res)), 200
                            except Exception as e:
                                return make_response(jsonify({ 'message': str(e)})), 401
                    if request.args.get('limit') and request.args.get('start'):
                        try:
                            start=int(request.args.get('start'))
                            limit=int(request.args.get('limit'))
                        except Exception:
                            return make_response(jsonify({'info': 'Please make sure limit and start are both integers'})), 401

                        if start <= 0 or limit <= 0:
                            return make_response(jsonify({'info': 'Start or Limit must be a number greater than or equal to 1'})), 401
                        if start and limit:
                            res = []
                            try:
                                results = Item.query.order_by(Item.id).filter_by(belongs_to=list_id).paginate(start,limit,error_out=False)
                                if not results:
                                    return make_response(jsonify({ 'message': 'error occured'})), 401
                                url = '/shoppinglists/' + '{}'.format(list_id) + '/items/'
                                previous = results.prev_num
                                nextint= results.next_num
                                if start<=1:links = {
                                    'next': url + '?start=%d&limit=%d' % (nextint, limit)
                                }
                                elif len(results.items)<limit :
                                    links = {
                                        'previous': url + '?start=%d&limit=%d' % (previous, limit)
                                    }
                                else:
                                    links = {
                                    'next': url + '?start=%d&limit=%d' % (nextint, limit),
                                    'previous': url + '?start=%d&limit=%d' % (previous, limit)
                                    }

                                for item in results.items:
                                    obj = {
                                        'id': item.id,
                                        'name': item.name,
                                        'price': item.price,
                                        'quantity': item.quantity,
                                        'date_created': item.date_created,
                                        'date_modified': item.date_modified,
                                        'shoppinglist_id': item.belongs_to
                                    }
                                    res.append(obj)
                                return make_response(jsonify(links=links,result=res)), 200
                            except Exception as e:
                                return make_response(jsonify({ 'message': str(e)})), 401
                    else:
                        item_list = Item.get_all(list_id)
                        results = []
                        for item in item_list:
                            obj = {
                                'id': item.id,
                                'name': item.name,
                                'price': item.price,
                                'date_created': item.date_created,
                                'date_modified': item.date_modified,
                                'quantity': item.quantity,
                                'shoppinglist_id': item.belongs_to
                            }
                            results.append(obj)

                        return make_response(jsonify(results=results)), 200
            else:
                response = {
                    'message': 'anouthorized'
                }
                return make_response(jsonify(response)), 401

        else:
            # user is not authorised return error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

@shoppinglist_bp.route('/shoppinglists/<int:list_id>/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
def item_manipulation(list_id, item_id, **kwargs):
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header

    if access_token:
        # Get the user id in token
        user_id = User.decode_token(access_token)
        #check if token has an integer an doesnt creat an error
        if not isinstance(user_id, str):

            # Get the item with the id specified
            item = Item.query.filter_by(id=item_id, belongs_to=list_id).first()
            if not item:
                # There is no item with this id for this shoppinglist so raise 404 error
                abort(404)

            if request.method == "DELETE":
                # delete the item
                item.delete()
                return {
                    "message": "{} item deleted".format(item.name)
                }, 200

            elif request.method == 'PUT':
                #obtain updates from data if not, use the existing
                name = str(request.data.get('name', '')).strip() if str(request.data.get('name', '')) and re.match(r"^[a-zA-Z0-9_ -]*$", str(request.data.get('name', ''))) and str(request.data.get('name', '')).strip != "" else item.name
                price = str(request.data.get('price', '')).strip('.') if str(request.data.get('price', '')) and re.match(r"^[0-9]*$", str(request.data.get('price', ''))) or re.match(r"^[0-9]+\.[0-9]*$", request.data.get('price', '')) else item.price
                quantity = str(request.data.get('quantity', '')).strip('.') if str(request.data.get('quantity', '')) and re.match(r"^[0-9]*$", str(request.data.get('quantity', ''))) or re.match(r"^[0-9]+\.[0-9]*$", request.data.get('quantity', '')) else item.quantity

                existing_item=Item.query.filter_by(belongs_to=list_id).all()
                for i in existing_item:
                    if name == i.name and item_id != i.id:
                        response = {
                            'message': 'NOT UPDATED: item with that name already exists or a blank input was submitted'
                        }
                        return make_response(jsonify(response)), 401
                item.name = name
                item.price = price
                item.quantity = quantity
                item.save()

                response = {
                    'id': item.id,
                    'name': item.name,
                    'price': item.price,
                    'quantity': item.quantity,
                    'date_created': item.date_created,
                    'date_modified': item.date_modified,
                    'shoppinglist_id': item.belongs_to
                }
                return make_response(jsonify(response)), 200
            else:
                # send back the item to the user if the request is GET
                response = {
                    'id': item.id,
                    'name': item.name,
                    'price': item.price,
                    'quantity': item.quantity,
                    'date_created': item.date_created,
                    'date_modified': item.date_modified,
                    'shoppinglist_id': item.belongs_to
                }
                return make_response(jsonify(response)), 200
        else:
            # user is not authenticated send error message
            message = user_id
            response = {
                'message': message
            }
            # reurn an anouthorized message
            return make_response(jsonify(response)), 401

@shoppinglist_bp.route('/buddies/', methods=['GET', 'POST'])
def buddies_view():
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header

    if access_token:
        # Get the user id in token
        user_id = User.decode_token(access_token)
        #check if token has an integer an doesnt creat an error
        if not isinstance(user_id, str):

            if request.method == "POST":
                username = str(request.data.get('username', ''))
                if username:
                    buddies = Buddy.query.filter_by(parent=user_id).all()
                    user = User.query.filter_by(username=username).first()
                    if not user:
                        response = {
                            'message': 'friend not added: User does not exist.'
                        }
                        # return user doesnt exist
                        return make_response(jsonify(response)), 401
                    if user.id == user_id:
                        response = {
                            'message': 'You can\'nt  add yourself as a friend.'
                        }
                        # return user doesnt exist
                        return make_response(jsonify(response)), 401
                    exists = False
                    for i in buddies:
                        exists = True if i.friend_id == user.id else False

                    if exists == True:
                        response = {
                            'message': 'Not added: You are already friends.'
                        }
                        # return user doesnt exist
                        return make_response(jsonify(response)), 401

                    buddy = Buddy(friend_id=user.id,parent=user_id)
                    buddy_two = Buddy(friend_id=user_id,parent=user.id)
                    buddy.save()
                    buddy_two.save()

                    response = {
                        'message': 'Success: friend added.',
                        'username': username,
                        'friend_id': user.id
                    }
                    # return success
                    return make_response(jsonify(response)), 201
            else:
                buddies = Buddy.query.filter_by(parent=user_id).all()
                response = []
                try:
                    for b in buddies:
                        user = User.query.filter_by(id=b.friend_id).first()
                        friend = {
                            'username': user.username,
                            'friend_id': user.id
                        }
                        response.append(friend)
                    # return success
                    return make_response(jsonify(result=response)), 200
                except Exception as e:
                     response = {
                         'error': str(e),
                         'message': 'error'

                     }
                     #return using code 500 internal server error
                     return make_response(jsonify(response)), 500
        else:
            # user is not authenticated send error message
            message = user_id
            response = {
                'message': message
            }
            # reurn an anouthorized message
            return make_response(jsonify(response)), 401

@shoppinglist_bp.route('/buddies/<int:friend_id>', methods=['GET', 'DELETE'])
def buddies_view_by_id(friend_id):
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header

    if access_token:
        # Get the user id in token
        user_id = User.decode_token(access_token)
        #check if token has an integer an doesnt creat an error
        if not isinstance(user_id, str):
            buddies = Buddy.query.filter_by(parent=user_id,friend_id=friend_id).all()
            if not buddies:
                abort(404)
            if request.method == "DELETE":
                buddy=Buddy.query.filter_by(parent=user_id,friend_id=friend_id).first()
                parent=Buddy.query.filter_by(friend_id=user_id,parent=friend_id).first()
                buddy.delete()
                parent.delete()
                response = {
                    'message': '{} unfriended'.format(friend_id)
                }
                # return ok
                return make_response(jsonify(response)), 200
            else:
                buddies = Buddy.query.filter_by(parent=user_id,friend_id=friend_id).all()
                response = []
                for b in buddies:
                    user = User.query.filter_by(id=b.friend_id).first()
                    friend = {
                        'username': user.username,
                        'friend_id': b.friend_id
                    }
                # return success
                return make_response(jsonify(friend)), 200
        else:
            # user is not authenticated send error message
            message = user_id
            response = {
                'message': message
            }
            # reurn an anouthorized message
            return make_response(jsonify(response)), 401

@shoppinglist_bp.route('/buddies/shoppinglists/', methods=['GET'])
def buddies_list_view():
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header

    if access_token:
        # Get the user id in token
        user_id = User.decode_token(access_token)
        #check if token has an integer an doesnt creat an error
        if not isinstance(user_id, str):
            buddies = Buddy.query.filter_by(parent=user_id).all()
            if not buddies:
                abort(404)

            else:
                blists = []
                result = []
                for b in buddies:
                    slist = Shoppinglist.query.filter_by(owned_by=b.friend_id, shared=True).all()
                    blists.append(slist)
                if blists == []:
                    abort(404)
                for slist in blists:
                    for l in slist:
                        obj = {
                            'id': l.id,
                            'name': l.name,
                            'shared': l.shared,
                            'date_created': l.date_created,
                            'owned_by': l.owned_by
                        }
                        result.append(obj)
                # return success
                return make_response(jsonify(result=result)), 200
        else:
            # user is not authenticated send error message
            message = user_id
            response = {
                'message': message
            }
            # reurn an anouthorized message
            return make_response(jsonify(response)), 401

@shoppinglist_bp.route('/buddies/shoppinglists/<int:list_id>', methods=['GET'])
def buddies_list_items_view(list_id):
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header

    if access_token:
        # Get the user id in token
        user_id = User.decode_token(access_token)
        #check if token has an integer an doesnt creat an error
        if not isinstance(user_id, str):
            if not int(list_id):
                abort(404)

            else:
                result = []
                slist = Shoppinglist.query.filter_by(id=list_id, shared=True).first()
                buddy = Buddy.query.filter_by(parent=user_id,friend_id=slist.owned_by).first()
                if not slist or not buddy:
                    response = {
                        'message': 'Anouthorized'
                    }
                    # return 401
                    return make_response(jsonify(response)), 401
                slist_items = Item.query.filter_by(belongs_to=list_id).all()
                if not slist_items:
                    abort(404)
                for item in slist_items:
                    obj = {
                        'id': item.id,
                        'name': item.name,
                        'price': item.price,
                        'quantity': item.quantity,
                        'date_created': item.date_created,
                        'shoppinglist_id': item.belongs_to
                    }
                    result.append(obj)
                # return success
                return make_response(jsonify(result=result)), 200
        else:
            # user is not authenticated send error message
            message = user_id
            response = {
                'message': message
            }
            # reurn an anouthorized message
            return make_response(jsonify(response)), 401
