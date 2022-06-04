# Project setup

    install virtualenv: pip install virtualenv

    python -m virtualenv venv (create virtual environment)

    source venv/bin/activate (activate environment)

    pip install flask (install flask framework)

    touch app.py (create base file)

### app.py

    from flask import Flask, render_template, jsonify

    app = Flask(__name__)

    @app.get("/")
    def home():
        return render_template("index.html")

    # response a json format
    @app.get("/user")
    def userInfo():
        return jsonify({
            "id": "1",
            "username": "Teng Kimhan",
            "email": "tengkimhan@gmail.com"
            })

    if __name__ == "__main__":
        app.run(debug=True)

## Setup Environment Variable

We need to setup some environment for our project

FLASK_APP = app.py (app.py is our base file and FLASK_APP tell flask to run with this file)

FLASK_ENV = development (since we are in development stage we put FLASK_ENV = development)

## Run Flask application

flask run

# Application Factory Function and Project Structure and Flaskenv etc

# Setup Database

## using SQLAlchemy

## Install SQLAlchemy: pip install flask-sqlalchemy
