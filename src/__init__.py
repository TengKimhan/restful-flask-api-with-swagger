# __init__ file has two duties. One is to tell python that the folder which it is inside is a package. Second, it will contain application factory.
# application factory means instead of declaring Flask instance in specific file we declare it in a function to avoid some issues.

import os

from flask import Flask, render_template, jsonify, redirect, url_for
from src.auth import auth
from src.bookmarks import bookmark
from src.database import Bookmark, db
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config
from src.constants.http_status_code import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),
        SWAGGER={
            'title': "Bookmark API",
            'uiversion': 3
        }
    )
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    @app.get("/home")
    def home():
        return render_template('index.html')

    db.app=app
    db.init_app(app)
    
    # initialize JWTManager
    JWTManager(app)

    # register a blueprint
    app.register_blueprint(auth)
    app.register_blueprint(bookmark)

    # initialize Swagger
    Swagger(app, config=swagger_config, template=template)

    # handling error
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR

    return app

    



