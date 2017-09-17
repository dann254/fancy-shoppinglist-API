from flask import make_response, request, jsonify, Blueprint, abort

from app.models import User, Shoppinglist, Item

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

@shoppinglist_bp.route('/shoppinglists/', methods=['POST', 'GET'])
def shoppinglists_view():
    # Get the access token from header
    auth_header = request.headers.get('Auth')
    access_token = auth_header.split(" ")[1]

    if access_token:
     # decode the token and get the user_id
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            # handle requests after authentication
            if request.method == "POST":
                name = str(request.data.get('name', ''))
                if name:
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
                # get all shoppinglists created by this user
                shoppinglists = Shoppinglist.query.filter_by(owned_by=user_id)
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

@shoppinglist_bp.route('/shoppinglists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def shoppinglist_manipulation(id, **kwargs):
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header.split(" ")[1]

    if access_token:
        # Get the user id in token
        user_id = User.decode_token(access_token)
        #check if token has an integer an doesnt creat an error
        if not isinstance(user_id, str):

            # Get the shoppinglist with the id specified
            shoppinglist = Shoppinglist.query.filter_by(id=id).first()
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
                name = str(request.data.get('name', ''))

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

@shoppinglist_bp.route('/shoppinglists/share/<int:id>', methods=['GET', 'PUT'])
def shoppinglist_share(id, **kwargs):
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header.split(" ")[1]

    if access_token:
        # Get the user id in token
        user_id = User.decode_token(access_token)
        #check if token has an integer an doesnt creat an error
        if not isinstance(user_id, str):

            # Get the shoppinglist with the id specified
            shoppinglist = Shoppinglist.query.filter_by(id=id).first()
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

@shoppinglist_bp.route('/shoppinglists/search', methods=['GET'])
def search():
    """allow the user to querry the database by name"""
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header.split(" ")[1]

    if access_token:
        # Get the user id rin token
        user_id = User.decode_token(access_token)
        #check if token has an integer an doesnt creat an error
        if not isinstance(user_id, str):
            shoppinglist_content = Shoppinglist.query.filter_by(owned_by=user_id).all()
            if not shoppinglist_content:
                return make_response(jsonify({ 'message': 'you dont have any shoppinglists'})), 404

            if not request.args.get('limit'):
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
                        return make_response(jsonify(result=res)), 201
                    except Exception as e:
                        return make_response(jsonify({ 'message': str(e)})), 401

            if not request.args.get('q'):
                list_limit = request.args.get('limit')
                if list_limit:
                    res = []
                    try:
                        results = Shoppinglist.query.filter_by(owned_by=user_id).limit(list_limit)
                        if not results:
                            return make_response(jsonify({ 'message': 'you dont have any shopping lists within that range'})), 401
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
                        return make_response(jsonify(result=res)), 201
                    except Exception as e:
                        return make_response(jsonify({ 'message': str(e)})), 401

            if request.args.get('limit') and request.args.get('q'):
                list_name=str(request.args.get('q'))
                if list_name:
                    result_ids = []
                    res = []
                    try:
                        for slist in shoppinglist_content:
                           if list_name in slist.name:
                                result_ids.append(slist.id)
                        results = Shoppinglist.query.filter(Shoppinglist.id.in_(result_ids)).limit(request.args.get('limit'))
                        if not results:
                            return make_response(jsonify({ 'message': 'you dont have any shopping lists with that name in that range'})), 401
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
                        return make_response(jsonify(result=res)), 201
                    except Exception as e:
                        return make_response(jsonify({ 'message': str(e)})), 401

        else:
            # user is not authenticated send error message
            message = user_id
            response = {
                'message': message
            }
            # reurn an anouthorized message
            return make_response(jsonify(response)), 401

@shoppinglist_bp.route('/shoppinglists/items/<int:id>', methods=['POST', 'GET'])
def items_view(id, **kwargs):
    # Get the access token from header
    auth_header = request.headers.get('Auth')
    access_token = auth_header.split(" ")[1]

    if access_token:
     # decode the token and get the user_id
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            # handle requests after authentication
            shoppinglist = Shoppinglist.query.filter_by(id=id).first()
            if shoppinglist.owned_by == user_id:
                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    price = int(request.data.get('price', ''))
                    quantity = int(request.data.get('quantity', ''))
                    if name:
                        item = Item(name=name, price=price, quantity=quantity, belongs_to=id)
                        item.save()
                        response = jsonify({
                            'id': item.id,
                            'name': item.name,
                            'price': item.price,
                            'quantity': item.quantity,
                            'belongs_to': item.belongs_to
                        })

                        return make_response(response), 201

                else:
                    # get all items created for this shoppinglist
                    item_list = Item.get_all(id)
                    results = []
                    for item in item_list:
                        obj = {
                            'id': item.id,
                            'name': item.name,
                            'price': item.price,
                            'quantity': item.quantity,
                            'belongs_to': item.belongs_to
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
