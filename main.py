# app.py
from flask import Flask, session
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

app = Flask(__name__,static_url_path='/static', static_folder='static') 
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')


# Set the secret key for the Flask app
app.config['SECRET_KEY'] = secrets.token_hex(32)

# Set the session type to filesystem
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, 'session_files')

# Ensure the directory for storing sessions exists
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# Initialize Flask-Session
server_session = Session(app)
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

# CORS(app, resources={r"/api/*": {"origins": "*"}})

CORS(app, resources={r"/static/*": {"origins": "*"}}, supports_credentials=True)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/test-image')
def test_image():
    return '<img width="400" src="https://images.pexels.com/photos/11035465/pexels-photo-11035465.jpeg">'

bg_remove_route(app)
add_bg_route(app)
apply_filter_route(app)
filter(app)
compress_route(app)
compressing(app)
image_enhance_route(app)
image_convertor_route(app)



if __name__ == '__main__':
    app.run(debug=True, port="5000", host="0.0.0.0")