from flask import make_response, request, jsonify, Blueprint, abort

from app.models import User, Shoppinglist, Item
import re

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
            username = username.lower()
            if not re.match(r"^[a-z0-9_]*$", username):
                response = {
                    'message': 'please enter a valid username'
                }
                return make_response(jsonify(response)), 401
            if len(password)<6:
                response = {
                    'message': 'password must be at least 6 characters long'
                }
                return make_response(jsonify(response)), 401
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
                    if not re.match(r"^[a-z0-9_ -]*$", name):
                        response = {
                            'message': 'please enter a valid shoppinglist name'
                        }
                        return make_response(jsonify(response)), 401
                    existing_list=Shoppinglist.query.filter_by(owned_by=user_id).all()
                    for i in existing_list:
                        if name == i.name:
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
                if not request.args.get('limit') and not request.args.get('q'):
                    # get all shoppinglists created by this user
                    shoppinglists = Shoppinglist.query.filter_by(owned_by=user_id).order_by(Shoppinglist.id)
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
                    shoppinglists = Shoppinglist.query.filter_by(owned_by=user_id).order_by(Shoppinglist.id)
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
    access_token = auth_header.split(" ")[1]

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

            if request.method == "DELETE":
                # delete the shoppinglist
                shoppinglist.delete()
                return {
                    "message": "shoppinglist {} deleted".format(shoppinglist.id)
                }, 200

            elif request.method == 'PUT':
                # obtain a name from data
                name = str(request.data.get('name', ''))
                existing_list=Shoppinglist.query.filter_by(owned_by=user_id).all()
                for i in existing_list:
                    if name == i.name:
                        response = {
                            'message': 'NOT UPDATED: shoppinglist with that name already exists'
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
    access_token = auth_header.split(" ")[1]

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
    access_token = auth_header.split(" ")[1]

    if access_token:
     # decode the token and get the user_id
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            # handle requests after authentication
            shoppinglist = Shoppinglist.query.filter_by(id=list_id).first()
            if shoppinglist.owned_by == user_id:
                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    price = int(request.data.get('price', ''))
                    quantity = int(request.data.get('quantity', ''))
                    if name:
                        if not re.match(r"^[a-z0-9_ -]*$", name):
                            response = {
                                'message': 'please enter a valid item name'
                            }
                            return make_response(jsonify(response)), 401
                        existing_item=Item.query.filter_by(belongs_to=list_id).all()
                        for i in existing_item:
                            if name == i.name:
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
                            'belongs_to': item.belongs_to
                        })

                        return make_response(response), 201

                else:
                    # get all items created for this shoppinglist
                    item_list = Item.get_all(list_id)
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

@shoppinglist_bp.route('/shoppinglists/<int:list_id>/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
def item_manipulation(list_id, item_id, **kwargs):
    # get the access token from  header
    auth_header = request.headers.get('Auth')
    access_token = auth_header.split(" ")[1]

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
                name = str(request.data.get('name', '')) if str(request.data.get('name', '')) else item.name
                price = str(request.data.get('price', '')) if str(request.data.get('price', '')) else item.price
                quantity = str(request.data.get('quantity', '')) if str(request.data.get('quantity', '')) else item.quantity

                existing_item=Item.query.filter_by(belongs_to=list_id).all()
                for i in existing_item:
                    if name == i.name and item_id != i.id:
                        response = {
                            'message': 'NOT UPDATED: item with that name already exists'
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
                    'belongs_to': item.belongs_to
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
                    'belongs_to': item.belongs_to
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
