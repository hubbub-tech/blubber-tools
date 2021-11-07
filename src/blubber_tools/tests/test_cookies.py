import os
import functools
from flask import Flask, Blueprint, request, make_response, jsonify
from flask_cors import CORS

# Testing constants
COOKIE_NAME = "myCookie"
COOKIE_VALUE = "HelloWorld"

class Config:
    SECRET_KEY = os.environ['SECRET_KEY']

def create_app():
    config_object = Config()
    app = Flask(__name__)

    # Cross-Origin Config
    CORS(app, origins=[os.environ["CORS_ALLOW_ORIGIN"]])

    app.register_blueprint(bp)
    return app

def auth_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        auth_cookie = request.cookies.get(COOKIE_NAME)
        if auth_cookie == COOKIE_VALUE:
            print("Cookie is authenticated; you're ready to rumble!")
            return view(**kwargs)
        else:
            print("Cookie is NOT authenticated. Bye, Felicia.")
            response = make_response({"serverTip": "Give me the GOOD cookie..."}, 405)
            return response
    return wrapped_view

bp = Blueprint('test', __name__)

@bp.get('/test/get')
def get_data():
    response = make_response({"testData": "Do you believe in life after love?"}, 200)
    response.set_cookie("myCookie", value="HelloWorld")
    response.content_type = 'application/json'
    return response

@bp.post('/test/post')
@auth_required
def post_data():
    data = request.json.get("data")
    print("Client Data: ", data)
    response = make_response({"testData": "We got your response--thanks for that."}, 200)
    return response

@bp.get('/test/protected')
@auth_required
def protected_data():
    response = make_response({"testData": "I really don't think I'm strong enough..."}, 200)
    response.content_type = 'application/json'
    return response

app = create_app()

if __name__ == "__main__":
    app.run()
