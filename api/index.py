# app.py
from flask import Flask, request, escape
from flask_cors import CORS 
from flask_session import Session
import os
import secrets

from App.Features.bg_remove import bg_remove_route
from App.Features.add_bg import add_bg_route
from App.Features.apply_filters import apply_filter_route
from App.Features.apply_filters import filter
from App.Features.compress import compress_route
from App.Features.compress import compressing
from App.Features.enhance import image_enhance_route
from App.Features.image_convertor import image_convertor_route

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'api', 'uploads')
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = secrets.token_hex(16)

# Initialize Flask-Session
server_session = Session(app)
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

# CORS(app, resources={r"/api/*": {"origins": "*"}})
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)} from Flask!'


bg_remove_route(app)
add_bg_route(app)
apply_filter_route(app)
filter(app)
compress_route(app)
compressing(app)
image_enhance_route(app)
image_convertor_route(app)



if __name__ == '__main__':
    app.run(debug=True)
