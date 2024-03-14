# app.py
from flask import Flask, session
from flask_cors import CORS
from flask_session import Session
import os
import secrets
from datetime import datetime, timedelta
import glob
import redis

from App.Features.bg_remove import bg_remove_route
from App.Features.add_bg import add_bg_route
from App.Features.apply_filters import apply_filter_route
from App.Features.apply_filters import filter
from App.Features.compress import compress_route
from App.Features.compress import compressing
from App.Features.enhance import image_enhance_route
from App.Features.image_convertor import image_convertor_route
from App.Features.profilepic_maker import profile_maker

app = Flask(__name__,static_url_path='/static', static_folder='static') 
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = secrets.token_hex(16)

# Initialize Flask-Session
server_session = Session(app)
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

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
profile_maker(app)


def delete_old_files(folder_path, max_age_hours=1):
    current_time = datetime.now()
    max_age = timedelta(hours=max_age_hours)

    for file_path in glob.glob(os.path.join(folder_path, '*')):
        file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
        if current_time - file_creation_time > max_age:
            os.remove(file_path)
            print(f"Deleted: {file_path}")


# Run the deletion for both folders
delete_old_files(os.path.join(os.getcwd(), 'static'))
delete_old_files(os.path.join(os.getcwd(), 'uploads'))


if __name__ == '__main__':
    app.run(debug=True, port="5000", host="0.0.0.0")