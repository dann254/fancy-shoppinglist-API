from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

from instance.config import app_config
from flask import request, jsonify, abort, make_response
# initialize sqlalchemy
db = SQLAlchemy()

def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    #import the blueprints and register them on the app
    from app.views import auth_bp, shoppinglist_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(shoppinglist_bp)


    return app
