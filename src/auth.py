from flask import Blueprint, request, jsonify
import validators
from werkzeug.security import generate_password_hash, check_password_hash

from src.constants.http_status_code import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_401_UNAUTHORIZED
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from src.database import db, User
from flasgger import swag_from

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.route("/register", methods=['POST', 'GET'])
@swag_from('./docs/auth/register.yml')
def register():
    if request.method == 'POST':
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']

        if len(password) < 6:
            return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

        if len(username) < 3:
            return jsonify({'error': "User is too short"}), HTTP_400_BAD_REQUEST

        if not username.isalnum() or " " in username:
            return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

        if not validators.email(email):
            return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

        if User.query.filter_by(email=email).first() is not None:
            return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

        if User.query.filter_by(username=username).first() is not None:
            return jsonify({'error': "username is taken"}), HTTP_409_CONFLICT

        pwd_hash = generate_password_hash(password)

        user = User(username=username, password=pwd_hash, email=email)

        # commit to database
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': "User created",
            'user': {
                'username': username, "email": email
            }

        }), HTTP_201_CREATED
    
    return "Register page"

@auth.route("/login", methods=['POST', 'GET'])
@swag_from('./docs/auth/login.yml')
def login():
    if request.method == 'POST':
        email = request.json.get('email', '')
        password = request.json.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user:
            is_pass_correct = check_password_hash(user.password, password)

            if is_pass_correct:
                refresh = create_refresh_token(identity=user.id)
                access = create_access_token(identity=user.id)

                return jsonify({
                    'user': {
                        'refresh': refresh,
                        'access': access,
                        'username': user.username,
                        'email': user.email
                    }

                }), HTTP_200_OK

        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED
    return "User Login Page"

@auth.route("/me", methods=['GET', 'POST'])
@jwt_required() # use jwt_required for route protection purpose
def me():
    if request.method == 'GET':
        user_id = get_jwt_identity() # get user if by using jwt identity
        user = User.query.filter_by(id=user_id).first()
        return jsonify({
            'username': user.username,
            'email': user.email
        }), HTTP_200_OK

@auth.route('/token/refresh', methods=['GET', 'POST'])
@jwt_required(refresh=True)
def refresh_users_token():
    if request.method == 'POST':
        identity = get_jwt_identity()
        access = create_access_token(identity=identity)

        return jsonify({
            'access': access
        }), HTTP_200_OK

    return "Hello"
    
        