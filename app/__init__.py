from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from instance.config import app_config
from flask import request, jsonify, abort
from flask_mail import Mail
# initialize sqlalchemy
db = SQLAlchemy()
mail = Mail()

def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    #add extension for handling Cross Origin Resource Sharing (CORS)
    CORS(app)
    mail.init_app(app)
    app.url_map.strict_slashes = False
    #import the blueprints and register them on the app
    from app.views import auth_bp, shoppinglist_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(shoppinglist_bp)

    #documentation
    @app.route('/docs', methods=['GET'])
    def docs():
        return jsonify({'documentation':'https://app.swaggerhub.com/apis/dann254/fancy-shoppinglist-API/1.0.0', 'info':'View in browser'})
    #custom error messages
    @app.errorhandler(404)
    def not_found(error=None):
        message = {
                'status': 404,
                'message': 'Not Found: ' + request.url ,
                'soft_note': 'Dont panic :-)'
        }
        resp = jsonify(message)
        resp.status_code = 404

        return resp
    @app.errorhandler(405)
    def not_allowed(error=None):
        message = {
                'status': 405,
                'message': 'Method not allowed in: ' + request.url ,
                'soft_note': 'Dont panic :-)'
        }
        resp = jsonify(message)
        resp.status_code = 405

        return resp

    @app.errorhandler(500)
    def server_error(error=None):
        message = {
                'status': 500,
                'message': 'OOPS!! something went wrong in: ' + request.url
        }
        resp = jsonify(message)
        resp.status_code = 500

        return resp
    return app
